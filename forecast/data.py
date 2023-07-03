from forecast.backup import backup_class, copy_class
from forecast.plot import plot_class
from forecast.trend import trend_class, generate_trend
from forecast.season import season_class, generate_season, find_seasons
from forecast.prediction import prediction_class
from forecast.quality import quality_class, is_like_list
from forecast.values import values_class
from forecast.study import study_class

from forecast.string import enclose_circled, nl, enclose_squared, bold, nl, indicator, pad
from forecast.path import read_time_data, correct_path, join_paths, output_folder
from forecast.dictionary import dictionary

import pandas as pd
import numpy as np


def read_data(path, header = True, form = None):
    time, values = read_time_data(path, header, form)
    return data_class(time, values)


class data_class(copy_class, backup_class, plot_class):
    def __init__(self, time = [], values = []):
        self.set_name(); self.set_unit()
        
        self._set_time(time)
        self._set_values(values)
        self.set_forecast_length()
        
        self._trend = trend_class()
        self._season = season_class()
        self._prediction = prediction_class()

        self._quality = quality_class()
        self._update_quality()
        
        self._update_label()
        
        backup_class.__init__(self)

        

    def set_name(self, name = None):
        self.name = name
        self._residuals_label = self.name
        return self

    def get_name(self):
        return self.name.title() if self.name is not None else "Data"

    def _get_path(self, name):
        name = name if name is not None else self.name if self.name is not None else "data"
        name = name.lower().replace(' ', '-')
        path = join_paths(output_folder, name)
        return correct_path(path)

    
    
    def set_unit(self, unit = None):
        self.unit = unit
        return self
        
    def get_unit(self, enclosed = False):
        return "" if self.unit is None else enclose_squared(self.unit) if enclosed else self.unit


    
    def _set_time(self, time):
        self._time = time.copy()

    def get_time(self):
        return self._time.datetime

    

    def _set_values(self, values):
        self._values = values.copy()
        self.length = self.l = self._values.length
        #self._values.sort(self._time.index_to_sort)

    def get_data(self):
        return self._values.data

    def get_dataframe(self):
        return pd.DataFrame(index = self._time.pandas_index, data = {'values': self.get_data()})

    
    def set_forecast_length(self, length = None):
        self.forecast_length = (0.2 * self.l) if length is None else length
        self.test_length = round(self.forecast_length / (self.l + self.forecast_length) * self.l)
        self.train_length = self.length - self.test_length

        

    def update_trend(self, order = None):
        self.fit_trend(order)
        self._update_trend_data()
        
        self._update_quality(); self._update_label(); 
        
    def fit_trend(self, order = None):
        order = self._trend.order if order is None else order
        self._trend.fit(self._time, self._values, order)

    def _update_trend_data(self):
        self._trend.update_data(self._time)

    def zero_trend(self):
        self._trend.zero()

    def get_trend(self):
        trend = self._trend.get_data()
        return trend if is_like_list(trend) else np.array([trend] * self.length)

    def find_trend(self, max_order = 15, test_length = None, method = "test", log = True):
        arguments = list(range(0, max_order + 1))
        trend = self._find_best(function_name = "update_trend", arguments = arguments, test_length = test_length, method = method, log = log)
        self.update_trend(trend)

    
        
    def update_season(self, *periods, detrend = None):
        detrend = self._trend.order  if detrend is None and self._trend.order is not None else detrend
        self.fit_season(*periods, detrend = detrend)
        self._update_season_data()

    def fit_season(self, *periods, detrend = None):
        periods = self._season.periods if len(periods) == 0 else periods
        self._season.fit(self._time, self._values, periods, detrend)
        self._season.update_label()

    def _update_season_data(self):
        self._season.update_data(self._time)
        self._update_quality()

    def zero_season(self):
        self._season.zero()

    def get_season(self):
        season = self._season.get_data()
        return season if is_like_list(season) else np.array([season] * self.length)

    def find_seasons(self, detrend = None, source = "acf", log = True, plot = False, threshold = 2.5):
        seasons = self.get_seasons(detrend = detrend, source = source, log = log, plot = plot, threshold = threshold)
        self.update_season(*seasons, detrend = detrend)

    def get_seasons(self, detrend = None, source = "acf", log = True, plot = False, threshold = 2.5):
        detrend = self._trend.order + 1 if detrend is None and self._trend.order is not None else detrend
        seasons = find_seasons(self._values.data, detrend_order = detrend, source = source, log = log, plot = plot, threshold = threshold)
        return seasons

    def all_seasons(self, detrend = None, threshold = 1):
        acf = self.get_seasons(detrend = detrend, source = "acf", log = False, threshold = threshold)
        fft = self.get_seasons(detrend = detrend, source = "fft", log = False, threshold = threshold)
        return list(set(acf + fft))


    
    def add_predictor(self, name, dictionary = None, weight = 1):
        self._prediction.add_predictor(name, dictionary, weight)

    def update_prediction(self):
        self._fit_predictors()
        self._update_prediction_data()

    def _fit_predictors(self):
        residuals = values_class(self.get_residuals())
        self._prediction.fit(self._time, residuals)
        return self

    def _update_prediction_data(self):
        self._prediction.update(self._time)
        self._update_quality()
        
    def use_predictor(self, name, dictionary = None):
        self.zero_prediction()
        self.add_predictor(name, dictionary = dictionary)
        self.update_prediction()

    def zero_prediction(self):
        self._prediction.zero()

    use_naive_dict = lambda self, dictionary: self.use_predictor("naive", dictionary)
    use_naive = lambda self, level = 'mean': self.use_naive_dict(dictionary.naive.default(level)) 

    use_es_dict = lambda self, dictionary: self.use_predictor("es", dictionary)
    use_es = lambda self, period: self.use_es_dict(dictionary.es.default(period))
    
    def find_es(self, periods = [], test_length = None, method = "Data", log = True):
        arguments = dictionary.es.all(periods)
        es_dict = self._find_best(function_name = "use_es_dict", arguments = arguments, test_length = test_length, method = method, log = log)
        self.use_es_dict(es_dict)

    use_prophet_dict = lambda self, dictionary: self.use_predictor("prophet", dictionary)
    use_prophet = lambda self, seasonality = True, points = 12: self.use_prophet_dict(dictionary.prophet.default(seasonality, points)) 

    def find_prophet(self, order = 10, test_length = None, method = "Data", log = True):
        arguments = dictionary.prophet.all(order)
        prophet_dict = self._find_best(function_name = "use_prophet_dict", arguments = arguments, test_length = test_length, method = method, log = log)
        self.use_prophet_dict(prophet_dict)

    use_auto_arima_dict = lambda self, dictionary: self.use_predictor("auto_arima", dictionary)
    use_auto_arima = lambda self, period = 1, max_order = 2: self.use_auto_arima_dict(dictionary.auto_arima.default(period, max_order)) 
    
    use_arima_dict = lambda self, dictionary: self.use_predictor("arima", dictionary)
    use_arima = lambda self, p = 1, d = 1, q = 1, P = 1, D = 1, Q = 1, m = 12: self.use_arima_dict(dictionary.arima.default(p, d, q, P, D, Q, m))
    
    def find_arima(self, periods = [], order = 1, test_length = None, method = "Data", log = True):
        arguments = dictionary.arima.all(periods, order)
        arima_dict = self._find_best(function_name = "use_arima_dict", arguments = arguments, test_length = test_length, method = method, log = log)
        self.use_arima_dict(arima_dict)

    use_uc_dict = lambda self, dictionary: self.use_predictor("uc", dictionary)
    use_uc = lambda self, level = 0, cycle = True, seasonal = 12, autoregressive = 1, stochastic = True: self.use_uc_dict(dictionary.uc.default(level, cycle, seasonal, autoregressive, stochastic))

    def find_uc(self, periods = [], order = 1, test_length = None, method = "Data", log = True):
        arguments = dictionary.uc.all(periods, order)
        uc_dict = self._find_best(function_name = "use_uc_dict", arguments = arguments, test_length = test_length, method = method, log = log)
        self.use_uc_dict(uc_dict)

    use_cubist_dict = lambda self, dictionary: self.use_predictor("cubist", dictionary)
    use_cubist = lambda self, committees = 0, neighbors = 1, composite = True, unbiased = True: self.use_cubist_dict(dictionary.cubist.default(committees, neighbors, composite, unbiased))
            
    def find_cubist(self, order = 10, test_length = None, method = "Data", log = True):
        arguments = dictionary.cubist.all(order)
        cubist_dict = self._find_best(function_name = "use_cubist_dict", arguments = arguments, test_length = test_length, method = method, log = log)    
        self.use_cubist_dict(cubist_dict)


        
    def auto(self, log = True):
        self.find_trend(log = log)
        self.find_seasons(threshold = 2.7, log = log)
        self.find_es(self.all_seasons(), log = log)
        #self.find_prophet(log = log)
        self.log() if log else None
        self.save_forecast(log = log)


        
    def forecast(self, length = None):
        length = self.forecast_length if length is None else length
        time = self._time.forecast(length)
        values = self._values.forecast(length)
        data = data_class(time, values)
        self._project_background_to(data)
        name = self.get_name() + " forecasted" + enclose_circled(length)
        data.set_name(name)
        return data    
        
    def extend(self, length = None):
        length = self.forecast_length if length is None else length
        data = self.append(self.forecast(length))
        name = self.get_name() + " extended" + enclose_circled(length)
        data.set_name(name)
        return data

    def save_forecast(self, log = True):
        self.forecast().plot().save_plot(log = log).save_background(log = log)
        self.extend().plot().save_plot(log = log)

    
        
    def get_treason(self):
        return self.get_trend() + self.get_season()

    def get_background(self):
        yb = self.get_treason() + self._prediction.get_data()
        self.background_ok = not is_zero(yb)
        return yb
    
    def zero_background(self):
        self.zero_trend()
        self.zero_season()
        self.zero_prediction()
        
    def get_background_dataframe(self):
        return pd.DataFrame(index = self._time.pandas_index, data = {'values': self.get_background()})

    def save_background(self, name = None, log = True):
        path = self._get_path(name) + ".csv"
        self.get_background_dataframe().to_csv(path_or_buf = path, header = False)
        print("background saved in", path) if log else None
        return self

    def _project_background_to(self, data, retrain = False):
        data._trend = self._trend.project(data._time)
        data._season = self._season.project(data._time)
        data._prediction = self._prediction.project(data._time)
        data.update_trend() if retrain else None
        data.update_season() if retrain else None
        data.update_prediction() if retrain else None
        data._update_label()
        data._update_quality()

    def get_residuals(self):
        return self.get_data() - self.get_treason()
        

    
    def _update_quality(self):
        y_true, y_pred = self.get_data(), self.get_background()
        self._quality.update(y_true, y_pred)
        return self._quality


    
    def _update_label(self):
        self._trend.update_label(); self._season.update_label(); self._prediction.update_label();
        self._update_label_short()
        self._update_label_long()
        
    def _update_label_short(self):
        labels = [self._trend.label_short, self._season.label_short, self._prediction.label_short]
        labels = [str(el) for el in labels if el is not None]
        no_label = len(labels) == 0
        self._label_short = "No Background" if no_label else ' + '.join(labels)
        self._residuals_label = self.get_name().lower() if no_label else self.get_name() + ' - background'

    def _update_label_long(self):
        labels = [self._trend.label_long, self._season.label_long, self._prediction.label_long]
        labels = [str(el) for el in labels if el is not None]
        no_label = len(labels) == 0
        self._label_long = "No Background" if no_label else nl.join(labels)

    def log(self, test_length = None):
        self._update_label()
        self._update_quality()
        name = "data" if self.name is None else self.name
        title = bold(self.get_name() + " Log")
        study = study_class(self, test_length)
        print(title + nl + self._label_long + nl + study._label_long + nl)
        return self

    def set(self, data):
        data = data if is_like_list(data) else [data] * self.length
        self._values.set(data)
        self._update_quality()
        return self

    def __mul__(self, constant):
        new = self.copy()
        new._trend = self._trend * constant
        new._season = self._season * constant
        new._prediction = self._prediction * constant
        new.set(self._values.data * constant)
        return new

    def __truediv__(self, constant):
        return self * (1 / constant)

    def smooth(self, length):
        return self.set(moving_average(self.get_data(), length))

    def simulate(self, trend = 0, period = 12, noise = 0.1):
        season = generate_season(period, self._values.delta / 3, self.l, trend, noise)
        trend = generate_trend(self._values.mean, self._values.delta, self.l, trend, noise)
        noise = generate_noise(0, noise, self.l)
        self.set(trend + season + noise)
        return self

    def white(self):
        self._values.white()
        self._update_quality()

        

    def part(self, begin, end, retrain = False):
        time = self._time.part(begin, end)
        values = self._values.part(begin, end)
        data = data_class(time, values)
        self._project_background_to(data, retrain)
        return data

    def split(self, test_length = None, retrain = False):
        test_length = self.test_length if test_length is None else test_length
        test_length = ratio_to_length(test_length, self.length)
        train_length = self.length - test_length
        train, test = self.part(0, train_length, retrain), self.part(train_length, self.length)
        train._project_background_to(test, retrain = False) if retrain else None
        train.set_name(self.get_name() + " train")
        test.set_name(self.get_name() + " test")
        train.set_unit(self.unit)
        test.set_unit(self.unit)
        return train, test

    def append(self, data):
        time = self._time.append(data._time)
        values = self._values.append(data._values)
        new = data_class(time, values)
        self._project_background_to(new)
        new.set_name(self.get_name() + " + " + data.get_name())
        return new

    def _find_best(self, function_name, arguments, test_length = None, method = "Data", log = True):
        print("optimizing function", bold(function_name)) if log else None
        data = self.copy()
        results = []
        l = len(arguments)
        for i in range(l):
            argument = arguments[i]
            study = study_class(data, test_length, method)
            #train.zero_background()
            eval("study.data." + function_name + "(argument)")
            study.update()
            results.append([argument, study])
            indicator(i + 1, l) if log else None

        results.sort(key = lambda el: el[1].quality)
        result = results[0][0] if len(results) > 0 else None

        if log and result is not None:
            arg_length = max([len(str(arg)) for arg in arguments])
            spaces = ' ' * (arg_length + 1)
            length_label = results[0][1].get_length()
            title = results[0][1]._label_short_title
            print(length_label)
            print(spaces + title)
            [print(pad(argument, arg_length), study._label_short) for (argument, study) in results]
            print()
            
        return result


    
# Data Utils
is_zero = lambda data: (is_like_list(data) and all(np.array(data) == 0)) or (not is_like_list(data) and data == 0)

generate_noise = lambda mean, amplitude, length: np.random.normal(0, amplitude , length)
ratio_to_length = lambda ratio, length: length if ratio is None else round(ratio * length) if ratio <= 1 else int(ratio)

def moving_average(data, length = 1):
    l = len(data)
    left_half = length // 2
    right_half = (length + 1) // 2
    window = lambda i: range(max(i - left_half, 0) , min(i + right_half, l))
    return [np.mean([data[j] for j in window(i)]) for i in range(l)]
