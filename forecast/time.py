from forecast.backup import copy_class
from forecast.season import transpose
from forecast.string import strings_to_numbers
from datetime import datetime as dt
from calendar import monthrange
from datetime import timedelta

import numpy as np
import pandas as pd

# from dateutil.relativedelta import relativedelta
# from forecast.tools import transpose


class time_class(copy_class):
    def __init__(self, data = [], form = None, time0 = None):
        self.set(data)
        self.set_form(form)
        self.set_datetime()
        #self.sort()
        # #self.set_datetime64()
        self.set_time0(time0)
        # self.set_timestamp()
        self.set_index()
        self.set_pandas_formats()

    def set_form(self, form):
        form = "%d/%m/%Y" if form is None else form
        self.form = form

    def set(self, data):
        self.data = data
        self.update_length()

    def update_length(self):
        self.length = self.l = len(self.data)

    def set_datetime(self):
        self.datetime = [dt.strptime(el, self.form) for el in self.data]
        self.freq = get_frequency(self.datetime) if self.length > 1 else None
        
    # def sort(self):
    #     dt_sorted = sorted(self.datetime)
    #     self.index_to_sort = [self.datetime.index(el) for el in dt_sorted]
    #     #self.index_to_unsort = [dt_sorted.index(el) for el in self.datetime]
    #     self.data = [self.data[i] for i in self.index_to_sort]
    #     self.datetime = dt_sorted

    # def set_datetime64(self):
    #     self.datetime64 = np.array([np.datetime64(el) for el in self.datetime])
    #     self.datetime64_reshaped = self.datetime64.reshape(-1, 1)

    def set_time0(self, time0 = None):
        self.time0 = min(self.datetime) if time0 is None and self.length > 0 else time0
        self.timestamp0 = self.time0.timestamp() if self.time0 is not None else 0
        
    # def set_timestamp(self):
    #     self.timestamp = ts = [el.timestamp() for el in self.datetime]
    #     dt = np.mean(derivative(self.timestamp)) if self.length > 1 else 1
    #     self.norm = [(ts[i] - self.timestamp0) / dt for i in range(self.length)]

    def set_index(self):
        dt = self.datetime
        self.index = [int(time_difference(dt[i], self.time0, self.freq)) for i in range(self.length)] if self.freq is not None else list(range(self.length))
        self.index_reshaped = np.array(self.index).reshape(-1, 1)

    def set_pandas_formats(self):
        #self.pd_timestamp = [pd.Timestamp(el) for el in self.datetime]
        self.pandas_index = pd.DatetimeIndex(self.datetime, freq = 'infer')
        #self.pd_freq = self.pd_index.freq


    # def forecast(self, length):
    #     index = range(0, length + 1) # 0 instead of 1 to make sure there is at least 2 elements in the new time class, otherwise the frequency cannot be calculated
    #     time = [add_time(self.datetime[-1], p, self.freq) for p in index]
    #     time = [el.strftime(self.form) for el in time]
    #     new = time_class(time, self.form, self.datetime[0])
    #     return new.part(1, length + 1)# the part method saves the frequency even for 1 element

    # def append(self, time):
    #     

    # def extend(self, length):
    #     return self.append(self.forecast(length))

    def forecast(self, length):
        index = range(-1, length + 1)
        time = [add_time(self.datetime[-1], p, self.freq) for p in index]
        time = [el.strftime(self.form) for el in time]
        new = time_class(time, self.form, self.datetime[0])
        return new.part(2, None)
    
    def append(self, time):
        return time_class(self.data + time.data, self.form, self.time0)

    def extend(self, length):
        return self.append(self.forecast(length))

    def part(self, begin, end):
        data = self.data[begin : end]
        new = time_class(data, self.form, self.time0)
        new.freq = self.freq
        new.index = self.index[begin : end]
        return new
    
    # def forecast(self, length):
    #     index = range(1, length + 1)
    #     time = [add_time(self.datetime[-1], p, self.freq) for p in index]
    #     time = [el.strftime(self.form) for el in time]
    #     time = time_class(time, self.form, self.datetime[0])
    #     return time

    # def append(self, time): # add horizontally
    #     return self.copy_from(self + time)

    # def extend(self, length):
    #     return self.append(self.forecast(length))
    
    # def __add__(self, time): # add horizonally
    #     return time_class(self.data + time.data, self.form, self.time0)

    # def __len__(self):
    #     return self.length

    # def split(self, size):
    #     train, test = self.split_method(size)
    #     train.update_length(); test.update_length();
    #     return train, test
    
def get_frequency(datetimes):
    deltas = [freq(datetimes, scale) for scale in scales]
    deltas_bool = [el != 0 for el in deltas]
    pos = len(scales) - 1 - deltas_bool[::-1].index(True)
    return (deltas[pos], scales[pos])

freq = lambda datetimes, scale: max(timediff(datetimes, scale)) # maximum number of days/years etc differences from one date to the next in a list of datetimes 
timediff = lambda datetimes, scale: derivative(timescale(datetimes, scale)) # from a list of datetimes to a list of scale differences, where scale is chosen (year/month/day etc) 
derivative = lambda data: [data[i] - data[i - 1] for i in range(1, len(data))] #  derivative of a list
timescale = lambda datetimes, scale: [eval("el." + scale) for el in datetimes] # for each element of a list of datetimes, it returns his scale chosen (year/month/day etc)
scales = ["year", "month", "day", "hour", "minute", "second", "microsecond"]

days_in_month = lambda time: monthrange(time.year, time.month)[1] # how many days in a particular month

def time_difference(time1, time0, freq):
    td = (time1 - time0)
    days = td.days + (td.seconds + td.microseconds / 10 ** 6) / (60 * 60 * 24)
    hours = days * 24
    minutes = hours * 60
    seconds = minutes * 60
    micros = seconds * 1000
    
    months = 12 * (time1.year - time0.year) + time1.month - time0.month
    extra_days = (time1.day - time0.day)
    extra_days += (time1.hour - time0.hour) / 24
    extra_days += (time1.minute - time0.minute) / (24 * 60)
    extra_days += (time1.second - time0.second) / (24 * 60 * 60)
    extra_days += (time1.microsecond - time0.microsecond) / (24 * 60 * 60 * 1000)
    months +=  extra_days / days_in_month(time1)
    
    years = months / 12
    out = [years, months, days, hours, minutes, seconds, micros]
    pos = scales.index(freq[1])
    return out[pos] / freq[0]

def add_time(datetime, delta, freq): # it jumps delta steps ahead of datetime where each step is defined by freq
    dictionary = {freq[1] + "s": delta * freq[0]}
    past_days = freq[1] in scales[0:2]
    delta = timedelta(**dictionary) if not past_days else relativedelta(**dictionary)
    return datetime + delta

# Time Forms 
def single_time_form(data):
    S = max(map(len, data))
    data = strings_to_numbers(data)
    m, M = min(data), max(data)
    if M >= 99:
        return "%Y"
    elif M > 31:
        return "%y"
    elif M > 12:
        return "%d"
    else:
        return "%m"

def time_form(data):
    data = transpose(data)
    form = [single_time_form(el) for el in data]
    form = '/'.join(form)
    return form

