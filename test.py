import forecast as fr

# name = "repairs"
# name = "monthly"
# name = "weekly"
#name = "weekly2"
#name = "salford"
# name = "car"
name = "plu"

data = fr.read_data(name, header = 0)

data.set_name(name)
data.set_unit("repairs")
data.set_forecast_length(12)
# data /= (10 ** 6)


# SETTINGS
fr.simple_print(0)
data.backup()
log = 1

data.plot()

# AUTO
#data.auto(log = log)


# SIMULATE
#data.simulate(trend = 10, period = 10, noise = 2).plot()

# SMOOTH
#data.smooth(length = 5)

# MANUAL TREND
#data.update_trend(0)

# FIND TREND
#trend = data.find_trend(method = "test", test_length = None, log = log)
#data.update_trend(trend)

# MANUAL SEASON
#data.update_season(52, detrend = None)

# FIND SEASON
# threshold = 2
# seasons_acf = data.find_seasons(detrend = None, source = "acf", threshold = threshold, plot = 1, log = log)
# seasons_fft = data.find_seasons(detrend = 3, source = "fft", threshold = threshold, plot = 0, log = log)
# seasons = seasons_acf + seasons_fft
# data.update_season(*seasons, detrend = None)


# NAIVE PREDICTOR
#data.use_naive('zero')


# EXPONENTIAL SMOOTHING 
#data.use_es(period = 52)

# FIND EXPONENTIAL SMOOTHING 
#es_seasons = data.all_seasons()
#data.find_es(es_seasons, method = "Data", test_length = None, log = log)

# PROPHET
#data.use_prophet(seasonality = True, points = 5)

# FIND PROPHET
#data.find_prophet(order = 10, method = "Data", test_length = None, log = log)

# AUTO ARIMA
#data.use_auto_arima(period = 52, max_order = 1)

# ARIMA
#data.use_arima(0,1,1, 1,0,0, 52)

# FIND ARIMA
#arima_periods = data.all_seasons(threshold = 2.8)
#data.find_arima(arima_periods, method = "Data", test_length = None, order = 1, log = log)

# UNOBSERVED COMPONENTS
#data.use_uc(level = 0, cycle = True, seasonal = 12, autoregressive = 1, stochastic = True)

# FIND UNOBSERVED COMPONENTS
#uc_periods = data.all_seasons(threshold = 2.8)
#data.find_uc(uc_periods, method = "Data", test_length = None, order = 0, log = log)

# CUBIST
#data.use_cubist(committees = 1, neighbors = 3, composite = True, unbiased = True)

# FIND CUBIST
#data.find_cubist(order = 10, method = "Data", test_length = None, log = log)

# LOG and PLOT
# data.log() if log else None
# data.log_split() if log else None
# data.plot()

# FORECAST and SAVE RESULTS
#data.save_forecast()
