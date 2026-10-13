#https://github.com/fmidev/fmi-open-pv-forecast-packaged/blob/main/examples.md
import datetime
import fmi_pv_forecaster as pvfc
import matplotlib.pyplot as plt

# system parameters, declared as variables so we can also plot the same values in the plot easily
tilt = 12
azimuth = 170
size = 12  # 12kw
# setting parameters
pvfc.set_angles(tilt, azimuth)  # south-west facing panels
pvfc.set_location(62.9, 27.6)
pvfc.set_nominal_power_kw(size)

# setting parameters which affect clearsky forecast
pvfc.set_default_air_temp(14)
pvfc.set_default_albedo(0.2)

# generating forecast
date_start = datetime.datetime(2021, 5, 30, 0, 0)
date_end = datetime.datetime(2021, 5, 30, 23, 59)

data = pvfc.get_clearsky_forecast_for_interval(date_start, date_end, 1)
# ^ final input variable here chooses the time between measurements in minutes. 1 results in really smooth plots

# plotting forecast
fig, ax = plt.subplots(layout='constrained')

plt.plot(data.index, data["output"], label="Clearsky forecast", color="black")

# adding axis labels, titles and other text elements
ax.set_xlabel("Time")
ax.set_ylabel("Power(W)")

timenow = date_start
timenow_string = datetime.datetime.fromtimestamp(timenow.timestamp()).strftime('%Y-%m-%d %H:%M')
plt.title("PV Forecast - " + timenow_string)

# parameter string, shows in the plot
explainer_txt = "Tilt: " + str(tilt) + " Azimuth: " + str(azimuth) + "\n" + "Size: " + str(size) + "kW."
# adding the parameter string to the plot, forecast start a X position, 80% of max power as text Y.
plt.text(date_start, max(data["output"]) * 0.8, explainer_txt)

ax.grid()

plt.legend(loc='upper right')

# showing plot
plt.show()

