import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature

from pyproj import Geod


# ============================================================
# 1. ERA5 laden
# ============================================================

era5_file = (
    r"C:\Users\janni\Desktop\Spitzbergen\Slides"
    r"\Exercise\Exercise1\era5_constants-2.nc"
)

era5 = xr.open_dataset(era5_file)


# ============================================================
# 2. ERA5 Bereich
# ============================================================

era5_area = era5.sel(
    longitude=slice(14, 17),
    latitude=slice(78.5, 78)
)

# ERA5 Geopotential -> Höhe [m]
era5_terrain = (
    era5_area["z"] / 9.80665
).squeeze()


# ============================================================
# 3. AROME laden
# ============================================================

arome_file = (
    "https://thredds.met.no/thredds/dodsC/"
    "aromearcticlatest/latest/"
    "arome_arctic_lagged_6_h_latest_2_5km_latest.nc"
)

arome = xr.open_dataset(arome_file)

# Erstes Ensemblemitglied
arome = arome.sel(
    ensemble_member=0
)


# ============================================================
# 4. AROME auf Longyearbyen / Adventdalen beschränken
# ============================================================

lat = arome["latitude"]
lon = arome["longitude"]

mask = (
    (lat >= 78.0) &
    (lat <= 78.5) &
    (lon >= 14.0) &
    (lon <= 17.0)
)

y_idx, x_idx = np.where(mask)

x_min = x_idx.min()
x_max = x_idx.max()

y_min = y_idx.min()
y_max = y_idx.max()

arome_area = arome.isel(
    x=slice(x_min, x_max + 1),
    y=slice(y_min, y_max + 1)
)

arome_lon = arome_area["longitude"].values
arome_lat = arome_area["latitude"].values


# ============================================================
# 5. Cross Section durch Adventdalen
# ============================================================

# Start ungefähr bei Longyearbyen
start_lon = 15.45
start_lat = 78.245

# Richtung Adventdalen
end_lon = 16.20
end_lat = 78.20

n_points = 150

cross_lon = np.linspace(
    start_lon,
    end_lon,
    n_points
)

cross_lat = np.linspace(
    start_lat,
    end_lat,
    n_points
)


# ============================================================
# 6. Entfernung entlang des Cross Sections
# ============================================================

geod = Geod(
    ellps="WGS84"
)

distance = np.zeros(
    n_points
)

for i in range(1, n_points):

    _, _, dist = geod.inv(
        cross_lon[i - 1],
        cross_lat[i - 1],
        cross_lon[i],
        cross_lat[i]
    )

    distance[i] = (
        distance[i - 1]
        + dist / 1000
    )


# ============================================================
# 7. ERA5 Terrainhöhe entlang des Cross Sections
# ============================================================

cross_height = []

for lon_point, lat_point in zip(
    cross_lon,
    cross_lat
):

    terrain_point = era5_terrain.sel(
        longitude=lon_point,
        latitude=lat_point,
        method="nearest"
    )

    cross_height.append(
        float(terrain_point.values)
    )

cross_height = np.array(
    cross_height
)


# ============================================================
# 8. AROME-Gitterpunkte nahe der Cross Section
# ============================================================

arome_lon_flat = arome_lon.ravel()
arome_lat_flat = arome_lat.ravel()


# Wir suchen AROME-Punkte,
# die tatsächlich nahe an der Schnittlinie liegen.

arome_cross_lon = []
arome_cross_lat = []
arome_cross_distance = []
arome_cross_height = []


# maximaler Abstand zur Cross Section
# in Grad
max_distance = 0.015


for lon_point, lat_point in zip(
    arome_lon_flat,
    arome_lat_flat
):

    # Abstand zu allen Punkten der Cross Section
    d = np.sqrt(
        (cross_lon - lon_point) ** 2
        +
        (cross_lat - lat_point) ** 2
    )

    idx = np.argmin(d)

    # Nur Punkte wirklich nahe an der Linie behalten
    if d[idx] < max_distance:

        ar_dist = distance[idx]

        # ERA5 Höhe an dieser Position
        ar_height = cross_height[idx]

        arome_cross_lon.append(
            lon_point
        )

        arome_cross_lat.append(
            lat_point
        )

        arome_cross_distance.append(
            ar_dist
        )

        arome_cross_height.append(
            ar_height
        )


arome_cross_lon = np.array(
    arome_cross_lon
)

arome_cross_lat = np.array(
    arome_cross_lat
)

arome_cross_distance = np.array(
    arorme_cross_distance
) if False else np.array(
    arome_cross_distance
)

arome_cross_height = np.array(
    arome_cross_height
)


# ============================================================
# 9. FIGURE
# ============================================================

fig = plt.figure(
    figsize=(15, 7)
)


# ============================================================
# LINKES PANEL: KARTE
# ============================================================

ax_map = fig.add_subplot(
    1,
    2,
    1,
    projection=ccrs.PlateCarree()
)

