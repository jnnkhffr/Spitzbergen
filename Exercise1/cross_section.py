import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

import cartopy.crs as ccrs

from pyproj import Geod, Transformer

import requests
from io import BytesIO
from PIL import Image


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

# Geopotential -> Terrainhöhe [m]
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

arome = xr.open_dataset(
    arome_file
)

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

arome_lon = arome_area[
    "longitude"
].values

arome_lat = arome_area[
    "latitude"
].values


# ============================================================
# 5. Cross Section durch Adventdalen
# ============================================================

# Start ungefähr bei Longyearbyen
start_lon = 15.45
start_lat = 78.245

# Ende weiter in Richtung Adventdalen
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
# 6. Entfernung entlang der Cross Section
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
        + dist / 1000.0
    )


# ============================================================
# 7. ERA5 Terrainhöhe entlang der Cross Section
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

arome_lon_flat = (
    arome_lon.ravel()
)

arome_lat_flat = (
    arome_lat.ravel()
)

max_distance = 0.015

arome_cross_distance = []
arome_cross_height = []


for lon_point, lat_point in zip(
    arome_lon_flat,
    arome_lat_flat
):

    d = np.sqrt(
        (cross_lon - lon_point) ** 2
        +
        (cross_lat - lat_point) ** 2
    )

    idx = np.argmin(d)

    if d[idx] < max_distance:

        arome_cross_distance.append(
            distance[idx]
        )

        # Aktuell verwenden wir ERA5-Terrainhöhe
        # für die Darstellung der AROME-Punkte.
        arome_cross_height.append(
            cross_height[idx]
        )


arome_cross_distance = np.array(
    arome_cross_distance
)

arome_cross_height = np.array(
    arome_cross_height
)


# ============================================================
# 9. LONGYEARBYEN KOORDINATEN
# ============================================================

longyearbyen_lon = 15.465
longyearbyen_lat = 78.246


# ============================================================
# 10. NÄCHSTEN AROME-GITTERPUNKT FINDEN
# ============================================================

distance_to_longyearbyen = (
    (arome_lon - longyearbyen_lon) ** 2
    +
    (arome_lat - longyearbyen_lat) ** 2
)

iy, ix = np.unravel_index(
    np.argmin(
        distance_to_longyearbyen
    ),
    distance_to_longyearbyen.shape
)


# Tatsächliche Koordinaten des verwendeten
# AROME-Gitterpunkts

profile_lon = arome_lon[iy, ix]
profile_lat = arome_lat[iy, ix]


print()
print("========================================")
print("AROME GRID POINT FOR WIND PROFILE")
print("========================================")

print(
    f"Requested location: "
    f"{longyearbyen_lon:.3f}°E, "
    f"{longyearbyen_lat:.3f}°N"
)

print(
    f"AROME grid point: "
    f"{profile_lon:.3f}°E, "
    f"{profile_lat:.3f}°N"
)


# ============================================================
# 11. AROME WINDDATEN
# ============================================================

# 10-m Wind
u10 = arome_area[
    "x_wind_10m"
]

v10 = arome_area[
    "y_wind_10m"
]


# Wind auf Druckleveln
u_pl = arome_area[
    "x_wind_pl"
]

v_pl = arome_area[
    "y_wind_pl"
]


# Verfügbare Drucklevel
pressure = arome["pressure"].values

print()
print(
    "Available pressure levels:",
    pressure
)


# ============================================================
# 12. WIND AM AROME-PUNKT EXTRAHIEREN
# ============================================================

u10_point = u10.isel(
    y=iy,
    x=ix
)

v10_point = v10.isel(
    y=iy,
    x=ix
)


u_pl_point = u_pl.isel(
    y=iy,
    x=ix
)

v_pl_point = v_pl.isel(
    y=iy,
    x=ix
)


# ============================================================
# 13. ZEITPUNKT
# ============================================================

# Erster verfügbarer Zeitpunkt
time_index = 0

selected_time = arome["time"].isel(
    time=time_index
).values

print()
print(
    "Time used for wind profile:",
    selected_time
)


# ============================================================
# 14. WINDKOMPONENTEN
# ============================================================

# 10 m
u10_value = float(
    u10_point
    .isel(time=time_index)
    .values
)

v10_value = float(
    v10_point
    .isel(time=time_index)
    .values
)


# Drucklevel
u_pl_values = (
    u_pl_point
    .isel(time=time_index)
    .values
)

