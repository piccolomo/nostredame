from .file import read_table, read_excel_data
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


def read_excel(file_name, header = False, form = None, log = True):
    print('loading data') if log else None 
    matrices = read_excel_data(file_name, log = log)
    datas = matrices.copy()
    for sheet in matrices:
        data = matrices[sheet]
        time = [el[0] for el in data]
        time = time_class(time, form)
        values = [float(el[-1].replace(',', '.')) for el in data]
        values = values_class(values)
        datas[sheet] = data_class(time, values).set_name(sheet)
    print('data loaded!\n') if log else None
    return datas
