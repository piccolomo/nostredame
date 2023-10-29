from cassandra.backup import copy_class
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from pandas import DatetimeIndex

class time_class(copy_class):
    def __init__(self, data = [], form = None, string_function = None):
        self.set(data, string_function)
        self.set_form(form)
        self.set_datetime()
        self.update_frequency()
        self.set_pandas()

    def set(self, data, string_function):
        self.data = [string_function(el) for el in data] if string_function is not None else data
        self.update_length()

    def update_length(self):
        self.length = self.l = len(self.data)
        self.index = range(self.length)

    def set_form(self, form):
        self.form = "%d/%m/%Y" if form is None else form

    def set_datetime(self):
        self.datetime = [dt.strptime(el, self.form) for el in self.data]

    def update_frequency(self):
        self.freq = get_frequency(self.datetime)

    def set_pandas(self):
        self.datetime_pandas = DatetimeIndex(self.datetime, freq = 'infer')
        self.freq_pandas = self.datetime_pandas.freq

    def forecast(self, length):
        index = range(-1, length + 1)
        time = [self.datetime[-1] + self.freq * i for i in range(0, length + 1)][1:]
        time = [el.strftime(self.form) for el in time]
        new = time_class(time, self.form)
        new.index = range(self.length, self.length + length)
        return new

    def append(self, time):
        return time_class(self.data + time.data, self.form)

    def extend(self, length):
        return self.append(self.forecast(length))

    def part(self, begin, end):
        data = self.data[begin : end]
        new = time_class(data, self.form)
        new.index = self.index[begin: end]
        return new

def get_frequency(datetimes):
    t = datetimes; l = len(t)
    delta = [relativedelta(t[i + 1], t[i]) for i in range(0, l - 1)];
    delta_no_duplicates = list(set(delta))
    if len(delta_no_duplicates) != 1:
        raise ValueError("time differences seem inconsistent (or you are using end of the month data).") 
    return delta_no_duplicates[0]
