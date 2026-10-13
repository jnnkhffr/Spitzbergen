#!/usr/bin/env python
# coding: utf-8

# ## Wind Resource Assessment on Svalbard Using CARRA Data
# 
# "The governor of Svalbard is considering an wind farm to reduce diesel consumption. You have been asked to evaluate several potential sites using CARRA reanalysis."

# ### Objectives
# 
# In this exercise you will:
# 
# 1. Visualise near-surface wind conditions from CARRA.
# 2. Produce maps of the study area.
# 3. Calculate wind speed from the wind vector components.
# 4. Characterise the wind climate using a Weibull distribution.
# 5. Estimate wind power density.
# 6. Assess whether the location may be suitable for wind energy production.
# 
# Dataset:
# - CARRA GRIB file
# - Region: West of Svalbard

# In[12]:


import xarray as xr
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature

from scipy.stats import weibull_min
from scipy.special import gamma

import matplotlib.dates as mdates


# ### Task 1
# 
# Open the CARRA nc file and investigate its contents.
# 
# Questions:
# 
# 1. What variables are available?
# 2. What projection is used?
# 3. What is the spatial resolution?
# 4. What time period is covered by the dataset?
# 

# In[13]:


# Carra
# ds = xr.open_dataset(
#     "carra.grib",
#     engine="cfgrib"
# )
file = "C:/Users\janni\Desktop\Spitzbergen\Slides\Exercise\Exercise2\point_timeseries.nc"
# file = '/Volumes/NO NAME/UNIS/point_timeseries.nc'
# file = '/Users/irms/Library/CloudStorage/OneDrive-UniversityofBergen/UniB/UNIS/teaching/excersises/CARRA.nc'
# file = 'your file path'
ds = xr.open_dataset(file)
# ds.longitude.value
ds
# print(float(ds.latitude.compute()))
# print(float(ds.longitude.compute()))


# In[ ]:


# ws_obs = df["VH1_10_min"].dropna()
# print(ws.describe())


# In[99]:


print(ds['ws'].attrs)
list(ds.data_vars)
print(ds)
print(ds.attrs)
print(ds.coords)
print(ds.valid_time.min().values)
print(ds.valid_time.max().values)


# ### Task 2
# 
# Calculate wind speed from the horizontal wind components.
# 
# Questions:
# 
# 1. What is the mean wind speed in the domain?
# 2. What is the maximum wind speed?
# 3. Why is wind speed calculated from both u and v components?

# In[16]:


# ws = np.sqrt(ds["u10"]**2 + ds["v10"]**2)
# ws = ds['ws'][:,0,:,:]
# ws.attrs["units"] = "m s-1"
ws=ds['ws']
ws


# ### Task 3
# 
# Create a map showing:
# 
# - Map containing Svalbard
# - Point of model output

# In[17]:


# Your selected point
lat0 = float(ds.latitude.compute())
lon0 = float(ds.longitude.compute())

fig = plt.figure(figsize=(8, 8))

ax = plt.axes(projection=ccrs.PlateCarree())

# Nice background
ax.add_feature(
    cfeature.LAND,
    facecolor="0.9",
    edgecolor="black",
    linewidth=0.5,
    zorder=1,
)

ax.add_feature(
    cfeature.OCEAN,
    facecolor="white",
    zorder=0,
)

ax.coastlines(
    resolution="10m",
    linewidth=0.8,
)

# Extent around location
ax.set_extent([
    lon0 - 8,
    lon0 + 8,
    lat0 - 4,
    lat0 + 4
])

# Plot point
ax.plot(
    lon0,
    lat0,
    marker="o",
    markersize=10,
    color="crimson",
    markeredgecolor="black",
    markeredgewidth=1,
    transform=ccrs.PlateCarree(),
    zorder=10,
)

# Annotation
ax.text(
    lon0 + 0.3,
    lat0 + 0.1,
    f"{lat0:.2f}°N\n{lon0:.2f}°E",
    fontsize=11,
    weight="bold",
    transform=ccrs.PlateCarree(),
    bbox=dict(
        facecolor="white",
        alpha=0.8,
        edgecolor="none"
    ),
)

# Gridlines
gl = ax.gridlines(
    draw_labels=True,
    linewidth=0.5,
    linestyle="--",
    alpha=0.5,
)

gl.top_labels = False
gl.right_labels = False

plt.title(
    "Location of Wind Analysis Site",
    fontsize=14,
    weight="bold",
)

plt.tight_layout()
plt.show()


# ### Task 4
# 
# Choose a location on eastern Svalbard and extract a wind speed time series.
# 
# Questions:
# 
# 1. What are the coordinates?
# 2. Why might this location be interesting for wind energy production?

# In[ ]:


# haversine function to calculate closest points
def nearest_grid_point(ds, lat0, lon0):

    R = 6371.0  # Earth radius [km]

    lat1 = np.radians(lat0)
    lon1 = np.radians(lon0)

    lat2 = np.radians(ds.latitude.values)
    lon2 = np.radians(ds.longitude.values)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat/2)**2 +
        np.cos(lat1) *
        np.cos(lat2) *
        np.sin(dlon/2)**2
    )

    c = 2 * np.arctan2(
        np.sqrt(a),
        np.sqrt(1-a)
    )

    distance = R * c

    iy, ix = np.unravel_index(
        np.argmin(distance),
        distance.shape
    )

    return iy, ix

