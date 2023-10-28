from cassandra.backup import backup_class, copy_class
from cassandra.values import values_class
from cassandra.trend import trend_class, np
from cassandra.season import season_class
from cassandra.prediction import prediction_class
from cassandra.quality import quality_class
from cassandra.string import enclose_circled, enclose_squared
from cassandra.list import find_seasons
from cassandra.file import join_paths, add_extension, write_text, output_folder
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('GTK3Agg')
# GTK3Agg, GTK3Cairo, GTK4Agg, GTK4Cairo, MacOSX, nbAgg, QtAgg, QtCairo, TkAgg, TkCairo, WebAgg, WX, WXAgg, WXCairo, Qt5Agg, Qt5Cairo


# from cassandra.plot import plot_class
# from cassandra.quality import quality_class, is_like_list
# from cassandra.values import values_class
# from cassandra.study import study_class
# from cassandra.best import find_best_class
# from cassandra.time import time_class

# from cassandra.path import read_table, correct_path, join_paths, output_folder
# from cassandra.dictionary import dictionary
# from .platform import platform, set_screen_default_size

# import pandas as pd
# import numpy as np

class data_class(copy_class, backup_class):
    def __init__(self, time, values):
        self.set_name()
        self.set_unit()
        
        self.set_data(time, values)
        self.update_length()
        
        self.trend = trend_class()
        self.season = season_class()
        self.prediction = prediction_class()

        self.quality = quality_class()
        
        self.update_label()
        backup_class.__init__(self)
        

    def set_name(self, name = 'Data'):
        self.name = name
        return self

    def set_unit(self, unit = ''):
        self.unit = unit
        return self


    def set_data(self, time, values):
        self.time = time.copy()
        self.values = values.copy()

    def update_length(self):
        self.length = self.values.length
        self.length_forecast = round(0.2 * self.length)
        self.length_test = round(self.length_forecast / (self.length + self.length_forecast) * self.length)
        self.length_train = self.length - self.length_test


    def find_seasons(self, threshold = 1, detrend = 2, log = True):
        return find_seasons(self.get_data(), threshold, detrend, log)
        
    



    def set_trend(self, order = None):
        self.trend.fit(self, order)
        return self

    def zero_trend(self):
        self.trend.zero()
        return self


    def set_season(self, *seasons, detrend = None):
        self.season.fit(self, seasons, detrend)
        return self

    def zero_season(self):
        self.season.zero()
        return self


    def set_predictor(self, name, dictionary):
        self.prediction.set_predictor(name, dictionary)
        residuals = data_class(self.time, values_class(self.get_residuals()))
        self.prediction.fit(residuals)
        return self

    def set_naive(self, level = 'mean'):
        self.set_predictor("naive", {'level': level})
        return self
     
    def set_es(self, period):
        self.set_predictor("es", {"seasonal_periods": period, "seasonal": "add"})
        return self
     
    def zero_prediction(self):
        self.prediction.zero()
        return self

    def zero_background(self):
        self.zero_trend()
        self.zero_season()
        self.zero_prediction()
        return self


    def set_quality_function(self, name):
        self.quality.set_function(name)
        return self

    def update_quality(self):
        self.quality.set(self.get_data(), self.get_background())
        self.quality.update_label()
        return self

    def get_quality(self):
        #self.update_quality()
        return self.quality.quality


    def log(self):
        self.update_label()
        print('----' + self.name.title() + '----')
        print(self.trend.label)
        print(self.season.label)
        print(self.prediction.label)
        print(self.quality.label)
        return self


    def get_data(self):
        return self.values.data
    
    def get_trend(self):
        trend = self.trend.data
        return trend if trend is not None else np.zeros(self.length)

    def get_season(self):
        season = self.season.data
        return season if season is not None else np.zeros(self.length)

    def get_prediction(self):
        prediction = self.prediction.data
        return prediction if prediction is not None else np.zeros(self.length)

    def get_treason(self):
        return self.get_trend() + self.get_season()

    def get_residuals(self):
        return self.get_data() - self.get_treason()

    def get_background(self):
        return self.get_treason() + self.get_prediction()

    
    def update_label(self):
        self.trend.update_label()
        self.season.update_label()
        self.prediction.update_label()
        self.update_quality()
        labels = [self.trend.label, self.season.label, self.prediction.label]
        self.label = ' + '.join([l for l in labels if l is not None])
        
    def get_ylabel(self):
        name = self.name.title()
        name = name if self.unit == '' else name + ' ' + enclose_squared(self.unit)
        return name
    

    def plot(self, width = 15, font_size = 1, block = 0):
        self.update_label()
        height = 9/ 16 * width; font_size = round(font_size * width / 1.1)
        plt.clf(); plt.close(); plt.pause(0.01);
        plt.rcParams.update({'font.size': font_size, "font.family": "sans-serif", 'toolbar': 'None'})
        plt.figure(figsize = (width, height)); plt.style.use(plt.style.available[-2])
        plt.plot(self.time.datetime, self.get_data(), label = self.name.title())
        plt.plot(self.time.datetime, self.get_background(), label = self.label)
        plt.title(self.name.title()); plt.ylabel(self.get_ylabel())
        plt.legend(); plt.tight_layout(); plt.pause(0.01); plt.show(block = block)
        return self

    
    def forecast(self, length = None):
        length = self.length_forecast if length is None else length
        time = self.time.forecast(length)
        values = self.values.forecast(length)
        data = data_class(time, values)
        self.project(data)
        data.name = self.name + " forecasted" + enclose_circled(length)
        data.unit = self.unit
        return data    
        
    def extend(self, length = None):
        forecast = self.forecast(length)
        data = self.append(forecast)
        data.name = self.name + " extended" + enclose_circled(length)
        data.unit = self.unit
        return data

    def project(self, data, retrain = False):
        data.trend = self.trend.project(data.time)
        data.season = self.season.project(data.time)
        data.prediction = self.prediction.project(data.time)
        data.update_label()
        # data.update_quality()

    def append(self, data):
        time = self.time.append(data.time)
        values = self.values.append(data.values)
        data = data_class(time, values)
        self.project(data)
        data.set_name(self.name + " + " + data.name)
        data.unit = self.unit 
        return data


    def save(self, log = True):
        path = self.get_path()
        path_back = add_extension(path, 'csv')
        path_plot = add_extension(path, 'jpg')
        background = np.transpose([self.time.data, self.get_background()])
        background = '\n'.join([','.join(el) for el in background])
        write_text(path_back, background)
        print("background saved in", path_back) if log else None
        self.plot(block = 0); plt.savefig(path_plot); plt.pause(0.01); plt.close();
        print("plot saved in", path_plot) if log else None
        return self

    def get_path(self):
        name = self.name.lower().replace(' ', '-')
        return join_paths(output_folder, name)
        

    
    def __mul__(self, constant):
        data = self.copy()
        data.trend = self.trend * constant
        data.season = self_season * constant
        data.prediction = self.prediction * constant
        data.set(self.time, self.values * constant)
        return data

    def __truediv__(self, constant):
        return self * (1 / constant)



