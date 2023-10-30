from cassandra.backup import backup_class, copy_class
from cassandra.values import values_class
from cassandra.background import background_class, np
from cassandra.quality import quality_class
from cassandra.string import enclose_circled, enclose_squared
from cassandra.file import join_paths, add_extension, write_text, output_folder
import matplotlib.pyplot as plt

import matplotlib
#matplotlib.use('GTK3Agg')


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
        self.set_forecast_length(round(0.2 * self.length))

    def set_forecast_length(self, length):
        self.length_forecast = length
        self.length_test = round(self.length_forecast / (self.length + self.length_forecast) * self.length)
        self.length_train = self.length - self.length_test


    def find_trend(self, log = False, set = True):
        trend = self.background.find_trend(self, log)
        self.fit_trend(trend) if set else None
        return trend

    def find_seasons(self, threshold = 1, detrend = 3, log = False, set = True):
        periods = self.background.find_seasons(self, threshold, detrend, log)
        self.fit_seasons(*periods[:3]) if set else None
        return periods

    def find_es(self, log = False, set = True):
        es = self.background.find_es(self, log)
        self.fit_es(es) if set else None
        return es

    def find_all(self, log = True):
        return self.background.find_all(self, log)

    def auto(self, trend = True, seasons = True, es = True, log = True):
        self.zero_background()
        self.find_trend() if trend else None
        self.find_seasons() if seasons else None
        self.find_es() if es else None
        self.log() if log else None
        self.log_split() if log else None
        self.save(log = log)
        #self.extend().plot() if log else None
        

        
    def fit_trend(self, order = None):
        self.background.fit_trend(self, order)
        self.update_quality()
        return self
    
    def fit_seasons(self, *periods):
        self.background.fit_seasons(self, periods)
        self.update_quality()
        return self

    def fit_naive(self, level = 'mean'):
        self.background.fit_naive(self, level)
        self.update_quality()
        return self
     
    def fit_es(self, period):
        self.background.fit_es(self, period)
        self.update_quality()
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
        label = self.name.upper()
        label = (label + ' | ' + self.quality.label) if self.quality.label is not None else label
        self.label = (label + ' | ' + self.background.label) if self.background.label is not None else label
    
    def update_quality(self):
        self.quality.set(self.get_data(), self.get_background())
        self.quality.update_label()
        return self
    

    def log_data(self):
        self.update_label()
        print(self.label)
        return self

    def log_split(self):
        train, test = self.split(retrain = True)
        #train.log()
        test.log_data()
        return self

    def log(self):
        self.log_data()
        self.log_split()
        print()
        return self


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
        extended = self.extend()
        background = extended.get_background()
        background = np.zeros(extended.length) * np.nan if background is None else background
        background = np.transpose([extended.time.data, extended.get_data(), background])
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


    def get_ylabel(self):
        name = self.name.title()
        name = name if self.unit == '' else name + ' ' + enclose_squared(self.unit)
        return name

    def get_path(self):
        name = self.name.lower().replace(' ', '-')
        return join_paths(output_folder, name)


    # def __add__(self, data):
    #     new = data.copy()
    #     new.values += data.values
    #     return new

    # def __sub__(self, data):
    #     new = data.copy()
    #     return new

    def add(self, array):
        new = self.copy()
        new.values.add(array)
        return new

    def sub(self, array):
        return self.add(-array)
