from forecast.time import time_class
from forecast.plot import plot_data
from forecast.quality import quality_class, mean_quality
import forecast.tools as tl 
from forecast.backup import backup_class, copy_class
from forecast.season import season_class, trend_class
from forecast.season import season_class
from forecast.prediction import prediction_class
from forecast.values import values_class
import pandas as pd
from forecast.find import find_class
from forecast.study import study_class
from forecast.predictor import dictionary

# from forecast.split import split_class
# from forecast.backup import backup_class

def from_csv(path, delimiter = ' ', first_row = 0, length = None, time_col = 0, values_col = 1, form = "%d/%m/%Y"):
    last_row = first_row + length if length is not None else None
    matrix = tl.read_data(path, delimiter = delimiter)[first_row : last_row]
    data = tl.transpose(matrix)
    time = data[time_col]
    values = data[values_col]
    #values = [el * scale for el in values]
    time = time_class(time, form)
    values = values_class(values)
    data = data_class(time, values)
    return data

class data_class(plot_data, backup_class, copy_class, find_class):
    def __init__(self, time = [], values = []):
        self.set_name(); self.set_unit()
        
        self._set_time(time)
        self._set_values(values)
        self.set_forecast_length()
        
        self._trend = trend_class()
        self._season = season_class()
        self._prediction = prediction_class()
        self._update_label()

        self._quality = quality_class()
        self._update_quality()
        
        backup_class.__init__(self)

        
    def set_name(self, name = None):
        self.name = name
        self._residuals_label = self.name
        return self

    def get_name(self):
        return self.name.title() if self.name is not None else "Data"

    def get_unit(self, enclosed = False):
        return "" if self.unit is None else tl.enclose_squared(self.unit) if enclosed else self.unit

    def set_unit(self, unit = None):
        self.unit = unit
        return self
        
    def _set_time(self, time):
        self._time = time.copy()

    def _set_values(self, values):
        self._values = values.copy()
        self.length = self.l = self._values.length
        #self._values.sort(self._time.index_to_sort)

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
        
        
    def find_seasons(self, detrend = 2, source= "acf", log = True, plot = False, threshold = 1):
        return tl.find_seasons(self._values.data, detrend_order = detrend, source = source, log = log, plot = plot, threshold = threshold)
        #tl.plt.show(block = 0)

    def all_seasons(self, detrend = 2):
        acf = self.find_seasons(detrend = detrend, source = "acf", log = False, threshold = 1)
        fft = self.find_seasons(detrend = detrend, source = "fft", log = False, threshold = 1)
        return list(set(acf + fft))
        
    def update_season(self, *periods, detrend = None):
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

                
    def add_predictor(self, name, dictionary = None, weight = 1):
        self._prediction.add_predictor(name, dictionary, weight)

    def update_prediction(self):
        self._fit_predictors()
        self._update_prediction_data()

    def use_predictor(self, name, dictionary = None):
        self.zero_prediction()
        self.add_predictor(name, dictionary = dictionary)
        self.update_prediction()

    use_arima = lambda self, dictionary: self.use_predictor("arima", dictionary)
    use_es = lambda self, dictionary: self.use_predictor("es", dictionary)
    use_uc = lambda self, dictionary: self.use_predictor("uc", dictionary)
    use_prophet = lambda self, dictionary: self.use_predictor("prophet", dictionary)
    use_cubist = lambda self, dictionary: self.use_predictor("cubist", dictionary)
        
    def _fit_predictors(self):
        residuals = values_class(self.get_residuals())
        self._prediction.fit(self._time, residuals)
        return self

    def _update_prediction_data(self):
        self._prediction.update(self._time)
        self._update_quality()
        
    def zero_prediction(self):
        self._prediction.zero()

    def get_trend(self):
        trend = self._trend.get_data()
        return trend if tl.is_like_list(trend) else tl.np.array([trend] * self.length)

    def get_season(self):
        season = self._season.get_data()
        return season if tl.is_like_list(season) else tl.np.array([season] * self.length)
        
    def get_treason(self):
        return self.get_trend() + self.get_season()

    def get_background(self):
        yb = self.get_treason() + self._prediction.get_data()
        self.background_ok = not tl.is_zero(yb)
        return yb

    def get_background_dataframe(self):
        return pd.DataFrame(index = self._time.pandas_index, data = {'values': self.get_background()})

    def get_time(self):
        return self._time.datetime

    def get_data(self):
        return self._values.data

    def get_dataframe(self):
        return pd.DataFrame(index = self._time.pandas_index, data = {'values': self.get_data()})

    def zero_background(self):
        self.zero_trend()
        self.zero_season()
        self.zero_prediction()
    
    def get_residuals(self):
        return self.get_data() - self.get_treason()

        
    def _update_label(self):
        self._trend.update_label(); self._season.update_label(); self._prediction.update_label();
        self._update_short_label()
        self._update_long_label()
        
    def _update_short_label(self):
        labels = [self._trend.short_label, self._season.short_label, self._prediction.short_label]
        labels = [str(el) for el in labels if el is not None]
        no_label = len(labels) == 0
        self._short_label = "No Background" if no_label else ' + '.join(labels)
        residuals_label = self.get_name() + " - " + tl.enclose_circled(self._short_label)
        self._residuals_label = self.get_name() if no_label else residuals_label

    def _update_long_label(self):
        labels = [self._trend.long_label, self._season.long_label, self._prediction.long_label]
        labels = [str(el) for el in labels if el is not None]
        no_label = len(labels) == 0
        self._long_label = "No Background" if no_label else tl.nl.join(labels)
        
    def _update_quality(self):
        y_true, y_pred = self.get_data(), self.get_background()
        self._quality.update(y_true, y_pred)
        return self._quality

    def update(self):
        self._update_season_data()
        self._update_trend_data()
        self._update_prediction_data()
        self._update_label()
        self._update_quality()
    

    def _project_background_to(self, data, retrain = False):
        data._trend = self._trend.project(data._time)
        data._season = self._season.project(data._time)
        data._prediction = self._prediction.project(data._time)
        data.update_trend() if retrain else None
        data.update_season() if retrain else None
        data.update_prediction() if retrain else None
        data._update_label()
        data._update_quality()
        
    def smooth(self, length):
        return self.set(tl.moving_average(self.get_data(), length))

    def simulate(self, trend = 2, period = 12, noise = 0):
        noise = self._values.std if noise is None else noise
        trend = tl.generate_trend(self._values.mean, self._values.delta, self.l, trend, 1)
        season = tl.generate_season(period, self._values.delta / 3, self.l, 2, 1)
        noise = tl.generate_noise(0, noise, self.l)
        self.set(trend + season + noise)
        return self
        
    def forecast(self, length = None):
        length = self.forecast_length if length is None else length
        time = self._time.forecast(length)
        values = self._values.forecast(length)
        data = data_class(time, values)
        self._project_background_to(data)
        name = ' '.join([el for el in [self.name, "forecasted"] if el is not None])
        data.set_name(name)
        return data    
        
    def append(self, data):
        time = self._time.append(data._time)
        values = self._values.append(data._values)
        new = data_class(time, values)
        self._project_background_to(new)
        new.set_name(self.get_name() + " + " + data.get_name())
        return new

    def extend(self, length = None):
        length = self.forecast_length if length is None else length
        data = self.append(self.forecast(length))
        name = ' '.join([el for el in [self.name, "extended"] if el is not None])
        data.set_name(name)
        return data

    def part(self, begin, end, retrain = False):
        time = self._time.part(begin, end)
        values = self._values.part(begin, end)
        data = data_class(time, values)
        self._project_background_to(data, retrain)
        return data

    def split(self, test_length = None, retrain = False):
        test_length = self.test_length if test_length is None else test_length
        test_length = tl.ratio_to_length(test_length, self.length)
        train_length = self.length - test_length
        train, test = self.part(0, train_length, retrain), self.part(train_length, self.length)
        train._project_background_to(test, retrain = False) if retrain else None
        train.set_name(self.get_name() + " train")
        test.set_name(self.get_name() + " test")
        train.set_unit(self.unit)
        test.set_unit(self.unit)
        return train, test

    def log_split(self, test_length = None):
        train, test = self.split(test_length)
        study = study_class(self, train, test)
        study.log()

    def set(self, data):
        data = data if tl.is_like_list(data) else [data] * self.length
        self._values.set(data)
        self._update_quality()
        return self

    def white(self):
        self._values.white()
        self._update_quality()
    
    def __mul__(self, constant):
        new = self.copy()
        new._set_values(self._values * constant)
        new._trend = self._trend * constant
        new._season = self._season * constant
        new._prediction = self._prediction * constant
        return new#.update()

    def __truediv__(self, constant):
        return self * (1 / constant)

    def __str__(self):
        name = "data" if self.name is None else self.name
        title = tl.colorize(self.get_name() + " Log", "blue+", "bold")
        return title + tl.nl + self._long_label + tl.nl + str(self._quality)

    def log(self):
        self._update_label()
        self._update_quality()
        print(str(self))
        return self

    def _get_path(self, name):
        name = name if name is not None else self.name if self.name is not None else "data"
        path = tl.join_paths(tl.output_folder, name)
        return path

    def save_background(self, name = None):
        path = self._get_path(name) + ".csv"
        self.get_background_dataframe().to_csv(path_or_buf = path, header = False)


    def find_best(self, function_name, arguments, log = True):
        data = self.copy()
        results = []
        l = len(arguments)
        for i in range(l):
            argument = arguments[i]
            #train.zero_background()
            eval("data." + function_name + "(argument)")
            train, test = data.split(self.test_length, retrain = True)
            study = study_class(data, train, test)
            results.append([argument, study])
            tl.indicator(i + 1, l) if log else None

        results.sort(key = lambda el: el[1].quality)
        result = results[0][0] if len(results) > 0 else None

        if log and result is not None:
            arg_length = max([len(str(arg)) for arg in arguments])
            spaces = ' ' * (arg_length + 1)
            length_label = results[0][1].get_length_string()
            title = results[0][1]._short_label_title
            print(length_label)
            print("Function", tl.bold(function_name))
            print(spaces + title)
            [print(tl.pad(argument, arg_length), study._short_label) for (argument, study) in results]
            
        return result

    def find_trend(self, max_order = 10, log = True):
        arguments = list(range(0, max_order + 1))
        return self.find_best(function_name = "update_trend", arguments = arguments, log = log)

    def find_arima(self, periods = [], order = 1, log = True):
        arguments = dictionary.arima.all(periods, order)
        return self.find_best(function_name = "use_arima", arguments = arguments, log = log)

    def find_es(self, periods = [], log = True):
        arguments = dictionary.es.all(periods)
        return self.find_best(function_name = "use_es", arguments = arguments, log = log)

    def find_uc(self, periods = [], order = 1, log = True):
        arguments = dictionary.uc.all(periods, order)
        return self.find_best(function_name = "use_uc", arguments = arguments, log = log)

    def find_prophet(self, order = 10, log = True):
        arguments = dictionary.prophet.all(order)
        return self.find_best(function_name = "use_prophet", arguments = arguments, log = log)

    # def find_cubist(self, order = 10, log = True):
    #     arguments = dictionary.cubist.all(order)
    #     return self.find_best(function_name = "use_cubist", arguments = arguments, log = log)    
    
