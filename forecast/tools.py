from plotext import colorize, transpose, join_paths, read_data, script_folder, parent_folder, write_data, save_text
import numpy as np
import warnings
warnings.filterwarnings('error')
warnings.filterwarnings(action = "ignore", message = "unclosed", category = ResourceWarning)
from scipy.signal import find_peaks 
from statsmodels.tsa.stattools import acf
from scipy.fft import rfft as rfft 
from scipy.optimize import OptimizeWarning 
from scipy.optimize import curve_fit

from sklearn.metrics import r2_score as r2
from sklearn.metrics import mean_absolute_percentage_error as mape
import matplotlib.pyplot as plt
import os, sys


# Platform
def platform(): # the platform (unix or windows) you are using
   platform = sys.platform
   if platform in {'win32', 'cygwin'}:
       return 'windows'
   else:
       return 'unix'

platform = platform()

# Folder
home_folder = os.path.expanduser("~")
forecast_folder = join_paths(home_folder, "Documents", "Forecast")
input_folder = join_paths(forecast_folder, "input")
output_folder = join_paths(forecast_folder, "output")

os.makedirs(input_folder) if not os.path.exists(input_folder) else None
os.makedirs(output_folder) if not os.path.exists(output_folder) else None

# Constants
nan = np.nan
pi = np.pi
zero_function = lambda el: 0

# String
enclose_squared = lambda string: '[' + str(string) + ']' if string != "" else string
enclose_circled = lambda string: '(' + str(string) + ')' if string != "" else string

def pad(string, length = 6): # 25.69 or 100.0
    string = str(string)
    ls = len(string)
    #length = ls if length is None else max(length, ls)
    spaces = " " * (length - ls)
    string += spaces
    return string[ : length]

def str_round(num, level = 2):
   if level > 0:
      return str(round(num, level))
   else:
      return str(int(round(num, 0)))# + '.'

def pad_round(num, length = 6, level = 2):
   if is_nan_or_none(num):
      return pad(num, length)
   int_length = len(str(int(num))) 
   level = min(level, length - int_length - 1)
   string = str_round(num, level)
   l = len(string)
   string = pad(string, length) if length >= l else '9' * length
   return string

percentage = lambda num, total = 1: 100 * num / total

bold = lambda word: colorize(word, style = "bold")
nl = "\n"
tab = "  "

def dictionary_to_string(dictionary):
    rounding = lambda el: el if isinstance(el, str) or is_like_list(el) else round(el, 2)
    dictionary = {el: rounding(dictionary[el]) for el in dictionary}
    return str(dictionary)

delete_line = lambda: sys.stdout.write("\033[A\033[2K")
def indicator(i, tot): # i goes from 1 to tot
    delete_line() if i != 1 else None 
    print(pad_round(percentage(i, tot), 5) + " %")


# Data Creation
zero = lambda length: np.zeros(length)

# Data List Check
is_like_list = lambda data: any([isinstance(data, el) for el in [list, tuple, range, np.ndarray]])
is_zero = lambda data: (is_like_list(data) and all(np.array(data) == 0)) or (not is_like_list(data) and data == 0)
is_constant = lambda data: len(data) == 0 or all([el == data[0] for el in data[1:]])
has_nan = lambda data: any(np.isnan(data)) if is_like_list(data) else np.isnan(data)
no_nan = lambda data: not has_nan(data)
is_nan_or_none = lambda el: np.isnan(el) or el is None

# Data Modification
flatten = lambda matrix: [el for data in matrix for el in data]

# Functions
nan_function = lambda el: nan
none_function = lambda el: None
to_time_function = lambda function: (lambda time: np.array([function(el) for el in time.index]))
#nan_time_function = to_time_function(nan_function)
ratio_to_length = lambda ratio, length: length if ratio is None else round(ratio * length) if ratio <= 1 else int(ratio)

# Data Analysis
rms = lambda data: np.mean(np.array(data) ** 2) ** 0.5

def mean(data, weights = None):
    l = len(data); L = range(l)
    nan_pos = [i for i in L if has_nan(data[i])]
    data = [data[i] for i in L if i not in nan_pos]
    weights = [weights[i] for i in L if i not in nan_pos] if weights is not None else None
    return np.average(data, weights = weights, axis = 0) if len(data) > 0 else None

from scipy.interpolate import interp1d as interpolate
from math import ceil

get_fft = lambda data, p = 1: np.abs(rfft(data)) ** p

def get_fft_inter(data):
    fft = get_fft(data)
    l, lf = len(data), len(fft)
    x = [l / el for el in range(1, lf)] # l to l / (lf - 1) included
    y = fft[1:]
    inter = interpolate(x, y, kind = "cubic")
    f = ceil(l / (lf - 1))
    xr = range(f, l)
    yr = inter(xr)
    return np.concatenate(([yr[0]] * f, yr))

get_acf = lambda data: acf(data, nlags = len(data))
    


# Trend
def get_trend_function(x, y, order = 2):
    if order is None or order is nan or len(x) == 0:
        return zero_function
    try:
        poly = np.polyfit(x, y, deg = order)
        function = np.poly1d(poly)
        return function
    except (RuntimeWarning, np.RankWarning):
        return nan_function

def map_function(function, data):
    return np.array(list(map(function, data)))

