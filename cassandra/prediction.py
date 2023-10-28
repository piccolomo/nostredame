from statsmodels.tools.sm_exceptions import ConvergenceWarning, SpecificationWarning, ValueWarning
from statsmodels.tsa.holtwinters import ExponentialSmoothing as ES
from cassandra.string import dictionary_to_string
from cassandra.backup import copy_class
import warnings
warnings.simplefilter('ignore', ConvergenceWarning)

import numpy as np

class prediction_class(copy_class):
    def __init__(self):
        self.zero()
        
    def zero(self):
        self.predictor = None
        self.set_function()
        self.set_data()
        self.update_label()
        
    def set_function(self, function = None):
        self.predictor.set_function(function) if self.predictor is not None else None

    def set_data(self, data = None):
        self.data = None if data is None else np.array(data)

    def update_label(self):
        self.predictor.update_label() if self.predictor is not None else None


    def set_predictor(self, name, dictionary):
        self.predictor = naive_predictor(dictionary) if name == "naive" else es_predictor(dictionary) if name == "es" else None
        print("Incorrect Model") if name not in ['es', 'naive'] else None

    def fit(self, data):
        self.predictor.fit(data) if self.predictor is not None else None
        self.update_data(data.time)
        self.update_label()

    def update_data(self, time):
        data = self.predict(time)
        self.set_data(data)

    def predict(self, time):
        return self.predictor.function(time) if self.predictor is not None else None

    def update_label(self):
        self.predictor.update_label() if self.predictor is not None else None
        self.label = self.predictor.label if self.predictor is not None else None
    
    def project(self, time):
        new = self.copy()
        new.update_data(time)
        return new

    def __mul__(self, constant):
        new = self.copy()
        data = None if self.data is None else self.data * constant
        new.set_data(data)
        new.predictor = None if self.predictor is None else self.predictor * constant
        return new

        
class predictor_class(copy_class):
    def __init__(self, name, dictionary):
        self.set_name(name)
        self.set_dictionary(dictionary)
        self.set_function()
        self.set_status()
        self.update_label()

    def set_name(self, name):
        self.name = name

    def set_dictionary(self, dictionary):
        self.dictionary = dictionary
        
    def set_function(self, function = None):
        self.function = function
        
    def set_status(self, status = 0):
        self.status = status # -1 = Failed, 0 = Non Fitted, 1 = Fitted

    def update_label(self):
        status = "Failed " if self.status == -1 else "Not-Fitted-" if self.status == 0 else ''
        self.label = status + self.name.title() + dictionary_to_string(self.dictionary)
        
    def __mul__(self, constant):
        new = self.copy()
        new.set_function(lambda el: self.function(el) * constant)
        return new

    
class naive_predictor(predictor_class):
    def __init__(self, dictionary):
        predictor_class.__init__(self, "naive", dictionary)

    def fit(self, data):
        level = self.dictionary["level"]
        level = 0 if level == "zero" else data.values.mean if level == "mean" else data.values.last if level == "last" else data.values.first if level == "first" else level
        dictionary = {"level": level}
        function = lambda time: np.full(time.length, 0) + level
        self.set_function(function)
        self.set_status(1)

        
class es_predictor(predictor_class):
    def __init__(self, dictionary):
        predictor_class.__init__(self, "exponential-smoothing", dictionary)

    def fit(self, data):
        try:
            model = ES(endog = data.values.data, **self.dictionary)
            fit = model.fit()
            function = lambda time: fit.predict(time.index[0], time.index[-1])
            self.set_function(function)
            self.set_status(1)
        except (TypeError, ValueWarning, ConvergenceWarning, ValueError):
            print("Carefull!")
            self.set_status(-1)


