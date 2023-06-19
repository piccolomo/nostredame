import forecast.tools as tl
from forecast.trend import trend_class

class season_class(trend_class):
    def __init__(self):
        self.set_periods()
        trend_class.__init__(self)

    def set_periods(self, periods = None):
        self.periods = periods if periods is not None else []
      
    def fit_function(self, time, values, periods, detrend = None):
        y = values.data.copy()
        y = tl.detrend(y, detrend)
        functions = []
        for period in periods:
            function = tl.get_season_function(y, period) #+ trend
            functions.append(function)
        function = lambda el: tl.np.sum([function(el) for function in functions])
        function = tl.to_time_function(function)
        self.set_function(function)
        
    def fit(self, time, values, periods, detrend):
        periods = [p for p in periods if p not in [0, 1]]
        self.fit_function(time, values, periods, detrend)
        self.set_periods(periods)
        self.set_order(detrend)
        self.update_label()

    def update_label(self):
        no_label = self.periods is None or len(self.periods) == 0
        self.update_short_label(no_label)
        self.update_long_label(no_label)
        
    def update_short_label(self, no_label):
        label = "Season"
        self.short_label = None if no_label else label

    def update_long_label(self, no_label):
        periods = list(map(str, self.periods))
        single_period = len(self.periods) == 1
        periods_string = "period = " if single_period else "periods = "
        periods_list = str(self.periods[0]) if single_period else tl.enclose_circled(', '.join(periods))
        periods = periods_string + periods_list
        detrend = "detrend = " + str(self.order)
        label = tl.pad("Season", 11) + periods + ", " + detrend
        self.long_label = None if no_label else label

    def project(self, time):
        new = self.copy()
        new.update_data(time)
        #new.update_label()
        return new
