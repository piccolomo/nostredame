from forecast.backup import copy_class
from datetime import datetime as dt
from datetime import timedelta as td
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import pandas as pd


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
        self.datetime_pandas = pd.DatetimeIndex(self.datetime, freq = 'infer')
        self.freq_pandas = self.datetime_pandas.freq

    def forecast(self, length):
        index = range(-1, length + 1)
        time = [self.datetime[-1] + self.freq * i for i in range(0, length + 1)][1:]
        time = [el.strftime(self.form) for el in time]
        return time_class(time, self.form)

    def append(self, time):
        return time_class(self.data + time.data, self.form)

    def extend(self, length):
        return self.append(self.forecast(length))

    def part(self, begin, end):
        data = self.data[begin : end]
        new = time_class(data, self.form)
        new.index = self.index[begin: end]
        return new

derivative = lambda data: [data[i] - data[i - 1] for i in range(1, len(data))]

def get_frequency(datetimes):
    t = datetimes; l = len(t)
    delta = [relativedelta(t[i + 1], t[i]) for i in range(0, l - 1)];
    delta_no_duplicates = list(set(delta))
    if len(delta_no_duplicates) != 1:
        raise ValueError("time differences seem inconsistent (or you are using end of the month data).")
    return delta_no_duplicates[0]

t1 = ["01/01/2014", "01/02/2014", "01/03/2014", "01/04/2014", "01/05/2014", "01/06/2014", "01/07/2014", "01/08/2014", "01/09/2014", "01/10/2014", "01/11/2014"]

# t2 = ["30/09/2021", "31/10/2021", "30/11/2021", "31/12/2021", "31/01/2022", "28/02/2022", "31/03/2022", "30/04/2022", "31/05/2022", "30/06/2022", "31/07/2022", "31/08/2022", "30/09/2022", "31/10/2022"]

# t3 = ["12/04/2020", "19/04/2020", "26/04/2020", "03/05/2020", "10/05/2020", "17/05/2020", "24/05/2020", "31/05/2020", "07/06/2020", "14/06/2020", "21/06/2020", "28/06/2020", "05/07/2020"]

# t3 = ["12/04/2020", "19/04/2020", "26/04/2020", "03/05/2020", "10/05/2020", "17/05/2020", "24/05/2020", "31/05/2020", "07/06/2020", "14/06/2020", "21/06/2020", "28/06/2020", "05/07/2020"]

t1 = time_class(t1)
# #t2 = time_class(t2)
# t3 = time_class(t3)

