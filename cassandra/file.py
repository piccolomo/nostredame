import os
from cassandra.time import time_class
from cassandra.values import values_class
from cassandra.data import data_class

# Path Manipulation
def correct_path(folder):
    folder = os.path.normpath(folder)
    folder = folder.replace("~", user_folder)
    is_relative = folder[ : len(os.sep)] != os.sep 
    folder = os.path.join(input_folder, folder) if is_relative else folder
    return folder

def join_paths(*args):
    return os.path.join(*args)

def base_name(path):
    return os.path.basename(correct_path(path))

add_csv_extension = lambda path: path + ".csv" if "." not in base_name(path) else path


# Folders
user_folder = os.path.expanduser("~")
forecast_folder = join_paths(user_folder, "Documents", "Forecast")

code_folder = join_paths(forecast_folder, "code")
input_folder = join_paths(forecast_folder, "input")
output_folder = join_paths(forecast_folder, "output")

os.makedirs(code_folder) if not os.path.exists(input_folder) else None
os.makedirs(input_folder) if not os.path.exists(input_folder) else None
os.makedirs(output_folder) if not os.path.exists(output_folder) else None


# Read Files
def read_table(path, delimiter = ",", header = False):
    path = add_csv_extension(path)
    text = read_text(path)
    text = text[header : ]
    data = [el.replace("\n", "").split(delimiter) for el in text]
    return data

def read_text(path):
    path = correct_path(path)
    with open(path, "r") as file:
        text = file.readlines()
    return text

def read_data(path,  delimiter = ",", header = False, form = None, string_function = None):
    data = read_table(path, delimiter, header)
    values = [float(el[-1]) for el in data]
    time = [el[0] for el in data]
    time = time_class(time, form, string_function)
    values = values_class(values)
    return data_class(time, values)

