from cassandra.trend import trend_class, np
from cassandra.list import remove_trend, get_season_function, to_time_class_function
from numpy import sum
from cassandra.string import enclose_circled
from cassandra.backup import copy_class


class season_class(trend_class):
    def __init__(self):
        self.zero()

    def zero(self):
        self.set_periods()
        super().zero()

    def set_periods(self, periods = []):
        self.periods = periods

    def fit(self, data, periods):
        periods = [p for p in periods if p not in [0, 1]]
        self.fit_function(data, periods)
        self.update_data(data.time)
        self.set_periods(periods)
        self.update_label()
      
    def fit_function(self, data, periods):
        y = data.values.data.copy(); r = range(len(y))
        functions = []
        for period in periods:
            function = get_season_function(y, period)
            functions.append(function)
            y -= np.vectorize(function)(r)
        function = lambda el: sum([function(el) for function in functions])
        function = to_time_class_function(function)
        self.set_function(function)
         
    def update_label(self):
    	self.label = "Season" + enclose_circled(', '.join(map(str,self.periods)) + ", detrend = " + str(self.order)) if len(self.periods) > 0 else None

        
    def empty(self):
        new = season_class()
        new.function = self.function
        new.periods = self.periods
        new.update_label()
        return new


