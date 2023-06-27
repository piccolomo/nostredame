from forecast.backup import copy_class
from forecast.string import pad, enclose_circled
import numpy as np


class trend_class(copy_class):
    def __init__(self):
        self.zero()

    def zero(self):
        self.set_order()
        self.set_function()
        self.set_data()
        self.update_label()

    def set_order(self, order = None):
        self.order = order

    def set_function(self, function = None):
        self.function = function if function is not None else none_function
        
    def set_data(self, data = None):
        self.data = np.array(data) if data is not None else None

    def update_data(self, time):
        data = self.predict(time)
        self.set_data(data)

    def fit(self, time, values, order):
        self.fit_function(time, values, order)
        self.set_order(order)
        self.update_label()
        
    def fit_function(self, time, values, order):
        function = get_trend_function(time.index, values.data, order)
        self.set_function(to_time_function(function))

    def update_label(self):
        no_label = self.order is None
        self.update_label_short(no_label)
        self.update_label_long(no_label)
        
    def update_label_short(self, no_label):
        label = "Trend" + enclose_circled(self.order)
        self.label_short = None if no_label else label

    def update_label_long(self, no_label):
        label = pad("Trend", 11) + str(self.order)
        self.label_long = None if no_label else label


    def get_data(self):
        return self.data if self.data is not None else 0

    def predict(self, time):
        return self.function(time)

    def project(self, time):
        new = self.copy()
        new.update_data(time)
        #new.update_label()
        return new

        
    def __mul__(self, constant):
        new = self.copy()
        data = None if self.data is None else self.data * constant
        new.set_data(data)
        function = none_function if self.function == none_function else (lambda el: self.function(el) * constant)
        new.set_function(function)
        return new


# Trend Utilities
nan = np.nan
zero_function = lambda el: 0
none_function = lambda el: None
nan_function = lambda el: nan
to_time_function = lambda function: (lambda time: np.array([function(el) for el in time.index]))

def get_trend_function(x, y, order = 2):
    if order is None or order is nan or len(x) == 0:
        return zero_function
    try:
        poly = np.polyfit(x, y, deg = order)
        function = np.poly1d(poly)
        return function
    except (RuntimeWarning, np.RankWarning):
        return nan_function

def map_function(function, data):
    return np.array(list(map(function, data)))

def get_trend(data, order = 2):
    x = range(len(data))
    function = get_trend_function(x, data, order)
    return map_function(function, x)

remove_trend = lambda data, order = 2: data - get_trend(data, order)

def generate_trend(mean = 100, delta = 10, length = 1000, order = 2, noise = 1):
    y0 = mean - delta / 2
    d = abs(noise) * 4
    poly = np.random.normal(0, d, order - 1) if noise * order != 0 else [0] * (order - 1) 
    s = sum(poly)
    poly = [y0] + list(poly) + [delta - s]
    poly = [poly[i] / length ** i for i in range(order + 1)][ : : -1]
    return np.polyval(poly, range(length))