# iy, ix = nearest_grid_point(ds, 78.25, 23.5)

# point = ds.isel(y=iy, x=ix)


# ### Task 5
# 
# Create a wind speed time series.
# 
# Questions:
# 
# 1. Does the location appear windy?
# 2. Are there calm periods?
# 3. Is there evidence of storm events?

# In[18]:


ds = ds.sortby("valid_time")


# In[19]:


fig, ax = plt.subplots(figsize=(12,4))

ax.plot(ds.valid_time, ds.ws, lw=0.8)

# One tick every 3 days
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))

ax.set_ylabel("Wind speed (m s$^{-1}$)")
ax.set_xlabel("Date")

ax.grid(alpha=0.3)

plt.tight_layout()
plt.show()


# ### Task 6
# 
# Produce a histogram of wind speed.
# 
# Questions:
# 
# 1. Is the distribution symmetric?
# 2. At which wind speed does the histogram peak?
# 3. Are high wind speeds common or rare?

# In[20]:


windspeed = ds['ws'][~np.isnan(ds['ws'])]

plt.figure(figsize=(8,5))

plt.hist(
    windspeed,
    bins=25,
    density=True,
    alpha=0.6
)

plt.xlabel("Wind speed (m/s)")
plt.ylabel("Probability density")

plt.title("Observed Wind-Speed Distribution")

plt.show()


# ### Task 7
# 
# Fit a Weibull distribution to the wind-speed data.
# 
# Questions:
# 
# 1. What are the fitted values of A and k?
# 2. What does the scale parameter A represent?
# 3. What does the shape parameter k represent?
# 4. Is the wind climate highly variable or relatively persistent?

# In[21]:


k, loc, A = weibull_min.fit(
    windspeed,
    floc=0
)

print(f"A = {A:.2f} m/s")
print(f"k = {k:.2f}")


# ### Task 8
# 
# Compare the observed wind-speed distribution and the fitted Weibull distribution.
# 
# Questions:
# 
# 1. Does the Weibull provide a good fit?
# 2. Where do the largest differences occur?
# 3. What meteorological reasons could explain these differences?

# In[22]:


x = np.linspace(
    0,
    windspeed.max(),
    300
)

pdf = weibull_min.pdf(
    x,
    k,
    scale=A
)

plt.figure(figsize=(8,5))

plt.hist(
    windspeed,
    bins=25,
    density=True,
    alpha=0.4,
    label="CARRA"
)

plt.plot(
    x,
    pdf,
    "r",
    linewidth=3,
    label="Weibull fit"
)

plt.xlabel("Wind speed (m/s)")
plt.ylabel("Probability density")

plt.legend()

plt.show()


# ### Task 9
# 
# Estimate the wind power density.
# 
# The wind power density is
# 
# P = 0.5 ρ A³ Γ(1+3/k)
# 
# Assume:
# 
# ρ = 1.225 kg m⁻³
# 
# Questions:
# 
# 1. What is the estimated wind power density?
# 2. How does it compare with typical wind farm sites?
# 3. Would this location be suitable for wind energy production?

# In[23]:


rho = 1.225

wpd = (
    0.5
    * rho
    * A**3
    * gamma(1 + 3/k)
)

print(f"Wind power density = {wpd:.1f} W m^-2")


# ### Task 10
# 
# Interpret your results.
# 
# Typical values:
# 
# | Resource quality | Wind power density |
# |-----------------|-------------------|
# | Poor | <100 W m⁻² |
# | Fair | 100–300 W m⁻² |
# | Good | 300–500 W m⁻² |
# | Excellent | >500 W m⁻² |
# 
# Questions:
# 
# 1. Into which category does your location fall?
# 2. What are the strengths and weaknesses of the site?
# 3. What additional information would be required before building a wind farm?

# ## Discussion
# 
# Summarise:
# 
# 1. The local wind climate.
# 2. The Weibull parameters obtained.
# 3. The estimated wind power density.
# 4. Whether the location appears suitable for wind energy.
# 5. The advantages and limitations of using reanalysis/model data (CARRA) instead of observations.

# ## Why Not Just Use the Mean Wind Speed?
# 
# A common way to describe a windy location is by its average wind speed.
# 
# For example:
# 
# - Site A: mean wind speed = 8 m/s
# - Site B: mean wind speed = 8 m/s
# 
# At first glance, these sites appear identical.
# 
# However, wind turbines do not produce power proportional to wind speed. Wind power is approximately proportional to the cube of wind speed:
# 
# P ∝ U³
# 
# This means that:
# 
# - Doubling the wind speed increases power by a factor of 8.
# - A few strong winds can contribute a large fraction of total energy production.
# 
# Therefore, two sites with the same average wind speed may have very different wind energy potential.

# ### Observations
# Now use obs from Adventdalen, make a histrogram, fi the Weibull distribution and compare to the offshore location. \

# In[24]:


# Observations Adventdalen
file = "C:/Users\janni\Desktop\Spitzbergen\Slides\Exercise\Exercise2\Adventdalen_Hour.dat"

with open(file, "r", errors="ignore") as f:
    for i in range(20):
        print(f.readline().rstrip())


# In[25]:


df = pd.read_csv(
    file,
    skiprows=[0, 2, 3],  # skip metadata, units, and type rows
    parse_dates=["TIMESTAMP"]
)

print(df.head())
print(df.columns)

