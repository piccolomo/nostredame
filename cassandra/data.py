from cassandra.backup import backup_class, copy_class
from cassandra.values import values_class
from cassandra.background import background_class, np
from cassandra.quality import quality_class
from cassandra.string import enclose_circled, enclose_squared
from cassandra.file import join_paths, add_extension, write_text, output_folder, create_folder
import matplotlib.pyplot as plt

#plt.ioff()
import matplotlib
matplotlib.use('GTK3Agg')  # or another backend ('Qt5Agg', 'WXAgg', etc.)

#['GTK3Agg', 'GTK3Cairo', 'GTK4Agg', 'GTK4Cairo', 'MacOSX', 'nbAgg', 'QtAgg', 'QtCairo', 'Qt5Agg', 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']

class data_class(backup_class):
    def __init__(self, time, values):
        self.set_name()
        self.set_unit()
        self.set_data(time, values)
        self.update_length()
        self.background = background_class()
        self.quality = quality_class(self.values.digits)
        self.update()
        backup_class.__init__(self)
        

    def set_name(self, name = None, surname = None):
        self.name = name
        self.surname = surname
        return self

    def get_name(self):
        return self.name if self.name is not None else ''
    
    def get_surname(self):
        return self.surname if self.surname is not None else ''

    def set_unit(self, unit = None):
        self.unit = unit
        return self

    def get_unit(self):
        return enclose_squared(self.unit) if self.unit is not None else ''


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


    def find_trend(self, method = 'test', order = 5, log = False, set = True):
        trend = self.background.find_trend(self, method, order, log)
        self.fit_trend(trend) if set and trend is not None else None
        return trend

    def find_seasons(self, threshold = 0, detrend = 3, log = False, set = True):
        periods = self.background.find_seasons(self, threshold, detrend, log)
        self.fit_seasons(*periods) if set and periods is not None else None
        return periods

    def find_es(self, method = 'data', depth = 1, log = False, set = True):
        es = self.background.find_es(self, method, depth, log)
        self.fit_es(es) if set and es is not None else None
        return es

    def find_all(self, log = True):
        return self.background.find_all(self, log)

    def auto(self, trend = True, seasons = True, es = True, log = True, save = False):
        self.zero_background()
        self.find_trend(log = log) if trend else None
        self.find_seasons(threshold = 1, log = log) if seasons else None
        self.find_es(log = log) if es else None
        self.log() if log else None
        self.save() if save else None
        

    def fit_trend(self, order = None):
        self.background.fit_trend(self, order)
        self.update()
        return self
    
    def get_trend(self):
        return self.background.get_trend()
    
    def fit_seasons(self, *periods):
        self.background.fit_seasons(self, periods)
        self.update()
        return self

    def get_season(self):
        return self.background.get_season()
    
    def get_treason(self):
        return self.background.get_treason()
    
    def fit_es(self, period):
        self.background.fit_es(self, period)
        self.update()
        return self

    def fit_naive(self, level = 'mean'):
        self.background.fit_naive(self, level)
        self.update()
        return self

    def get_prediction(self):
        return self.background.get_prediction()

    
    def retrain_background(self):
        self.background.retrain(self)
        return self

    def zero_background(self):
        self.background.zero()
        return self

    def get_background(self):
        return self.background.get_total()
        

    def update_quality(self):
        self.quality.set(self.get_data(), self.get_background())
        self.quality.update_label()
        return self

    
    def update_label(self):
        quality = self.quality.label if self.quality.label is not None else ''
        background = self.background.label if self.background.label is not None else 'No Background'
        label = self.get_name().title() + ' ' + self.get_surname()
        label = label.ljust(20 + 15) + ' | '
        label += quality + ' | '
        label += background 
        self.label = label
        self.logger = ''
        return self

    def update(self):
        self.background.update_label()
        self.update_quality()
        self.update_label()
        self.update_error()
        return self

    def log(self):
        self.update()
        self.print_split()

    def print_split(self):
        self.print()
        train, test = self.split(retrain = True);
        D = train.append(test); D.set_name(self.get_name(), 'Train + Test'); D.update();
        D.print()
        train.print()
        test.print()
        self.logger = '\n'.join([self.label, train.label, test.label])
        return self

    def print(self):
        print(self.label)


    def plot(self, width = 15, font_size = 1, lw = 1): # color_data = "navy", color_back = 'darkorchid'
        height = 9 / 16 * width; font_size = round(font_size * width / 1.1); lw = lw * width / 15
        color_back = 'goldenrod'
        plt.clf(); plt.close(); plt.pause(0.01); plt.rcParams.update({'font.size': font_size, "font.family": "sans-serif", 'toolbar': 'None'})
        plt.figure(figsize = (width, height)); plt.style.use(plt.style.available[-2])
        time, data, back, err = self.time.datetime, self.get_data(), self.get_background(), self.error
        plt.plot(time, self.get_data(), label = self.get_name().title(), lw = lw)
        plt.plot(time, back, label = self.background.label, lw = lw, color = color_back) if back is not None else None
        plt.fill_between(time, back - err, back + err, alpha = 0.1, color = color_back, lw = 0) if back is not None and err is not None else None
        ylabel = self.get_name().title() + self.get_surname() + self.get_unit()
        plt.title(self.get_name().title() + self.get_surname()); plt.ylabel(ylabel)
        plt.legend(); plt.tight_layout(); plt.pause(0.01); plt.show(block = 0)
        return self

    def save(self, log = True):
        path = join_paths(self.get_folder(), 'data.csv')
        extended = self.extend()
        data = [extended.time.data, extended.get_data()]
        background = extended.get_background()
        data = data if background is None else data + [background]
        data = np.transpose(data)
        text = '\n'.join([','.join(line) for line in data])
        write_text(path, text)
        print("data saved in", path) if log else None
        path = join_paths(self.get_folder(), 'plot.jpg')
        extended.plot();  plt.savefig(path); plt.pause(0.1);  plt.close();
        print("plot saved in", path) if log else None
        path = join_paths(self.get_folder(), 'log.txt')
        write_text(path, self.logger)
        print("log saved in", path) if log else None

    
    
    def forecast(self):
        time = self.time.forecast(self.length_forecast)
        data = self.project(time)
        data.background = self.project_background(time)
        data.set_name(self.name, "Forecasted" + enclose_circled(self.length_forecast))
        data.set_unit(self.unit)
        data.update()
        data.set_error(self.get_forecast_error())
        return data

    def extend(self):
        time = self.time.extend(self.length_forecast)
        data = self.project(time)
        data.background = self.project_background(time)
        data.set_name(self.name, "Extended" + enclose_circled(self.length_forecast))
        data.set_unit(self.unit)
        data.update()
        forecast_error = self.get_forecast_error()
        error = np.concatenate([self.error, forecast_error]) if self.error is not None and forecast_error is not None else None
        data.set_error(error)
        return data
    
    def split(self, test_length = None, retrain = False):
        test_length = round(test_length * self.length) if test_length is not None and test_length < 1 else test_length
        train_length = self.length_train if test_length is None else self.length - test_length
        
        train = self.part(0, train_length);
        train.retrain_background() if retrain else None

        test_time = self.time.part(train_length, self.length)
        test = self.project(test_time)
        test.background = train.project_background(test.time) #if retrain 

        train.set_name(self.name, "Train"); train.set_unit(self.unit)
        test.set_name(self.name, "Test"); test.set_unit(self.unit)
        train.update(); test.update()
        return train, test

    def part(self, begin, end):
        time = self.time.part(begin, end)
        data = self.project(time)
        data.background = self.background.part(begin, end)
        surname = '[{0}:{1}]'.format(begin, end)
        data.set_name(self.name, self.surname)
        data.set_unit(self.unit)
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
        new.set_name(self.get_name(), ".append(" + data.get_name() + ')')
        new.set_unit(self.unit)
        new.update()
        return new

    def copy(self):
        new = data_class(self.time.copy(), self.values.copy())
        new.set_name(self.name)
        new.set_unit(self.unit)
        new.set_forecast_length(self.length_forecast)
        new.background = self.background.copy()
        new.quality = self.quality.copy()
        new.update()
        return new

    
    def get_folder(self):
        name = self.name.lower().replace(' ', '-')
        folder = join_paths(output_folder, name)
        create_folder(folder)
        return folder

    def add(self, array):
        new = self.copy()
        new.values.add(array)
        return new

    def sub(self, array):
        return self.add(-array)

    def __repr__(self):
        return self.label

    def __len__(self):
        return self.length

    def set_error(self, error = None):
        self.error = error

    def update_error(self):
        error = np.full(self.length, self.quality.rms) if self.quality.rms is not None else None
        self.set_error(error)

    def get_forecast_error(self):
        data = self.copy()
        T, t = data.split(retrain = True)
        e0 = data.quality.rms
        e1 = t.quality.rms
        return np.array([e1] * data.length_forecast)
        #return np.linspace(e0, max(e1, e0), data.length_forecast) if e0 is not None and e1 is not None else None
        #return np.linspace(e0, e0 * (1 + (t.length_forecast / data.length)**0.1), data.length_forecast) if e0 is not None and e1 is not None else None
        #return e0 * np.exp(np.arange(data.length_forecast) * (t.length_forecast / data.length)) if e0 is not None and e1 is not None else None
