from cassandra.trend import trend_class
from cassandra.list import remove_trend, get_season_function, to_time_class_function
from numpy import sum
from cassandra.string import enclose_circled

class season_class(trend_class):
    def __init__(self):
        self.set_periods()
        trend_class.__init__(self)

    def set_periods(self, periods = []):
        self.periods = periods

    def fit(self, data, periods, detrend):
        periods = [p for p in periods if p not in [0, 1]]
        self.fit_function(data, periods, detrend)
        self.update_data(data.time)
        self.set_periods(periods)
        self.set_order(detrend)
        self.update_label()
      
    def fit_function(self, data, periods, detrend = None):
        y = data.values.data.copy()
        y = remove_trend(y, detrend)
        functions = []
        for period in periods:
            function = get_season_function(y, period) #+ trend
            functions.append(function)
        function = lambda el: sum([function(el) for function in functions])
        function = to_time_class_function(function)
        self.set_function(function)
         
    def update_label(self):
    	self.label = "Season" + enclose_circled(', '.join(map(str,self.periods)) + ", detrend = " + str(self.order)) if len(self.periods) > 0 else None

    def project(self, time):
        new = self.copy()
        new.update_data(time)
        return new
