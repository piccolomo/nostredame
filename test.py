import forecast as fr
import plotext as plx

#fr.simple_print(0)

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
data.set_name("weekly repairs plu").set_unit("repairs")
data.set_forecast_length(12)

# #data.simulate(period = 50).plot()


# data.backup()

# log = 1

# trend = data.find_trend(10)
# data.update_trend(trend)
# #data.update_trend(2)

# threshold = 3
# seasons_acf = data.find_seasons(detrend = 3, source = "acf", threshold = threshold, plot = 0, log = log)
# seasons_fft = data.find_seasons(detrend = 3, source = "fft", threshold = threshold, plot = 0, log = log)
# seasons = seasons_acf + seasons_fft
# data.update_season(*seasons, detrend = 3)
# #data.update_season(52, 7, detrend = 3)

# #es_seasons = list(range(data.l))
# #es_seasons = data.all_seasons(detrend = 3)
# #es = data.find_es(es_seasons)
# #data.use_es(es)

# #data.use_auto_arima(fr.dictionary.auto_arima.default())

# # arima = data.find_arima([52], order = 1)
# # data.use_arima(arima)

# # uc = data.find_uc([52], order = 1)
# # data.use_uc(uc)

# # prophet = data.find_prophet(order = 10)
# # data.use_prophet(prophet)

# # cubist = data.find_cubist(order = 10)
# # data.use_cubist(cubist)

# data.use_es(fr.dictionary.es.default(52))
# #data.use_arima(fr.dictionary.arima.default(0, 1, 1, 0, 1, 0, 12))
# #data.use_uc(fr.dictionary.uc.default(fr.uc_levels[1], True, 52, True, False))

# data.log()
# data.log_split()
data.plot()

# f = data.forecast()
# f.plot()
# #f.save_plot()
# f.save_background()

# e = data.extend()
# e.plot()
# e.save_plot()
