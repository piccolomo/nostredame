from cassandra.backup import copy_class
from cassandra.string import enclose_circled
from cassandra.list import get_trend_function, to_time_class_function
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
        self.function = function
        
    def set_data(self, data = []):
        self.data = np.array(data)

    def update_label(self):
        self.label = None if self.order is None else "Trend" + enclose_circled(self.order)


    def fit(self, data, order):
        self.fit_function(data, order)
        self.update_data(data.time)
        self.set_order(order)
        self.update_label()
        
    def fit_function(self, data, order):
        function = get_trend_function(data.time.index, data.values.data, order)
        self.set_function(to_time_class_function(function))
    
    def update_data(self, time):
        data = self.predict(time)
        self.set_data(data)

    def predict(self, time):
        return self.function(time)

    def get_data(self):
        return self.data

    def project(self, time):
        new = self.copy()
        new.update_data(time)
        return new

    def __mul__(self, constant):
        new = self.copy()
        data = None if self.data is None else self.data * constant
        function = function if self.function is None else (lambda el: self.function(el) * constant)
        new.set_data(data)
        new.set_function(function)
        return new