#     def smooth(self, length):
#         return self.set(moving_average(self.get_data(), length))

#     def simulate(self, trend = 2, season = None, noise = 0.1):
#         season = generate_season(season, self._values.delta / 3, self.l, trend, 2) if season is not None else zero(self.l)
#         trend = generate_trend(self._values.mean, self._values.delta, self.l, trend, 2)
#         signal = trend + season




        
        
#         return self
        
#     def _fit_trend(self, order = None):
#         #order = self._trend.order if order is None else order
#         self._trend.fit(self._time, self._values, order)

#     def _update_trend_data(self):
#         self._trend.update_data(self._time)

#     def _retrain_trend(self):
#         self.update_trend(self._trend.order)




#     def get_trend_dataframe(self):
#         return pd.DataFrame(index = self._time.datetime_pandas, data = {'values': self.get_trend()})

#     def _get_path(self, name):
#         name = name if name is not None else self.name if self.name is not None else "data"
#         name = name.lower().replace(' ', '-')
#         path = join_paths(output_folder, name)
#         return correct_path(path)

    
    
        


    


#     def get_time(self):
#         return self._time.datetime

    



#     def get_data(self):
#         return self._values.data

#     def get_dataframe(self):
#         return pd.DataFrame(index = self._time.datetime_pandas, data = {'values': self.get_data()})

    


        



    


#     def _update_season_data(self):
#         self._season.update_data(self._time)
#         self._update_quality()

#     def _retrain_season(self):
#         self.update_season(*self._season.periods, detrend = self._season.order)

#     def get_season(self):
#         season = self._season.get_data()
#         return season if is_like_list(season) else np.array([season] * self.length)

#     def get_season_dataframe(self):
#         return pd.DataFrame(index = self._time.datetime_pandas, data = {'values': self.get_season()})
    
    
#     def correct_detrend_order(self, detrend = None):
#         trend_order = self._trend.order
#         return None if detrend is None and trend_order is None else trend_order + 1 if detrend is None and trend_order is not None else detrend


    





#     def update_prediction(self):
#         self._fit_predictors()
#         self._update_prediction_data()
#         return self

#     def _fit_predictors(self):
#         residuals = values_class(self.get_residuals())
#         self._prediction.fit(self._time, residuals)
#         return self

#     def _update_prediction_data(self):
#         self._prediction.update(self._time)




#     def get_prediction_dataframe(self):
#         return pd.DataFrame(index = self._time.datetime_pandas, data = {'values': self.get_prediction()})

        

        


