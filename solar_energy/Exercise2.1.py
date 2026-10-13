import fmi_pv_forecaster as pvfc
import datetime
import matplotlib.pyplot as plt

# setting parameters
pvfc.set_angles(25, 235)  # south-west facing panels
pvfc.set_location(55.6804144, 12.5821649)  # near Copenhagen, Denmark
pvfc.set_nominal_power_kw(10)

# setting parameters which affect clearsky forecast
pvfc.set_default_air_temp(-5)
pvfc.set_default_albedo(0.7)

# generating forecast
data = pvfc.get_default_fmi_forecast()

# generating clearsky forecast
data_clearsky = pvfc.get_default_clearsky_forecast(5)

# plotting forecast
fig, ax = plt.subplots(layout='constrained')

plt.plot(data.index, data["output"], label="Forecast", color="#303193")
plt.plot(data_clearsky.index, data_clearsky["output"], label="Cloud free forecast", color="#6ec8fa")

# adding axis labels, titles and other text elements
ax.set_xlabel("Time")
ax.set_ylabel("Power(W)")

timenow = datetime.datetime.now()
timenow_string = datetime.datetime.fromtimestamp(timenow.timestamp()).strftime('%Y-%m-%d %H:%M')
plt.title("PV Forecast - " + timenow_string)

plt.legend(loc='upper right')

# showing plot
plt.show()