def get_trend(data, order = 2):
    x = range(len(data))
    function = get_trend_function(x, data, order)
    return map_function(function, x)

detrend = lambda data, order = 2: data - get_trend(data, order)


# Season
def get_season_function(data, period):
    season = get_partial_season(data, period)
    function = lambda el: season[el % period]
    return function

def get_season(data, period):
    return repeat(get_partial_season(data, period), len(data))

def deseason(data, period):
    data = np.array(data) - get_season(data, period)
    #data = moving_average(data, period)
    return data

def get_partial_season(data, period):
    season = [np.mean(data[i : : period]) for i in range(period)]
    return np.array(season) #- np.mean(season)

def repeat(data, length):
    l = len(data)
    data = np.tile(data, (length // l) + 1)
    return data[ : length]

# Plot utils
def get_screen_size():
    try:
        if platform == "unix":
            process = os.popen("xrandr -q -d :0")
            screen = process.readlines()[0]
            process.close()
            width = screen.split()[7]
            height = screen.split()[9][:-1]
        elif platform == "window":
            #process = os.popen("xrandr -q -d :0")
            process = os.popen("wmic desktopmonitor get screenheight, screenwidth")
            lines = process.readlines()
            process.close()
            height, width = lines[4].split()
        else:
            height, width = None, None
        width, height = int(width), int(height)
    except:
        print("screen size failed in", platform)
        width, height = 2560, 1440
    return width, height

def set_plot_size():
    fig = plt.figure(0, constrained_layout = True)
    style = plt.style.available[-2]
    plt.style.use(style)
    
    mngr = plt.get_current_fig_manager();
    x, y = [round(el / 2) for el in get_screen_size()]
    size = "{}x{}+{}+{}".format(x, y, x, 0)
    mngr.window.geometry(size)

    fs = round(x / 80)
    plt.rcParams.update({'font.size': fs, "font.family": "sans-serif"})

# Find Season 
def get_peaks(data, threshold = 1, order = 1):
    l, m, M, std, mean = len(data), min(data), max(data), np.std(data), np.mean(data)
    height_threshold = threshold if order == 1 else 0
    prominence_threshold = prominence if order == 2 else 0
    positions, properties = find_peaks(data, height = height_threshold, prominence = prominence_threshold, width = 0, rel_height = 0.5)
    heights = properties["peak_heights"]
    prominences = properties["prominences"]
    #relative_prominences = 100 * (prominences - std) / (M - m)
    return sorted(zip(positions, heights, prominences), key = lambda tuple: tuple[order], reverse = 1)

def find_seasons(data, detrend_order = None, source = "acf", log = True, plot = True, threshold = 1):
    #print("Detrend Order", detrend_order, nl) if log else None
    #log += plot
    proceed_manually = (plot == 1)
    length = len(data)
    source = "acf" if "a" in source else "fft"
    use_acf = source == "acf"

    data = detrend(data, detrend_order)
    
    acf_data = get_acf(data)
    peaks_data = acf_data if use_acf else get_fft_inter(data)

    lower, upper = 2, length // (2 if use_acf else 3)
    x = range(lower, upper + 1)
    peaks_data = [peaks_data[i] for i in x]
    mean, std = np.mean(peaks_data), np.std(peaks_data)
    peaks_data = [(el - mean)/ std for el in peaks_data]
        
    peaks = get_peaks(peaks_data, threshold, 1)

    lp = len(peaks)
    (periods, heights, _) = transpose(peaks) if lp != 0 else [[]] * 3
    periods = [el + lower for el in periods]

    if log:
        for i in range(lp):
            period =  bold(pad(str(periods[i]), 3))
            height =  pad(str_round(heights[i], 1), 3)
            print(bold("Period"), period, "height", height, "[std]", source)
    if log and lp == 0:
        print("no peaks found: see ya!") if log else None

    if plot:
        set_plot_size()
        title = "AutoCorrelation Plot" if use_acf else "FFT Plot"
        plt.clf()
        plt.plot(x, peaks_data)
        plt.title(title)
        #plt.xscale("log") if not use_acf else None
        for period in periods:
            plt.axvline(x = period, c = "g", lw = 1)
        plt.axhline(y = threshold, c = "r", lw = 1)
        plt.xlim(lower - 1, upper + 1)
        #plt.ylim(0, 1.05)
        plt.xlabel("Period")
        plt.show(block = 0)

    return periods

def moving_average(data, length = 1):
    return np.convolve(data, np.ones(length), mode = "same") / length

def generate_trend(mean = 100, delta = 10, length = 1000, order = 2, noise = 1):
    y0 = mean - delta / 2
    d = abs(noise) * 4
    poly = np.random.normal(0, d, order - 1) if noise * order != 0 else [0] * (order - 1) 
    s = sum(poly)
    poly = [y0] + list(poly) + [delta - s]
    poly = [poly[i] / length ** i for i in range(order + 1)][ : : -1]
    return np.polyval(poly, range(length))


def generate_season(period, amplitude, length, order = 4, noise = 1):
    repeat = length // period + 1
    signal = [generate_trend(0, amplitude, period, order, noise)] * repeat
    signal = flatten(signal)
    return np.array(signal[ : length])

def generate_noise(mean, amplitude, length):
    return np.random.normal(0, amplitude , length)
