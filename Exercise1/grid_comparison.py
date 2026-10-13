import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# 1. ERA5 laden
era5_file = r"C:\Users\janni\Desktop\Spitzbergen\Slides\Exercise\Exercise1\era5_constants-2.nc"

era5 = xr.open_dataset(era5_file)

# Bereich um Longyearbyen / Adventdalen
era5_area = era5.sel(
    longitude=slice(14, 17),
    latitude=slice(78.5, 78)
)

# ERA5 Terrainhöhe
era5_terrain = era5_area["z"] / 9.80665


# 2. AROME laden
arome_file = (
    "https://thredds.met.no/thredds/dodsC/"
    "aromearcticlatest/latest/"
    "arome_arctic_lagged_6_h_latest_2_5km_latest.nc"
)

arome = xr.open_dataset(arome_file)

# Erstes Ensemblemitglied
arome = arome.sel(ensemble_member=0)


# 3. AROME auf Region beschränken
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


# 4. Koordinaten vorbereiten
# ERA5: 1D -> 2D
era5_lon, era5_lat = np.meshgrid(
    era5_area.longitude.values,
    era5_area.latitude.values
)

# AROME: bereits 2D
arome_lon = arome_area.longitude.values
arome_lat = arome_area.latitude.values


# 5. Karte
fig = plt.figure(figsize=(10, 10))

ax = plt.axes(
    projection=ccrs.PlateCarree()
)

ax.set_extent(
    [13, 18, 77.7, 78.7],
    crs=ccrs.PlateCarree()
)




# 6. Land / See
ax.add_feature(
    cfeature.OCEAN,
    facecolor="lightblue",
    zorder=0
)

ax.add_feature(
    cfeature.LAND,
    facecolor="lightgray",
    zorder=1
)


# 7. ERA5 Gridpunkte

ax.scatter(
    era5_lon,
    era5_lat,
    color="red",
    s=40,
    marker="s",
    transform=ccrs.PlateCarree(),
    label="ERA5 grid points",
    zorder=5
)


# 8. AROME Gridpunkte
ax.scatter(
    arome_lon,
    arome_lat,
    color="blue",
    s=4,
    transform=ccrs.PlateCarree(),
    label="AROME Arctic grid points",
    zorder=6
)


# 9. Longyearbyen
longyearbyen_lon = 15.465
longyearbyen_lat = 78.246

ax.scatter(
    longyearbyen_lon,
    longyearbyen_lat,
    color="yellow",
    edgecolor="black",
    s=150,
    transform=ccrs.PlateCarree(),
    zorder=10,
    label="Longyearbyen"
)

ax.text(
    15.53,
    78.26,
    "Longyearbyen",
    transform=ccrs.PlateCarree(),
    zorder=10
)


# 10. Kartenelemente

ax.coastlines(resolution="10m")

ax.add_feature(
    cfeature.BORDERS,
    linestyle=":"
)

gl = ax.gridlines(
    draw_labels=True,
    linewidth=0.5,
    color="gray",
    linestyle="--"
)

gl.top_labels = False
gl.right_labels = False

plt.title(
    "ERA5 and AROME Arctic Grid Around Longyearbyen"
)

plt.legend()

plt.tight_layout()

plt.show()

# next step: Die UNIS Wetterstationen mit einbauen.