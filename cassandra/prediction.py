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
        self.set_name()
        self.set_dictionary()
        self.set_function()
        self.set_data()
        self.set_status()
        self.update_label()

    def set_name(self, name = None):
        self.name = name

    def set_dictionary(self, dictionary = None):
        self.dictionary = dictionary
        
    def set_status(self, status = 0):
        self.status = status # -1 = Failed, 0 = Non Fitted, 1 = Fitted
        
    def set_naive(self, level = 'mean'):
        self.set_name('naive')
        self.set_dictionary({'level': level})
        return self
     
    def set_es(self, period):
        self.set_name('es')
        self.set_dictionary({"seasonal_periods": period, "seasonal": "add"})
        return self

    def fit_es(self, data):
        try:
            model = ES(endog = data.values.data, **self.dictionary)
            fit = model.fit()
            function = lambda time: fit.predict(time.index[0], time.index[-1])
            self.set_status(1)
            self.set_function(function)
        except (RuntimeWarning, TypeError, ValueWarning, ConvergenceWarning, ValueError):
            self.set_status(-1)
            self.set_function()
            
    def fit_naive(self, data):
        level = self.dictionary["level"]
        level = 0 if level == "zero" else data.values.mean if level == "mean" else data.values.last if level == "last" else data.values.first if level == "first" else level
        function = lambda time: np.full(time.length, 0) + level
        self.set_function(function)
        self.set_status(1)

    def fit(self, data):
        self.fit_naive(data) if self.name == 'naive' else self.fit_es(data) if self.name == 'es' else None
        self.update_data(data.time)
        self.update_label()

    def update_label(self):
        status = "Failed-" if self.status == -1 else "Not-Fitted-" if self.status == 0 else ''
        label = status + self.name.title() if self.name is not None else None
        label = label + enclose_circled(self.dictionary['level']) if self.name == 'naive' else label
        label = label + enclose_circled(self.dictionary['seasonal_periods']) if self.name == 'es' else label
        self.label = label

    def empty(self):
        new = prediction_class()
        new.name = self.name
        new.dictionary = self.dictionary.copy() if self.dictionary is not None else None
        new.function = self.function
        new.name = self.name
        new.status = self.status
        new.update_label()
        return new

