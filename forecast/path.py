from forecast.values import values_class
from forecast.time import time_class, time_form

from forecast.string import get_numerical, strings_to_numbers, form_to_input
import os
import pandas as pd


# Path Manipulation
def correct_path(folder):
    folder = os.path.normpath(folder)
    folder = folder.replace("~", user_folder)
    is_relative = folder[ : len(os.sep)] != os.sep 
    folder = os.path.join(input_folder, folder) if is_relative else folder
    return folder

def join_paths(*args): # it join a list of string in a proper file path; if the first argument is ~ it is turnded into the used home folder path
    return os.path.join(*args)

def name(path):
    return os.path.basename(correct_path(path))


# Folders
user_folder = os.path.expanduser("~")
forecast_folder = join_paths(user_folder, "Documents", "Forecast")
input_folder = join_paths(forecast_folder, "input")
output_folder = join_paths(forecast_folder, "output")

os.makedirs(input_folder) if not os.path.exists(input_folder) else None
os.makedirs(output_folder) if not os.path.exists(output_folder) else None


# Read Files
def read(path):
    path = correct_path(path)
    with open(path, "r") as file:
        text = file.readlines()
    return text

def read_table(path, delimiter = ","):
    path = add_csv(path)
    text = read(path)
    data = [el.replace("\n", "").split(delimiter) for el in text]
    return data

add_csv = lambda path: path + ".csv" if "." not in name(path) else path

def read_data(path): # it turns a text file into data lists
    path = add_csv(path)
    text = read(path)
    data = [get_numerical(el) for el in text]
    return data

def read_time_data(path, header = True, form = None):
    data = read_data(path)
    data = data[1 - header : ]
    values = [el[-1] for el in data]
    time = [el[:-1][:3] for el in data]
    values = strings_to_numbers(values)
    form = time_form(time) if form is None else form
    input_form = form_to_input(form)
    time = [input_form.format(*el) for el in time]
    time = time_class(time, form)
    values = values_class(values)
    return time, values

def read_time_dataframe(frame, time_name = None, values_name = None):
    time = frame.index if time_name is None else frame[time_name]
    values = frame.iloc[:, -1] if values_name is None else frame[values_name]
    form = '%d/%m/%Y'
    time = pd.DatetimeIndex(time)
    time = time.strftime(form)
    time = time_class(time, form)
    values = values_class(values)
    return time, values


# def parts(path):
#     path  = correct(path)
#     parts = path.split(os.sep)
#     parts = ["/"] + [el for el in parts if el != ""] 
#     return parts
    

# def parent(folder, level = 1): # it return the parent folder of the path or file given; if level is higher then 1 the process is iterated
#     parts = parts(folder)
#     l = len(parts)
#     level = l - 1 if level is None or level > l - 1 else level
#     parts = parts[ : l - level]
#     return join(*parts)


# root = lambda path: parent_folder(copath, None)
