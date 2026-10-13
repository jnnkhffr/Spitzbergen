"""
ECMWF IFS wind profile for Longyearbyen.

Downloads:
    - 00 UTC forecast run
    - +12 h forecast step
    - u and v wind components
    - pressure levels

Then plots the vertical wind profile.
"""

import logging
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from ecmwf.opendata import Client


# ============================================================================
# CONFIGURATION
# ============================================================================

OUTPUT_DIR = Path(
    r"C:/Users/janni/Desktop/ECMWF"
)

# Longyearbyen
LAT = 78.2233
LON = 15.6469

LOCATION_NAME = "Longyearbyen"

# ECMWF
MODEL = "ifs"

# Forecast date
# date=0 means the current available forecast date.
FORECAST_DATE = datetime.now().date()

# Exactly what we want:
FORECAST_RUN = 0       # 00 UTC
FORECAST_STEP = 12     # +12 hours

# Pressure levels in hPa
PRESSURE_LEVELS = [
    1000,
    925,
    850,
    700,
    600,
    500,
    400,
    300,
    250,
    200,
    150,
    100,
    50,
]

# Only wind components
PARAMETERS = [
    "u",
    "v",
]


# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# ============================================================================
# DOWNLOAD
# ============================================================================

def download_wind_data() -> Path:
    """
    Download ECMWF IFS u/v wind data for Longyearbyen.

    00 UTC run
    +12 h forecast
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    grib_file = (
        OUTPUT_DIR
        / "longyearbyen_wind_00UTC_plus12h.grib2"
    )

    logger.info(
        "=================================================="
    )

    logger.info(
        "Downloading ECMWF IFS wind data"
    )

    logger.info(
        "Location: %.4f N, %.4f E",
        LAT,
        LON,
    )

    logger.info(
        "Forecast date: %s",
        FORECAST_DATE.strftime("%d.%m.%Y"),
    )

    logger.info(
        "Run: %02d UTC",
        FORECAST_RUN,
    )

    logger.info(
        "Forecast step: +%02d h",
        FORECAST_STEP,
    )

    logger.info(
        "=================================================="
    )

    client = Client(
        source="ecmwf",
        beta=False,
    )

    client.retrieve(
        date=0,
        time=FORECAST_RUN,
        step=[FORECAST_STEP],
        stream="oper",
        type="fc",
        levtype="pl",
        levelist=PRESSURE_LEVELS,
        model=MODEL,
        param=PARAMETERS,
        target=str(grib_file),
    )

    logger.info(
        "Download complete: %s",
        grib_file,
    )

    return grib_file


# ============================================================================
# READ DATA
# ============================================================================

def read_wind_data(
    grib_file: Path,
) -> xr.Dataset:
    """
    Read GRIB file and select the nearest ECMWF grid point
    to Longyearbyen.
    """

    logger.info(
        "Reading GRIB file..."
    )

    ds = xr.open_dataset(
        grib_file,
        engine="cfgrib",
    )

    logger.info(
        "Original dataset:"
    )

    logger.info(
        "\n%s",
        ds,
    )

    # ------------------------------------------------------------
    # Select nearest ECMWF grid point
    # ------------------------------------------------------------

    ds = ds.sel(
        latitude=LAT,
        longitude=LON,
        method="nearest",
    )

    logger.info(
        "Selected ECMWF grid point:"
    )

    logger.info(
        "Latitude: %.3f",
        float(ds.latitude),
    )

    logger.info(
        "Longitude: %.3f",
        float(ds.longitude),
    )

    return ds


# ============================================================================
# CALCULATE WIND SPEED
# ============================================================================

def calculate_wind_speed(
    ds: xr.Dataset,
) -> xr.DataArray:
    """
    Calculate wind speed from u and v.

    wind_speed = sqrt(u² + v²)
    """

    u = ds["u"]
    v = ds["v"]

    wind_speed = np.sqrt(
        u**2 + v**2
    )

    wind_speed.name = "wind_speed"

    wind_speed.attrs["units"] = "m/s"

    return wind_speed


# ============================================================================
# PLOT
# ============================================================================

def plot_wind_profile(
    ds: xr.Dataset,
) -> None:
    """
    Plot the vertical wind profile against pressure.
    """

    wind_speed = calculate_wind_speed(
        ds
    )

    # ------------------------------------------------------------
    # Remove step dimension if present
    # ------------------------------------------------------------

    if "step" in wind_speed.dims:
        wind_speed = wind_speed.squeeze(
            "step"
        )

    pressure = ds[
        "isobaricInhPa"
    ]

    # ------------------------------------------------------------
    # Convert to NumPy arrays
    # ------------------------------------------------------------

    wind_speed_values = np.asarray(
        wind_speed.values,
        dtype=float,
    )

    pressure_values = np.asarray(
        pressure.values,
        dtype=float,
    )

    # ------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(9, 9)
    )

    ax.plot(
        wind_speed_values,
        pressure_values,
        marker="o",
        linewidth=2,
        color="tab:blue",
        label="ECMWF IFS",
    )

    # ------------------------------------------------------------
    # Pressure decreases upwards
    # ------------------------------------------------------------

    ax.invert_yaxis()

    # ------------------------------------------------------------
    # Axis labels
    # ------------------------------------------------------------

    ax.set_xlabel(
        "Windgeschwindigkeit [m/s]"
    )

    ax.set_ylabel(
        "Druck [hPa]"
    )

    # ------------------------------------------------------------
    # Title with forecast date
    # ------------------------------------------------------------

    ax.set_title(
        f"ECMWF IFS – {LOCATION_NAME}\n"
        f"Forecast: {FORECAST_DATE.strftime('%d.%m.%Y')} | "
        f"{FORECAST_RUN:02d} UTC Lauf | "
        f"+{FORECAST_STEP:02d} h"
    )

    # ------------------------------------------------------------
    # Grid
    # ------------------------------------------------------------

    ax.grid(
        True,
        alpha=0.3,
    )

    # ------------------------------------------------------------
    # Legend
    # ------------------------------------------------------------

    ax.legend(
        loc="best"
    )

    # ------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------

    plt.tight_layout()

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    output_file = (
        OUTPUT_DIR
        / "longyearbyen_wind_profile.png"
    )

    plt.savefig(
        output_file,
        dpi=150,
        bbox_inches="tight",
    )

    plt.show()

    logger.info(
        "Plot saved to: %s",
        output_file,
    )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    """
    Download ECMWF forecast and create
    the vertical wind profile.
    """

    logger.info(
        "=================================================="
    )

    logger.info(
        "Longyearbyen vertical wind profile"
    )

    logger.info(
        "=================================================="
    )

    # ------------------------------------------------------------
    # 1. Download
    # ------------------------------------------------------------

    grib_file = download_wind_data()

    # ------------------------------------------------------------
    # 2. Read GRIB
    # ------------------------------------------------------------

    ds = read_wind_data(
        grib_file
    )

    # ------------------------------------------------------------
    # 3. Calculate and plot
    # ------------------------------------------------------------

    plot_wind_profile(
        ds
    )

    # ------------------------------------------------------------
    # 4. Close dataset
    # ------------------------------------------------------------

    ds.close()

    logger.info(
        "Finished."
    )


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
