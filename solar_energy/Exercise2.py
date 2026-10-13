import fmi_pv_forecaster as pvfc

"""
This example shows the minimal amount of needed code for forecasting PV output.
Panel angles are south facing with a tilt of 25 degrees, fairly typical for roof mounted panels.
Geolocation is within Helsinki.
Power rating set at 4kw.
"""

pvfc.set_angles(25, 180)
pvfc.set_location(60.1576, 24.8762)
pvfc.set_nominal_power_kw(4)

data = pvfc.get_default_fmi_forecast()

print("Forecast:")
print(data)

