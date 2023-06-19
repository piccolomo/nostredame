from forecast.backup import copy_class
import forecast.tools as tl

class trend_class(copy_class):
    def __init__(self):
        self.zero()

    def zero(self):
        self.set_order()
        self.set_function()
        self.set_data()
        self.update_label()

    def set_order(self, order = None):
        self.order = order

    def set_function(self, function = None):
        self.function = function if function is not None else tl.none_function
        
    def set_data(self, data = None):
        self.data = tl.np.array(data) if data is not None else None

    def update_data(self, time):
        data = self.predict(time)
        self.set_data(data)

    def fit_function(self, time, values, order):
        function = tl.get_trend_function(time.index, values.data, order)
        self.set_function(tl.to_time_function(function))

    def fit(self, time, values, order):
        self.fit_function(time, values, order)
        self.set_order(order)
        self.update_label()
        
    def update_label(self):
        no_label = self.order is None
        self.update_short_label(no_label)
        self.update_long_label(no_label)
        
    def update_short_label(self, no_label):
        label = "Trend"
        self.short_label = None if no_label else label

    def update_long_label(self, no_label):
        label = tl.pad("Trend", 11) + str(self.order)
        self.long_label = None if no_label else label


    def get_data(self):
        return self.data if self.data is not None else 0

    def predict(self, time):
        return self.function(time)

    def project(self, time):
        new = self.copy()
        new.update_data(time)
        #new.update_label()
        return new

        
    def __mul__(self, constant):
        new = self.copy()
        data = None if self.data is None else self.data * constant
        new.set_data(data)
        function = tl.none_function if self.function == tl.none_function else (lambda el: self.function(el) * constant)
        new.set_function(function)
        return new
        
