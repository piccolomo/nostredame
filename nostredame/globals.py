from .file import read_table
from .time import time_class
from .values import values_class
from .data import data_class

def read_data(path,  delimiter = ",", header = False, form = None, string_function = None):
    data = read_table(path, delimiter, header)
    values = [float(el[-1].replace(',', '.')) for el in data]
    time = [el[0] for el in data]
    time = time_class(time, form, string_function)
    values = values_class(values)
    return data_class(time, values)
