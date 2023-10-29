from cassandra.backup import backup_class, copy_class
from cassandra.values import values_class
from cassandra.background import background_class, np
from cassandra.quality import quality_class
from cassandra.string import enclose_circled, enclose_squared
from cassandra.file import join_paths, add_extension, write_text, output_folder
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('GTK3Agg')

# import numpy as np

class data_class(backup_class):
    def __init__(self, time, values):
        self.set_name()
        self.set_unit()
        self.set_data(time, values)
        self.update_length()
        self.background = background_class()
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

    def get_data(self):
        return self.values.data

    def update_length(self):
        self.length = self.values.length
        self.length_forecast = round(0.2 * self.length)
        self.length_test = round(self.length_forecast / (self.length + self.length_forecast) * self.length)
        self.length_train = self.length - self.length_test
        

    def find_trend(self, log = True):
        return self.background.find_trend(self, log)
        
    def fit_trend(self, order = None):
        self.background.fit_trend(self, order)
        return self
    
    def find_seasons(self, threshold = 1, log = True):
        return self.background.find_seasons(self, threshold, log)
    
    def fit_season(self, *periods):
        self.background.fit_season(self, periods)
        return self

    def fit_naive(self, level = 'mean'):
        self.background.prediction.set_naive(level)
        self.background.fit_predictor(self)
        return self
     
    def fit_es(self, period):
        self.background.prediction.set_es(period)
        self.background.fit_predictor(self)
        return self

    
    def retrain_background(self):
        self.background.retrain(self)
        return self

    def zero_background(self):
        self.background.zero()
        return self

    def get_background(self):
        return self.background.get_total()

    def get_trend(self):
        return self.background.get_trend()
    
    def get_season(self):
        return self.background.get_season()
    
    def get_treason(self):
        return self.background.get_treason()
    
    def get_prediction(self):
        return self.background.get_prediction()


    def update_label(self):
        self.background.update_label()
        self.update_quality()
        
    
    def update_quality(self):
        self.quality.set(self.get_data(), self.get_background())
        self.quality.update_label()
        return self
    
    def set_quality_function(self, name):
        self.quality.set_function(name)
        return self

    def get_quality(self):
        #self.update_quality()
        return self.quality.quality


    def log(self):
        self.update_label()
        out = self.name.upper()
        out = (out + ': ' + self.background.label + ': ' + self.quality.label) if self.background.label != '' else out
        print(out)


    def plot(self, width = 15, font_size = 1, block = 0):
        self.update_label()
        height = 9/ 16 * width; font_size = round(font_size * width / 1.1)
        plt.clf(); plt.close(); plt.pause(0.01);
        plt.rcParams.update({'font.size': font_size, "font.family": "sans-serif", 'toolbar': 'None'})
        plt.figure(figsize = (width, height)); plt.style.use(plt.style.available[-2])
        plt.plot(self.time.datetime, self.get_data(), label = self.name.title())
        back = self.get_background()
        plt.plot(self.time.datetime, back, label = self.background.label) if back is not None else None
        plt.title(self.name.title()); plt.ylabel(self.get_ylabel())
        plt.legend(); plt.tight_layout(); plt.pause(0.01); plt.show(block = block)
        return self

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
    
    
    def forecast(self):
        time = self.time.forecast(self.length_forecast)
        data = self.project(time)
        data.background = self.project_background(time)
        data.name = self.name + " forecasted" + enclose_circled(self.length_forecast)
        data.unit = self.unit
        return data

    def extend(self):
        time = self.time.extend(self.length_forecast)
        data = self.project(time)
        data.background = self.project_background(time)
        data.name = self.name + " extended" + enclose_circled(self.length_forecast)
        data.unit = self.unit
        return data
    
    def split(self, test_length = None, retrain = False):
        train = self.part(0, self.length_train);
        train.retrain_background() if retrain else None

        test_time = self.time.part(self.length_train, self.length)
        test = self.project(test_time)
        test.background = train.project_background(test.time)

        train.name = self.name + " train"; train.set_unit(self.unit)
        test.name = self.name + " test"; test.set_unit(self.unit)
        return train, test

    def part(self, begin, end):
        time = self.time.part(begin, end)
        data = self.project(time)
        data.background = self.background.part(begin, end)
        data.name = self.name + '[{0}:{1}]'.format(begin, end)
        data.unit = self.unit
        return data

    def project(self, time):
        values = [self.values.data[i] if i in self.time.index else np.nan for i in time.index]
        new = data_class(time, values_class(values))
        new.quality = self.quality.copy()
        return new


    def project_background(self, time):
        return self.background.project(time)

    def append(self, data):
        time = self.time.append(data.time)
        values = self.values.append(data.values)
        new = data_class(time, values)
        new.background = self.background.append(data.background)
        new.set_name(self.name + " + " + data.name)
        new.unit = self.unit 
        return new

    def copy(self):
        new = data_class(self.time.copy(), self.values.copy())
        new.name = self.name
        new.unit = self.unit
        new.background = self.background.copy()
        new.quality = self.quality.copy()
        new.update_label()
        return new

  
    def __add__(self, constant):
        new = self.copy()
        new.values += constant
        return new
    
    def __sub__(self, constant):
        return self + (-constant)

    def __mul__(self, constant):
        new = self.copy()
        new.values *= constant
        return new

    def __truediv__(self, constant):
        return self * (1 / constant)


    def get_ylabel(self):
        name = self.name.title()
        name = name if self.unit == '' else name + ' ' + enclose_squared(self.unit)
        return name

    def get_path(self):
        name = self.name.lower().replace(' ', '-')
        return join_paths(output_folder, name)
        



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