v_pl_values = (
    v_pl_point
    .isel(time=time_index)
    .values
)


# ============================================================
# 15. WINDSPEED BERECHNEN
# ============================================================

wind_speed_10m = np.sqrt(
    u10_value ** 2
    +
    v10_value ** 2
)


wind_speed_pl = np.sqrt(
    u_pl_values ** 2
    +
    v_pl_values ** 2
)


# ============================================================
# 16. WINDWERTE AUSGEBEN
# ============================================================

print()
print("========================================")
print("MODELED WIND PROFILE")
print("========================================")

print(
    f"10 m: "
    f"{wind_speed_10m:.2f} m/s"
)

for i, p in enumerate(pressure):

    print(
        f"{p:.0f} hPa: "
        f"{wind_speed_pl[i]:.2f} m/s"
    )


# ============================================================
# 17. WINDPROFIL ZUSAMMENSTELLEN
# ============================================================

# Wir haben:
#
# 10 m
# 925 hPa
# 850 hPa
#
# 1000 hPa wird nur als untere Position
# für den 10-m-Wert verwendet.
#
# Der 10-m-Wert ist natürlich KEIN 1000-hPa-Wert.

profile_pressure = np.array([
    1000,
    925,
    850
])

profile_wind = np.array([
    wind_speed_10m,
    wind_speed_pl[
        np.where(pressure == 925)[0][0]
    ],
    wind_speed_pl[
        np.where(pressure == 850)[0][0]
    ]
])


# ============================================================
# 18. NPI HILLSHADE
# ============================================================

map_lon_min = 14.0
map_lon_max = 17.0

map_lat_min = 78.0
map_lat_max = 78.5


# ------------------------------------------------------------
# WGS84 -> UTM 33N
# ------------------------------------------------------------

transformer_to_utm = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:25833",
    always_xy=True
)


x_min_map, y_min_map = transformer_to_utm.transform(
    map_lon_min,
    map_lat_min
)

x_max_map, y_max_map = transformer_to_utm.transform(
    map_lon_max,
    map_lat_max
)


# ============================================================
# 19. NPI TERRAIN HILLSHADE
# ============================================================

hillshade_url = (
    "https://geodata.npolar.no/arcgis/rest/services/"
    "Basisdata_Intern/"
    "NP_TerrengFjellskygge_Svalbard_WMTS_25833/"
    "MapServer/export"
)


params = {
    "bbox": (
        f"{x_min_map},"
        f"{y_min_map},"
        f"{x_max_map},"
        f"{y_max_map}"
    ),

    "bboxSR": "25833",

    "imageSR": "25833",

    "size": "1200,900",

    "format": "png",

    "transparent": "false",

    "f": "image"
}


response = requests.get(
    hillshade_url,
    params=params,
    timeout=30
)

response.raise_for_status()


hillshade_image = Image.open(
    BytesIO(response.content)
)


# ============================================================
# 20. FIGURE
# ============================================================

fig = plt.figure(
    figsize=(19, 7)
)


# ============================================================
# PANEL 1
# KARTE
# ============================================================

ax_map = fig.add_subplot(
    1,
    3,
    1,
    projection=ccrs.PlateCarree()
)


ax_map.set_extent(
    [
        map_lon_min,
        map_lon_max,
        map_lat_min,
        map_lat_max
    ],
    crs=ccrs.PlateCarree()
)


# ------------------------------------------------------------
# NPI Hillshade
# ------------------------------------------------------------

ax_map.imshow(
    hillshade_image,

    origin="upper",

    extent=[
        map_lon_min,
        map_lon_max,
        map_lat_min,
        map_lat_max
    ],

    transform=ccrs.PlateCarree(),

    zorder=0
)


# ============================================================
# AROME GRID
# ============================================================

ax_map.scatter(
    arome_lon,
    arome_lat,

    color="cyan",

    s=4,

    alpha=0.6,

    transform=ccrs.PlateCarree(),

    label="AROME grid",

    zorder=5
)


# ============================================================
# ERA5 GRID
# ============================================================

era5_lon_grid, era5_lat_grid = np.meshgrid(
    era5_area.longitude.values,
    era5_area.latitude.values
)

ax_map.scatter(
    era5_lon_grid,
    era5_lat_grid,

    color="red",

    marker="s",

    s=35,

    edgecolor="white",

    linewidth=0.3,

    transform=ccrs.PlateCarree(),

    label="ERA5 grid",

    zorder=6
)


# ============================================================
# CROSS SECTION
# ============================================================

