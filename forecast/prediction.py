from forecast.backup import copy_class
from forecast.trend import none_function
from forecast.values import mean
from forecast.string import dictionary_to_string, enclose_circled, pad, platform

from statsmodels.tsa.statespace.structural import UnobservedComponents as UC
from statsmodels.tsa.holtwinters import ExponentialSmoothing as ES
from statsmodels.tsa.statespace.sarimax import SARIMAX as arima
from prophet import Prophet as prophet
from pmdarima.arima import auto_arima
if platform == "unix":
    from cubist import Cubist as cubist

from statsmodels.tools.sm_exceptions import ConvergenceWarning, SpecificationWarning, ValueWarning
from numpy.linalg import LinAlgError

import warnings
warnings.filterwarnings("error")
warnings.filterwarnings(action = "ignore", message = "unclosed", category = ResourceWarning)
warnings.filterwarnings(action = "ignore", category = ConvergenceWarning) # for a rare arima warning

import logging # to suppress prophet log
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").disabled = True

import numpy as np
import pandas as pd


class total_predictor_class():
    def __init__(self):
        self.zero()
        
    def zero(self):
        self.predictors = []
        self.weights = []
        self.update_active()
        self.update_label()

    def update_active(self):
        active_pos = [i for i in range(len(self.predictors)) if  self.predictors[i].status == 1]
        self.active_predictors = [self.predictors[i] for i in active_pos]
        self.active_weights = [self.weights[i] for i in active_pos]
        self.update_relative_weights()

    def update_relative_weights(self):
        total_weight = np.sum(self.active_weights)
        active_weights = [100 * el / total_weight for el in self.active_weights]
        constant_test = is_constant(self.active_weights)
        self.relative_weights = [str(round(el, 2)) + " % " if not constant_test else "" for el in active_weights]

    def update_label(self):
        self.update_labels()
        no_label = len(self.active_predictors) == 0
        self.update_label_short(no_label)
        self.update_label_long(no_label)
        
    def update_labels(self):
        [el.update_label() for el in self.predictors]
        
    def update_label_short(self, no_label):
        labels = [pred.label_short for pred in self.active_predictors]
        self.label_short = None if no_label else ' + '.join(labels)
    
    def update_label_long(self, no_label):
        l = len(self.active_predictors)
        labels = [pred.label_long for pred in self.active_predictors]
        labels = [self.relative_weights[i] + labels[i] for i in range(l)]
        self.label_long = None if no_label else pad('Predictor', 11) + ' + '.join(labels)

    def add_predictor(self, name, dictionary, weight):
        if weight == 0:
            return
        if name.lower() == "naive":
            predictor = naive_predictor(dictionary)
        elif name.lower() == "arima":
            predictor = arima_predictor(dictionary)
        elif name.lower() in ["auto arima", "auto_arima"]:
            predictor = auto_arima_predictor(dictionary)
        elif name.lower() in ["es", "exponential smoothing", "exponential", "smoothing"]:
            predictor = es_predictor(dictionary)
        elif name.lower() in ["uc", "unobserved components", "unobserved", "components"]:
            predictor = uc_predictor(dictionary)
        elif name.lower() == "prophet":
            predictor = prophet_predictor(dictionary)
        elif name.lower() == "cubist":
            predictor = cubist_predictor(dictionary)
        else:
            print("Incorrect Model")
            return
        self.predictors.append(predictor)
        self.weights.append(weight)

    def fit(self, time, values):
        for predictor in self.predictors:
            predictor.fit(time, values)
            predictor.update_label()

    def get_function(self):
        active_functions = lambda time: np.array([pred.function(time) for pred in self.active_predictors]) if len(time.data) != 0 else []
        return lambda time: mean(active_functions(time), self.active_weights)
    

class prediction_class(copy_class, total_predictor_class):
    def __init__(self):
        self.zero()
        
    def zero(self):
        self.set_function()
        self.set_data()
        total_predictor_class.zero(self)

    def set_function(self, function = None):
        self.function = function if function is not None else none_function

    def set_data(self, data = None):
        self.data = np.array(data) if data is not None else None

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

        
class predictor_class(copy_class):
    def __init__(self, name, dictionary):
        self.set_name(name)
        self.set_dictionary(dictionary)
        self.set_function()
        self.set_status()
        self.update_label()

    def set_name(self, name):
        self.name = name

    def set_dictionary(self, dictionary = None):
        self.dictionary = dictionary if dictionary is not None else {}
        
    def set_function(self, function = None):
        self.function = function
        
    def set_status(self, status = 0):
        self.status = status # -1 = Failed, 0 = Non Fitted, 1 = Fitted

    def update_label(self):
        self.update_label_short()
        self.update_label_long()

    def update_label_short(self):
        arguments = map(str, self.dictionary.values())
        arguments = ', '.join(arguments)
        self.label_short = self.name.title() + enclose_circled(arguments)
        
    def update_label_long(self):
        status = "Failed " if self.status == -1 else "Non Fitted " if self.status == 0 else ""
        dictionary = dictionary_to_string(self.dictionary) if self.dictionary is not None else ""
        dictionary = enclose_circled(dictionary)
        self.label_long = status + self.name.title() + dictionary

    def get_dataframe(self, time, values):
        return pd.DataFrame(index = time.pandas_index, data = {'values': values.data})

    def __mul__(self, constant):
        new = self.copy()
        new.set_function(lambda el: self.function(el) * constant)
        return new

    