#     def save_all(self, log = True):
#         self.forecast().plot().save_plot(log = log).save_background(log = log)
#         self.extend().plot().save_plot(log = log)
#         return self
    

    
#     def auto(self, trend = True, season = True, prediction = True, log = True, save = True):
#         self.zero_background()
#         self.find_trend(log = log) if isinstance(trend, bool) and trend else self.update_trend(trend) if not isinstance(trend, bool) and isinstance(trend, int) else self.update_trend(None)
        
#         season = [season] if isinstance(season, int) and not isinstance(season, bool) else season
#         self.find_seasons(threshold = 2.7, log = log, apply_result = True) if isinstance(season, bool) and season else self.update_season(*season) if not isinstance(season, bool) and isinstance(season, list) else self.update_season()

#         if isinstance(prediction, bool) and prediction:
#             self.find_es(self.all_seasons(threshold = 1.0), log = log)
            
#         elif not isinstance(prediction, bool) and isinstance(prediction, int): 
#             self.add_es(prediction)
            
#         elif isinstance(prediction, str):
#             self.find_es(self.all_seasons(threshold = 1.0), log = log)
#         else:
#             self.zero_prediction()
        
#         self.log() if log else None
#         self.save_all(log = log) if save else None 


        
    
#     def get_treason_dataframe(self):
#         return pd.DataFrame(index = self._time.datetime_pandas, data = {'values': self.get_treason()})

    
        
#     def get_background_dataframe(self):
#         return pd.DataFrame(index = self._time.datetime_pandas, data = {'values': self.get_background()})
    
#     def save_background(self, name = None, log = True):
#         path = self._get_path(name) + ".csv"
#         self.get_background_dataframe().to_csv(path_or_buf = path, header = False)
#         print("background saved in", path) if log else None
#         return self



        

    
#     def _update_quality(self):
#         y_true, y_pred = self.get_data(), self.get_background()
#         self._quality.update(y_true, y_pred)
#         return self._quality


    
#     def _update_label(self):
#         self._trend.update_label(); self._season.update_label(); self._prediction.update_label();
#         self._update_label_short()
#         self._update_label_long()
        
#     def _update_label_short(self):
#         labels = [self._trend.label_short, self._season.label_short, self._prediction.label_short]
#         labels = [str(el) for el in labels if el is not None]
#         no_label = len(labels) == 0
#         self._label_short = "No Background" if no_label else ' + '.join(labels)
#         self._residuals_label = self.get_name().lower() if no_label else self.get_name() + ' - background'

#     def _update_label_long(self):
#         labels = [self._trend.label_long, self._season.label_long, self._prediction.label_long]
#         labels = [str(el) for el in labels if el is not None]
#         no_label = len(labels) == 0
#         self._label_long = "No Background" if no_label else nl.join(labels)

#     def log(self, test_length = None):
#         self._update_label()
#         self._update_quality()
#         name = "data" if self.name is None else self.name
#         title = bold(self.get_name() + " Log")
#         study = study_class(self, test_length)
#         print(title + nl + self._label_long + nl + study._label_long)
#         return self

#     def set(self, data):
#         data = data if is_like_list(data) else [data] * self.length
#         self._values.set(data)
#         self._update_quality()
#         return self

#     def white(self):
#         self._values.white()
#         self._update_quality()
#         return self
        

#     def part(self, begin, end, retrain = False):
#         time = self._time.part(begin, end)
#         values = self._values.part(begin, end)
#         data = data_class(time, values)
#         self._project_background_to(data, retrain)
#         return data

#     def split(self, test_length = None, retrain = False):
#         test_length = self.test_length if test_length is None else test_length
#         test_length = ratio_to_length(test_length, self.length)
#         train_length = self.length - test_length
#         train, test = self.part(0, train_length, retrain), self.part(train_length, self.length)
#         train._project_background_to(test, retrain = False) if retrain else None
#         train.set_name(self.get_name() + " train")
#         test.set_name(self.get_name() + " test")
#         train.set_unit(self.unit)
#         test.set_unit(self.unit)
#         return train, test


    
# # Data Utils
# is_zero = lambda data: (is_like_list(data) and all(np.array(data) == 0)) or (not is_like_list(data) and data == 0)

# generate_noise = lambda mean, amplitude, length: np.random.normal(0, amplitude , length)
# ratio_to_length = lambda ratio, length: length if ratio is None else round(ratio * length) if ratio <= 1 else int(ratio)

# def moving_average(data, length = 1):
#     l = len(data)
#     left_half = length // 2
#     right_half = (length + 1) // 2
#     window = lambda i: range(max(i - left_half, 0) , min(i + right_half, l))
#     return [np.mean([data[j] for j in window(i)]) for i in range(l)]