ax_map.plot(
    cross_lon,
    cross_lat,

    color="black",

    linewidth=3,

    transform=ccrs.PlateCarree(),

    label="Cross section",

    zorder=10
)


# ============================================================
# START
# ============================================================

ax_map.scatter(
    start_lon,
    start_lat,

    color="lime",

    edgecolor="black",

    s=100,

    transform=ccrs.PlateCarree(),

    zorder=11
)


# ============================================================
# END
# ============================================================

ax_map.scatter(
    end_lon,
    end_lat,

    color="orange",

    edgecolor="black",

    s=100,

    transform=ccrs.PlateCarree(),

    zorder=11
)


# ============================================================
# LONGYEARBYEN
# ============================================================

ax_map.scatter(
    longyearbyen_lon,
    longyearbyen_lat,

    color="yellow",

    edgecolor="black",

    s=160,

    transform=ccrs.PlateCarree(),

    label="Longyearbyen",

    zorder=15
)


ax_map.text(
    longyearbyen_lon + 0.04,
    longyearbyen_lat + 0.015,

    "Longyearbyen",

    transform=ccrs.PlateCarree(),

    fontsize=10,

    fontweight="bold",

    zorder=15
)


# ============================================================
# USED AROME WIND PROFILE POINT
# ============================================================

ax_map.scatter(
    profile_lon,
    profile_lat,

    color="magenta",

    edgecolor="black",

    marker="*",

    s=180,

    transform=ccrs.PlateCarree(),

    label="Wind profile grid point",

    zorder=20
)


# ============================================================
# GRIDLINES
# ============================================================

gl = ax_map.gridlines(
    draw_labels=True,

    linewidth=0.5,

    color="white",

    linestyle="--",

    alpha=0.7
)

gl.top_labels = False
gl.right_labels = False


ax_map.set_title(
    "Adventdalen – Model Grid and Cross Section"
)


ax_map.legend(
    loc="lower left",
    fontsize=7
)


# ============================================================
# PANEL 2
# TERRAIN CROSS SECTION
# ============================================================

ax_cross = fig.add_subplot(
    1,
    3,
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
# ERA5 Grid Points
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
# AROME Grid Points
# ------------------------------------------------------------

ax_cross.scatter(
    arome_cross_distance,
    arome_cross_height,

    color="blue",

    s=30,

    alpha=0.8,

    label="AROME grid points",

    zorder=5
)


# ------------------------------------------------------------
# START
# ------------------------------------------------------------

ax_cross.scatter(
    distance[0],
    cross_height[0],

    color="lime",

    edgecolor="black",

    s=100,

    zorder=10
)


# ------------------------------------------------------------
# END
# ------------------------------------------------------------

ax_cross.scatter(
    distance[-1],
    cross_height[-1],

    color="orange",

    edgecolor="black",

    s=100,

    zorder=10
)


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
# PANEL 3
# MODELIERTES WINDPROFIL
# ============================================================

ax_wind = fig.add_subplot(
    1,
    3,
    3
)


# ------------------------------------------------------------
# Drei Punkte mit einer Linie verbinden
# ------------------------------------------------------------

ax_wind.plot(
    profile_wind,
    profile_pressure,

    color="tab:blue",

    marker="o",

    markersize=8,

    linewidth=2,

    label="AROME"
)


# Druckachse:
# 850 hPa oben
# 1000 hPa unten

ax_wind.invert_yaxis()


# ------------------------------------------------------------
# Achsen
# ------------------------------------------------------------

ax_wind.set_xlabel(
    "Wind speed [m/s]"
)

ax_wind.set_ylabel(
    "Pressure [hPa]"
)


ax_wind.set_title(
    "Modeled Wind Profile\n"
    f"AROME: "
    f"{profile_lon:.3f}°E, "
    f"{profile_lat:.3f}°N"
)


# ------------------------------------------------------------
# Gitter
# ------------------------------------------------------------

ax_wind.grid(
    linestyle="--",
    alpha=0.5
)


# ------------------------------------------------------------
# Werte direkt an die Punkte schreiben
# ------------------------------------------------------------

for x, y in zip(
    profile_wind,
    profile_pressure
):

    ax_wind.annotate(
        f"{x:.1f} m/s",

        (x, y),

        xytext=(8, 0),

        textcoords="offset points",

        va="center"
    )


# ============================================================
# 21. LAYOUT
# ============================================================

plt.tight_layout()

plt.show()
