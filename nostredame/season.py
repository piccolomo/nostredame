from nostredame.trend import trend_class, np
from nostredame.list import remove_trend, get_season_function, to_time_class_function
from numpy import sum
from nostredame.string import enclose_circled
from nostredame.backup import copy_class


class season_class(trend_class):
    def __init__(self):
        self.zero()

    def zero(self):
        self.set_periods()
        super().zero()

    def set_periods(self, periods = []):
        self.periods = periods

    def select_periods(self, length):
        self.periods = [p for p in self.periods if p not in [0, 1] and p < length]

    def fit(self, data, periods):
        self.set_periods(periods)
        self.select_periods(data.length)
        self.fit_function(data) if len(self.periods) > 0 else None
        self.update_data(data.time)
        self.update_label()
      
    def fit_function(self, data):
        y = data.values.data.copy(); r = range(len(y))
        functions = []
        for period in self.periods:
            function = get_season_function(y, period)
            functions.append(function)
            y -= np.vectorize(function)(r)
        function = lambda el: sum([function(el) for function in functions])
        function = to_time_class_function(function)
        self.set_function(function)

         
    def update_label(self):
        periods = self.periods
        self.label = "Season" + enclose_circled(', '.join(map(str, periods))) if len(periods) > 0 else None

        
    def empty(self):
        new = season_class()
        new.function = self.function
        new.periods = self.periods
        new.update_label()
        return new


