from forecast.backup import backup_class, copy_class
from forecast.plot import plot_class
from forecast.trend import trend_class, generate_trend
from forecast.season import season_class, generate_season
from forecast.prediction import prediction_class, zero
from forecast.quality import quality_class, is_like_list
from forecast.values import values_class
from forecast.study import study_class
from forecast.best import find_best_class

from forecast.string import enclose_circled, nl, enclose_squared, bold, nl
from forecast.path import read_time_data, read_time_dataframe, correct_path, join_paths, output_folder
from forecast.dictionary import dictionary
from .platform import platform, set_screen_default_size

import pandas as pd
import numpy as np


def read_data(path, header = True, form = None):
    time, values = read_time_data(path, header, form)
    return data_class(time, values)

def read_dataframe(frame, time_name = None, values_name = None):
    time, values = read_time_dataframe(frame, time_name, values_name)
    return data_class(time, values)

class data_class(copy_class, backup_class, plot_class, find_best_class):
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
        set_screen_default_size()

        

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
        return self

        

    def update_trend(self, order = None):
        self._fit_trend(order)
        self._update_trend_data()
        
        self._update_quality(); self._update_label();
        return self
        
    def _fit_trend(self, order = None):
        #order = self._trend.order if order is None else order
        self._trend.fit(self._time, self._values, order)

    def _update_trend_data(self):
        self._trend.update_data(self._time)

    def _retrain_trend(self):
        self.update_trend(self._trend.order)

    def zero_trend(self):
        self._trend.zero()
        return self

    def get_trend(self):
        trend = self._trend.get_data()
        return trend if is_like_list(trend) else np.array([trend] * self.length)

    def get_trend_dataframe(self):
        return pd.DataFrame(index = self._time.pandas_index, data = {'values': self.get_trend()})

    
    def update_season(self, *seasons, detrend = None):
        self._fit_season(*seasons, detrend = detrend)
        self._update_season_data()
        return self

    def _fit_season(self, *seasons, detrend = None):
        detrend = self.correct_detrend_order(detrend)
        self._season.fit(self._time, self._values, seasons, detrend)
        self._season.update_label()

    def _update_season_data(self):
        self._season.update_data(self._time)
        self._update_quality()

    def _retrain_season(self):
        self.update_season(*self._season.periods, detrend = self._season.order)

    def zero_season(self):
        self._season.zero()
        return self

    def get_season(self):
        season = self._season.get_data()
        return season if is_like_list(season) else np.array([season] * self.length)

    def get_season_dataframe(self):
        return pd.DataFrame(index = self._time.pandas_index, data = {'values': self.get_season()})
    
    
    def correct_detrend_order(self, detrend = None):
        trend_order = self._trend.order
        return None if detrend is None and trend_order is None else trend_order + 1 if detrend is None and trend_order is not None else detrend


    
    def add_predictor(self, name, dictionary = None, weight = 1):
        self._prediction.add_predictor(name, dictionary, weight)
        self.update_prediction()
        return self

    def update_prediction(self):
        self._fit_predictors()
        self._update_prediction_data()
        return self

    def _fit_predictors(self):
        residuals = values_class(self.get_residuals())
        self._prediction.fit(self._time, residuals)
        return self

    def _update_prediction_data(self):
        self._prediction.update(self._time)
        self._update_quality()
        
    def zero_prediction(self):
        self._prediction.zero()
        return self

    def get_prediction(self):
        return self._prediction.get_data()

    def get_prediction_dataframe(self):
        return pd.DataFrame(index = self._time.pandas_index, data = {'values': self.get_prediction()})

        
    add_naive = lambda self, level = 'mean', weight = 1: self.add_predictor("naive", dictionary.naive.default(level), weight = weight) 
    add_es = lambda self, seasonal_periods, seasonal = 'add', weight = 1: self.add_predictor("es", dictionary.es.default(seasonal_periods, seasonal), weight = weight)
    add_prophet = lambda self,  yearly_seasonality = True, n_changepoints = 12, weight = 1: self.add_predictor("prophet", dictionary.prophet.default(yearly_seasonality, n_changepoints), weight = weight) 

    add_auto_arima = lambda self, m = 1, max_order = 2, weight = 1: self.add_predictor("auto_arima", dictionary.auto_arima.default(m, max_order), weight = weight)
    
    add_arima = lambda self, order = (1, 0, 1), seasonal_order = (0, 1, 0, 0), weight = 1: self.add_predictor("arima", dictionary.arima.default(order, seasonal_order), weight = weight)
    
    add_uc = lambda self, level = 0, cycle = True, seasonal = 12, autoregressive = 1, stochastic_cycle = True, weight = 1: self.add_predictor("uc", dictionary.uc.default(level, cycle, seasonal, autoregressive, stochastic_cycle), weight = weight)

    add_cubist = lambda self, n_committees = 0, neighbors = 1, composite = True, unbiased = True, weight = 1: self.add_predictor("cubist", dictionary.cubist.default(n_committees, neighbors, composite, unbiased), weight = weight)
    
            
        
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

    def save_all(self, log = True):
        self.forecast().plot().save_plot(log = log).save_background(log = log)
        self.extend().plot().save_plot(log = log)
        return self
    

    
    def auto(self, trend = True, season = True, prediction = True, log = True, save = True):
        self.zero_background()
        self.find_trend(log = log) if isinstance(trend, bool) and trend else self.update_trend(trend) if not isinstance(trend, bool) and isinstance(trend, int) else self.update_trend(None)
        
        season = [season] if isinstance(season, int) and not isinstance(season, bool) else season
        self.find_seasons(threshold = 2.7, log = log, apply_result = True) if isinstance(season, bool) and season else self.update_season(*season) if not isinstance(season, bool) and isinstance(season, list) else self.update_season()

        if isinstance(prediction, bool) and prediction:
            self.find_es(self.all_seasons(threshold = 1.0), log = log)
            
        elif not isinstance(prediction, bool) and isinstance(prediction, int): 
            self.add_es(prediction)
            
        elif isinstance(prediction, str):
            self.find_es(self.all_seasons(threshold = 1.0), log = log)
            self.find_prophet(order = 10, log = log)
            arima_seasons = self.all_seasons(threshold = 2.8)
            self.find_arima(arima_seasons, order = 1, log = log)
            self.find_uc(arima_seasons, order = 1, apply_result = False, log = log)
            self.find_cubist(order = 1, log = log) if platform == 'unix' else None

        else:
            self.zero_prediction()
        
        self.log() if log else None
        self.save_all(log = log) if save else None 


        
    def get_treason(self):
        return self.get_trend() + self.get_season()
    
    def get_treason_dataframe(self):
        return pd.DataFrame(index = self._time.pandas_index, data = {'values': self.get_treason()})

    def get_background(self):
        yb = self.get_treason() + self._prediction.get_data()
        self.background_ok = not is_zero(yb)
        return yb
    
    def zero_background(self):
        self.zero_trend()
        self.zero_season()
        self.zero_prediction()
        return self
        
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
        
        data._retrain_trend() if retrain else None
        data._retrain_season() if retrain else None
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
        print(title + nl + self._label_long + nl + study._label_long)
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

    def simulate(self, trend = 2, season = None, noise = 0.1):
        season = generate_season(season, self._values.delta / 3, self.l, trend, 2) if season is not None else zero(self.l)
        trend = generate_trend(self._values.mean, self._values.delta, self.l, trend, 2)
        signal = trend + season
        noise = generate_noise(0, noise * np.mean(signal), self.l)
        self.set(signal + noise)
        return self

    def white(self):
        self._values.white()
        self._update_quality()
        return self
        

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