class naive_predictor(predictor_class):
    def __init__(self, dictionary):
        dictionary = {"level": "mean"} if dictionary is None else dictionary
        predictor_class.__init__(self, "naive", dictionary)

    def fit(self, time, values):
        level = self.dictionary["level"]
        level = 0 if level == "zero" else values.mean if level == "mean" else values.last if level == "last" else values.first if level == "first" else level
        dictionary = {"level": level}
        function = lambda time: zero(time.length) + level
        self.set_function(function)
        self.set_status(1)


class arima_predictor(predictor_class):
    def __init__(self, dictionary):
        predictor_class.__init__(self, "arima", dictionary)

    def fit(self, time, values):
        try:
            dataframe = self.get_dataframe(time, values)
            model = arima(endog = dataframe, **self.dictionary)
            fit = model.fit(disp = 0)
            function = lambda time: fit.predict(time.pandas_index[0], time.pandas_index[-1]).to_numpy()
            self.set_function(function)
            self.set_status(1)
        except (UserWarning, RuntimeWarning, LinAlgError, TypeError, ValueError, ConvergenceWarning):
            self.set_status(-1)


class auto_arima_predictor(arima_predictor):
    def __init__(self, dictionary):
        predictor_class.__init__(self, "auto arima", dictionary)

    def fit(self, time, values):
        try:
            model = auto_arima(values.data, **self.dictionary)
            order = model.order
            seasonal_order = model.seasonal_order
            dictionary = {"order": order, "seasonal_order": seasonal_order}
            arima_predictor.__init__(self, dictionary)
            self.set_name("Auto Arima")
            arima_predictor.fit(self, time, values)
        except (RuntimeWarning):
            self.set_status(-1)

        
class es_predictor(predictor_class):
    def __init__(self, dictionary):
        predictor_class.__init__(self, "exponential smoothing", dictionary)

    def fit(self, time, values):
        try:
            dataframe = self.get_dataframe(time, values)
            model = ES(endog = dataframe, **self.dictionary)
            fit = model.fit()
            function = lambda time: fit.predict(time.pandas_index[0], time.pandas_index[-1]).to_numpy()
            self.set_function(function)
            self.set_status(1)
        except (TypeError, ValueWarning, ConvergenceWarning, ValueError):
            self.set_status(-1)


class uc_predictor(predictor_class):
    def __init__(self, dictionary):
        predictor_class.__init__(self, "Unobserved Components", dictionary)

    def fit(self, time, values):
        try:
            dataframe = self.get_dataframe(time, values)
            model = UC(endog = dataframe, **self.dictionary)
            fit = model.fit(disp = 0)
            function = lambda time: fit.predict(time.pandas_index[0], time.pandas_index[-1]).to_numpy()
            self.set_function(function)
            self.set_status(1)
        except (TypeError, RuntimeWarning, ConvergenceWarning, SpecificationWarning, ValueWarning, LinAlgError, ValueError):
            self.set_status(-1)


class prophet_predictor(predictor_class):
    def __init__(self, dictionary):
        predictor_class.__init__(self, "prophet", dictionary)

    def get_dataframe(self, time, values):
        return pd.DataFrame(data = {'ds': time.datetime, 'y': values.data})

    def fit(self, time, values):
        try:
            dataframe = self.get_dataframe(time, values)
            model = prophet(**self.dictionary)
            fit = model.fit(dataframe)
            function = lambda time: fit.predict(pd.DataFrame(data = {'ds': time.pandas_index})).yhat.to_numpy()
            self.set_function(function)
            self.set_status(1)
        except TypeError:
            self.set_status(-1)
    
            
class cubist_predictor(predictor_class):
    def __init__(self, dictionary):
        predictor_class.__init__(self, "cubist", dictionary)

    def get_time(self, time):
        return pd.DataFrame(time.index_reshaped, columns = ["time"])
        
    def fit(self, time, values):
        try:
            model = cubist(**self.dictionary)
            fit = model.fit(self.get_time(time), values.data)
            function = lambda time: fit.predict(self.get_time(time))
            self.set_function(function)
            self.set_status(1)
        except (TypeError, ValueError, UserWarning):
           self.set_status(-1)


# Utilities
is_constant = lambda data: len(data) == 0 or all([el == data[0] for el in data[1:]])
zero = lambda length: np.full(length, 0)



