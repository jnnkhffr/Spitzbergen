import xarray as xr
import numpy as np


# ============================================================
# ERA5
# ============================================================

era5_file = r"C:\Users\janni\Desktop\Spitzbergen\Slides\Exercise\Exercise1\era5_constants-2.nc"

era5 = xr.open_dataset(era5_file)

print("\n================ ERA5 ================")

print("Latitude:")
print(era5.latitude)

print("\nLongitude:")
print(era5.longitude)

print("\nLatitude shape:", era5.latitude.shape)
print("Longitude shape:", era5.longitude.shape)


# ============================================================
# AROME Arctic
# ============================================================

arome_file = (
    "https://thredds.met.no/thredds/dodsC/"
    "aromearcticlatest/latest/"
    "arome_arctic_lagged_6_h_latest_2_5km_latest.nc"
)

arome = xr.open_dataset(arome_file)

print("\n================ AROME ================")

print("Latitude:")
print(arome.latitude)

print("\nLongitude:")
print(arome.longitude)

print("\nLatitude shape:", arome.latitude.shape)
print("Longitude shape:", arome.longitude.shape)

print("\nAROME dimensions:")
print(arome.dims)

print(arome)
print(list(arome.data_vars))
print(arome.coords)
print(arome.dims)

