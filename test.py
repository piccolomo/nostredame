import forecast as fr
import plotext as plx

# name = "repairs"
# data = fr.read_data(name)
# data.set_name("weekly repairs")
# data.set_unit("M£")
# data.set_forecast_length(12)

# name = "monthly"
# data = fr.read_data(name)
# data /= (10 ** 6)
# data.set_name("monthly repairs")
# data.set_unit("M£")
# data.set_forecast_length(12)

# name = "weekly.csv"
# data = fr.read_data(name)
# data /=  10 ** 6
# data.set_name("weekly repairs")
# data.set_unit("M£")
# data.set_forecast_length(12)

# name = "weekly2.csv"
# data = fr.read_data(name, header = 0)
# data.set_name("weekly2")
# data.set_unit("repairs")
# data.set_forecast_length(12)

# name = "stock1.csv"
# data = fr.read_data(name, header = 0)
# data.set_name("stock1").set_unit("$")
# data.set_forecast_length(12)

# name = "stock2.csv"
# data = fr.read_data(name, header = 0)
# data.set_name("stock2").set_unit("$")
# data.set_forecast_length(12)

# name = "salford.csv"
# data = fr.read_data(name, header = 0)
# data.set_name("salford").set_unit("$")
# data.set_forecast_length(12)

# name = "car.csv"
# data = fr.read_data(name, header = 0)
# data.set_name("weekly repairs car").set_unit("repairs")
# data.set_forecast_length(12)

name = "plu.csv"
data = fr.read_data(name, header = 0)
#data.set_name("weekly repairs plu").set_unit("repairs")
data.set_forecast_length(12)


# SETTINGS
fr.simple_print(0)
data.backup()
log = 1


# SIMULATE
# data.simulate(period = 50).plot()

# MANUAL TREND
data.update_trend(0)

# FIND TREND
#trend = data.find_trend(log = log)
# data.update_trend(trend)

# MANUAL SEASON
data.update_season(52, detrend = None)

# FIND SEASON -----------
# threshold = 2
# seasons_acf = data.find_seasons(detrend = None, source = "acf", threshold = threshold, plot = 1, log = log)
# seasons_fft = data.find_seasons(detrend = 3, source = "fft", threshold = threshold, plot = 0, log = log)
# seasons = seasons_acf + seasons_fft
# data.update_season(*seasons, detrend = None)

# NAIVE -----------
#data.use_naive('zero')


# EXPONENTIAL SMOOTHING 
#data.use_es(period = 52)

# FIND EXPONENTIAL SMOOTHING 
#es_seasons = data.all_seasons()
#data.find_es(es_seasons, log = log)

# PROPHET
#data.use_prophet(seasonality = True, points = 5)

# FIND PROPHET
#data.find_prophet(order = 10, log = log)

# AUTO ARIMA
#data.use_auto_arima(period = 52, max_order = 1)

# ARIMA
data.use_arima(0,1,1, 1,0,0, 52)

# FIND ARIMA
#arima_periods = data.all_seasons(threshold = 2.8)
#data.find_arima(arima_periods, order = 1, log = log)

# UNOBSERVED COMPONENTS
#data.use_uc(level = 0, cycle = True, seasonal = 12, autoregressive = 1, stochastic = True)

# FIND UNOBSERVED COMPONENTS
#uc_periods = data.all_seasons(threshold = 2.8)
#data.find_uc(uc_periods, order = 0, log = log)

# CUBIST
#data.use_cubist(committees = 1, neighbors = 3, composite = True, unbiased = True)

# FIND CUBIST
#data.find_cubist(order = 10, log = log)

data.log()
# data.log_split()
data.plot()

# f = data.forecast()
# f.plot()
# #f.save_plot()
# f.save_background()

# e = data.extend()
# e.plot()
# e.save_plot()