ax_map.set_extent(
    [14.0, 17.0, 78.0, 78.5],
    crs=ccrs.PlateCarree()
)


# ------------------------------------------------------------
# Land / Meer
# ------------------------------------------------------------

# Bewusst 50m statt 10m:
# ausreichend für Übersicht und deutlich leichter

ax_map.add_feature(
    cfeature.OCEAN,
    facecolor="lightblue",
    zorder=0
)

ax_map.add_feature(
    cfeature.LAND,
    facecolor="lightgray",
    zorder=1
)

ax_map.add_feature(
    cfeature.COASTLINE.with_scale("50m"),
    linewidth=0.8,
    zorder=3
)


# ------------------------------------------------------------
# AROME Grid
# ------------------------------------------------------------

ax_map.scatter(
    arome_lon,
    arome_lat,
    color="blue",
    s=4,
    alpha=0.6,
    transform=ccrs.PlateCarree(),
    label="AROME grid",
    zorder=5
)


# ------------------------------------------------------------
# ERA5 Grid
# ------------------------------------------------------------

era5_lon_grid, era5_lat_grid = np.meshgrid(
    era5_area.longitude.values,
    era5_area.latitude.values
)

ax_map.scatter(
    era5_lon_grid,
    era5_lat_grid,
    color="red",
    marker="s",
    s=30,
    transform=ccrs.PlateCarree(),
    label="ERA5 grid",
    zorder=6
)


# ------------------------------------------------------------
# Cross Section Linie
# ------------------------------------------------------------

ax_map.plot(
    cross_lon,
    cross_lat,
    color="black",
    linewidth=3,
    transform=ccrs.PlateCarree(),
    label="Cross section",
    zorder=10
)


# ------------------------------------------------------------
# Start / Ende des Cross Sections
# ------------------------------------------------------------

ax_map.scatter(
    start_lon,
    start_lat,
    color="green",
    edgecolor="black",
    s=80,
    transform=ccrs.PlateCarree(),
    zorder=11
)

ax_map.scatter(
    end_lon,
    end_lat,
    color="orange",
    edgecolor="black",
    s=80,
    transform=ccrs.PlateCarree(),
    zorder=11
)


# ------------------------------------------------------------
# Longyearbyen
# ------------------------------------------------------------

longyearbyen_lon = 15.465
longyearbyen_lat = 78.246

ax_map.scatter(
    longyearbyen_lon,
    longyearbyen_lat,
    color="yellow",
    edgecolor="black",
    s=150,
    transform=ccrs.PlateCarree(),
    zorder=15,
    label="Longyearbyen"
)

ax_map.text(
    longyearbyen_lon + 0.04,
    longyearbyen_lat + 0.015,
    "Longyearbyen",
    transform=ccrs.PlateCarree(),
    fontsize=10,
    zorder=15
)


# ------------------------------------------------------------
# Gridlines
# ------------------------------------------------------------

gl = ax_map.gridlines(
    draw_labels=True,
    linewidth=0.5,
    color="gray",
    linestyle="--"
)

gl.top_labels = False
gl.right_labels = False


ax_map.set_title(
    "Adventdalen – Cross Section Location"
)

ax_map.legend(
    loc="lower left",
    fontsize=8
)


# ============================================================
# RECHTES PANEL: CROSS SECTION
# ============================================================

ax_cross = fig.add_subplot(
    1,
    2,
    2
)


# ------------------------------------------------------------
# ERA5 Terrain
# ------------------------------------------------------------

ax_cross.plot(
    distance,
    cross_height,
    color="black",
    linewidth=2,
    label="ERA5 terrain",
    zorder=2
)


# ------------------------------------------------------------
# ERA5 Gridpunkte
# ------------------------------------------------------------

ax_cross.scatter(
    distance,
    cross_height,
    color="red",
    marker="s",
    s=30,
    label="ERA5 grid points",
    zorder=4
)


# ------------------------------------------------------------
# AROME Gridpunkte
# ------------------------------------------------------------

ax_cross.scatter(
    arome_cross_distance,
    arome_cross_height,
    color="blue",
    s=20,
    alpha=0.8,
    label="AROME grid points",
    zorder=5
)


# ------------------------------------------------------------
# Start / Ende markieren
# ------------------------------------------------------------

ax_cross.scatter(
    distance[0],
    cross_height[0],
    color="green",
    edgecolor="black",
    s=80,
    zorder=10
)

ax_cross.scatter(
    distance[-1],
    cross_height[-1],
    color="orange",
    edgecolor="black",
    s=80,
    zorder=10
)


# ------------------------------------------------------------
# Achsen
# ------------------------------------------------------------

ax_cross.set_xlabel(
    "Distance along Adventdalen [km]"
)

ax_cross.set_ylabel(
    "Elevation [m]"
)

ax_cross.set_title(
    "Terrain Cross Section"
)

ax_cross.grid(
    linestyle="--",
    alpha=0.4
)

ax_cross.legend()


# ============================================================
# 10. Layout
# ============================================================

plt.tight_layout()

plt.show()
