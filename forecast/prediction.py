from forecast.backup import copy_class
import pandas as pd
import forecast.tools as tl
from forecast.predictor import *

class prediction_class(copy_class, total_predictor_class):
    def __init__(self):
        self.zero()
        
    def zero(self):
        self.set_function()
        self.set_data()
        total_predictor_class.zero(self)

    def set_function(self, function = None):
        self.function = function if function is not None else tl.none_function

    def set_data(self, data = None):
        self.data = tl.np.array(data) if data is not None else None

    def update_function(self):
        self.set_function(self.get_function())

    def update_data(self, time):
        data = self.predict(time)
        self.set_data(data)
        
    def update(self, time):
        self.update_active()
        self.update_function()
        self.update_data(time)
        self.update_label()

    def predict(self, time):
        return self.function(time)

    def get_data(self):
        return self.data if self.data is not None else 0

    def project(self, time):
        new = self.copy()
        new.update(time)
        #new.update_label()
        return new
    
    def __mul__(self, constant):
        new = self.copy()
        data = None if self.data is None else self.data * constant
        new.set_data(data)
        self.predictors = [pred * constant for pred in self.predictors]
        new.update_function()
        return new
