from statsmodels.tools.sm_exceptions import ConvergenceWarning, SpecificationWarning, ValueWarning
from statsmodels.tsa.holtwinters import ExponentialSmoothing as ES
from cassandra.string import enclose_circled
from cassandra.trend import trend_class, np
import warnings
warnings.simplefilter('ignore', ConvergenceWarning)

class prediction_class(trend_class):
    def __init__(self):
        self.zero()
        
    def zero(self):
        self.predictor = None
        super().zero()
        
    def set_data(self, data = None):
        self.data = None if data is None else np.array(data)

    def update_label(self):
        self.predictor.update_label() if self.predictor is not None else None


    def set_predictor(self, name, dictionary):
        self.predictor = naive_predictor(dictionary) if name == "naive" else es_predictor(dictionary) if name == "es" else None
        print("Incorrect Model") if name not in ['es', 'naive'] else None

    def set_naive(self, level = 'mean'):
        self.set_predictor("naive", {'level': level})
        return self
     
    def set_es(self, period):
        self.set_predictor("es", {"seasonal_periods": period, "seasonal": "add"})
        return self

    def fit(self, data):
        self.predictor.fit(data) if self.predictor is not None else None
        self.update_data(data.time) if self.predictor.status == 1 else self.set_data() 
        self.update_label()

    def update_data(self, time):
        data = self.predict(time)
        self.set_data(data)

    def predict(self, time):
        just_do_it = self.predictor is not None and self.predictor.function is not None
        return self.predictor.function(time) if just_do_it else None

    def update_label(self):
        self.predictor.update_label() if self.predictor is not None else None
        self.label = self.predictor.label if self.predictor is not None else None
    
    def empty(self):
        new = prediction_class()
        new.predictor = self.predictor
        new.update_label()
        return new

        
class predictor_class():
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


        
class naive_predictor(predictor_class):
    def __init__(self, dictionary):
        predictor_class.__init__(self, "naive", dictionary)

    def fit(self, data):
        level = self.dictionary["level"]
        level = 0 if level == "zero" else deata.values.mean if level == "mean" else data.values.last if level == "last" else data.values.first if level == "first" else level
        dictionary = {"level": level}
        function = lambda time: np.full(time.length, 0) + level
        self.set_function(function)
        self.set_status(1)

    def update_label(self):
        self.label = self.name.title() + enclose_circled(self.dictionary['level'])

        
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
        except (RuntimeWarning, TypeError, ValueWarning, ConvergenceWarning, ValueError):
            self.set_status(-1)
            self.set_function()

    def update_label(self):
        status = "Failed-" if self.status == -1 else "Not-Fitted-" if self.status == 0 else ''
        self.label = status + self.name.title() + enclose_circled(self.dictionary['seasonal_periods'])


