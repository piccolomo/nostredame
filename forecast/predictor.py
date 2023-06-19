from forecast.backup import copy_class
from statsmodels.tsa.statespace.sarimax import SARIMAX as arima
from pmdarima.arima import auto_arima
from statsmodels.tsa.holtwinters import ExponentialSmoothing as ES
from statsmodels.tsa.statespace.structural import UnobservedComponents as UC
from prophet import Prophet as prophet
#from cubist import Cubist as cubist

from numpy.linalg import LinAlgError
from statsmodels.tools.sm_exceptions import ConvergenceWarning, SpecificationWarning, ValueWarning

import warnings
#warnings.filterwarnings("error")
#warnings.filterwarnings(action = "ignore", message = "unclosed", category = ResourceWarning)
warnings.filterwarnings(action = "ignore", category = ConvergenceWarning) # for a rare arima warning

import logging # to suppress prophet log
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").disabled = True

import forecast.tools as tl
import pandas as pd


class total_predictor_class():
    def __init__(self):
        self.zero()
        #         self.update_label()
        #         self.update_function()
        
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
        total_weight = tl.np.sum(self.active_weights)
        active_weights = [100 * el / total_weight for el in self.active_weights]
        is_constant = tl.is_constant(self.active_weights)
        self.relative_weights = [str(round(el, 2)) + " % " if not is_constant else "" for el in active_weights]

    def update_label(self):
        self.update_labels()
        no_label = len(self.active_predictors) == 0
        self.update_short_label(no_label)
        self.update_long_label(no_label)
        
    def update_labels(self):
        [el.update_label() for el in self.predictors]
        
    def update_short_label(self, no_label):
        labels = [pred.short_label for pred in self.active_predictors]
        self.short_label = None if no_label else ' + '.join(labels)
    
    def update_long_label(self, no_label):
        l = len(self.active_predictors)
        labels = [pred.long_label for pred in self.active_predictors]
        labels = [self.relative_weights[i] + labels[i] for i in range(l)]
        self.long_label = None if no_label else tl.pad('Predictor', 11) + ' + '.join(labels)

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
        ##elif name.lower() == "cubist":
        ##    predictor = cubist_predictor(dictionary)
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
        active_functions = lambda time: tl.np.array([pred.function(time) for pred in self.active_predictors]) if len(time.data) != 0 else []
        return lambda time: tl.mean(active_functions(time), self.active_weights)

        
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
        self.update_short_label()
        self.update_long_label()

    def update_short_label(self):
        self.short_label = self.name.title()
        
    def update_long_label(self):
        status = "Failed " if self.status == -1 else "Non Fitted " if self.status == 0 else ""
        dictionary = tl.dictionary_to_string(self.dictionary) if self.dictionary is not None else ""
        dictionary = tl.enclose_circled(dictionary)
        self.long_label = status + self.name.title() + dictionary

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
        function = lambda time: tl.zero(time.length) + level
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


# class cubist_predictor(predictor_class):
#     def __init__(self, dictionary):
#         predictor_class.__init__(self, "cubist", dictionary)

#     def get_time(self, time):
#         return pd.DataFrame(time.index_reshaped, columns = ["time"])
        
#     def fit(self, time, values):
#         try:
#             model = cubist(**self.dictionary)
#             fit = model.fit(self.get_time(time), values.data)
#             function = lambda time: fit.predict(self.get_time(time))
#             self.set_function(function)
#             self.set_status(1)
#         except (TypeError, ValueError, UserWarning):
#            self.set_status(-1)

from random import choice

class dictionaries_class():
    def __init__(self):
        self.naive = naive_dictionaries()
        self.arima = arima_dictionaries()
        self.es = es_dictionaries()
        self.uc = uc_dictionaries()
        self.prophet = prophet_dictionaries()
        #self.cubist = cubist_dictionaries()


class naive_dictionaries():
    def default(self, level = "mean"):
        return {"level": level}
    
    def all(self):
        return [self.default(level) for level in ["first", "mean", "last"]]

    def random(self):
        return choice(self.all())

        
class arima_dictionaries():
    def default(self, p = 1, d = 1, q = 1, P = 1, D = 1, Q = 1, s = 12):
        return {"order": (p, d, q), "seasonal_order": (P, D, Q, s)} 
    
    def all(self, periods, order = 2):
        data = list(range(0, order + 1))
        return [self.default(p, d, q, P, D, Q, s) for p in data for d in data for q in data for P in data for D in data for Q in data for s in periods]

    def random(self, periods, order = 2):
        return choice(self.all(periods, order))

class es_dictionaries():
    def default(self, p = 12):
        return {"seasonal_periods": p, "seasonal": "add"}
    
    def all(self, periods):
        return [self.default(p) for p in periods]

    def random(self, periods):
        return choice(self.all(periods))



class uc_dictionaries():
    def __init__(self):
        self.levels = ['random walk', 'local linear trend', 'smooth trend', 'local level', 'deterministic constant', 'deterministic trend', "fixed intercept", "fixed slope", "local linear deterministic trend", "ntrend", 'random trend', 'random walk with drift']

    def default(self, l = 'random walk', c = True, s = 12, a = 1, sc = True):
        return {'level': l, 'cycle': c, 'seasonal': s, 'autoregressive': a, 'stochastic_cycle': sc}
        
    def all(self, periods, order = 2):
        A = list(range(0, order + 1))
        C = [True, False]
        return [self.default(l, c, s, a, sc) for l in self.levels for c in C for s in periods for a in A for sc in C]

    def random(self, periods, order = 2):
        return choice(self.all(periods, order))


class prophet_dictionaries():
    def default(self, y = True, n = 12):
        return {"yearly_seasonality": y, "n_changepoints": n}
    
    def all(self, order = 10):
        Y = [True, False]
        N = list(range(0, order + 1))
        return [self.default(y, n) for y in Y for n in N]

    def random(self, order = 10):
        return choice(self.all(order))

    
class cubist_dictionaries():
    def default(self, nc = 0, n = 1, c = True, u = True):
        return {"n_committees": nc, "neighbors": n, "composite": c, "unbiased": u} 
        
    def all(self, order = 10):
        NC = list(range(0, order + 1))
        N = range(1, 9)
        C = [True, False]
        return [self.default(nc, n, c, u) for nc in NC for n in N for c in C for u in C]

    def random(self, order = 10):
        return choice(self.all(order))


dictionary = dictionaries_class()


    

    

    
