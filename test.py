import forecast as fr

# name = "repairs"
# name = "monthly"
# name = "weekly"
#name = "weekly2"
name = "salford"
name = "car"
name = "plu"

data = fr.read_data(name, header = 0)

data.set_name(name)
data.set_unit("repairs")
data.set_forecast_length(12)
# data /= (10 ** 6)

# SETTINGS
#fr.simple_print(1)
#fr.set_screen_default_size(1024, 768)
#data.backup()
log = 1

# INITIAL PLOT
#data.plot()

# AUTO
#data.auto(trend = True, season = True, prediction = True, log = True, save = True)
#data.auto(trend = 1, season = False, prediction = False, log = True, save = 1it)
# trend: False for no trend, True to automatically find it, and integer for specific value
# season: False for no season, True to automatically find it, and integer for specific value or a list of integers
# prediction: False for no prediction, True to automatically find best exponential smoothing, and integer for specific exponential smoothing or the string "deep" to find all possible best predictors (es, prophet, arima, uc, cubist if available) and combine them with weighted average (depending on their error)

# SIMULATE
#data.simulate(trend = 2, season = 52, noise = 0.1)#.plot()

# TURN WHITE
#data.white()#.plot()

# SMOOTH
#data.smooth(length = 5)#.plot()

# PLOT ACF or FFT if needed
#data.plot_acf()
#data.plot_fft()

# MANUAL TREND
#data.update_trend(2)

# FIND TREND
#data.find_trend(order = 15, test_length = None, method = "test", apply_result = True, log = log)

# MANUAL SEASON
#data.update_season(52, detrend = None)#.plot()

# FIND SEASONS and study them
# data.find_seasons(detrend = None, source = "acf", threshold = 2.5, apply_result = False, plot = 1, log = log)
# data.find_seasons(detrend = 3, source = "fft", threshold = 1.5, apply_result = False, plot = 1, log = log)

# FIND SEASON QUICKLY
#seasons = data.all_seasons(detrend = 4, threshold = 2.5, log = log)
#data.update_season(*seasons, detrend = 4)

# FIND BEST PREDICTOR
# data.find_naive(test_length = None, method = "Data", apply_result = True, log = log)
# data.find_es(seasons = data.all_seasons(threshold = 1.5), test_length = None, method = "Data", apply_result = True, log = log)
# data.find_prophet(order = 10, test_length = None, method = "Data", apply_result = True, log = log)
#data.find_arima(seasons = data.all_seasons(threshold = 2.8), order = 1, test_length = None, method = "Data", apply_result = True, log = True)
#data.find_uc(seasons = data.all_seasons(threshold = 2.8), order = 1, test_length = None, method = "Data", apply_result = True, log = True)
#data.find_cubist(order = 10, test_length = None, method = "Data", apply_result = True, log = log)

# ADD PREDICTOR MANUALLY
#data.add_naive(level = 'zero', weight = 1)
#data.add_es(seasonal_periods = 52, weight = 1)
# data.add_prophet(yearly_seasonality = True, n_changepoints = 12, weight = 1)
# #data.add_auto_arima(m = 1, max_order = 2, weight = 1)
# data.add_arima(order = (1, 0, 1), seasonal_order = (0, 1, 0, 0), weight = 1)
# data.add_uc(level = "random walk", cycle = True, seasonal = 12, autoregressive = 1, stochastic_cycle = True, weight = 1)
#data.add_cubist(n_committees = 0, neighbors = 1, composite = True, unbiased = True, weight = 1)

# LOG 
#data.log(test_length = None) if log else None

# PLOT
#data.plot()

# ATOMATICALLY PLOT and SAVE FORECASTED and EXTENDED RESULTS
#data.save_all()

# MANUALLY PLOT and SAVE FORECASTED and EXTENDED RESULTS
#data.forecast().plot().save_plot(log = log).save_background(log = log)
#data.extend().plot().save_plot(log = log)
