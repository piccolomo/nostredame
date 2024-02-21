from statsmodels.tsa.stattools import acf
from scipy.signal import find_peaks
import numpy as np

import warnings
warnings.simplefilter('ignore', np.RankWarning)

# Time Utilities
to_time_class_function = lambda function: (lambda time: np.array([function(el) for el in time.index]))
nan_function = lambda el: np.nan
nan_time_class_function = to_time_class_function(nan_function)

# Trend Utilities
def get_trend_function(x, y, order = 2):
    try:
        poly = np.polyfit(x, y, deg = order)
        function = np.poly1d(poly)
        return function
    except (RuntimeWarning, np.RankWarning):
        return lambda el: np.nan
        
def get_trend_data(data, order = 2):
    x = range(len(data))
    function = get_trend_function(x, data, order)
    return np.vectorize(function)(x)
    
remove_trend = lambda data, order = 2: data - get_trend_data(data, order)


# Season Utilities

def get_season_function(data, period):
    data = get_partial_season(data, period)
    function = lambda el: data[el % period]
    return function
    
def get_partial_season(data, period):
    period = [np.mean(data[i : : period]) for i in range(period)]
    return np.array(period)

get_acf = lambda data: acf(data, nlags = len(data))

def find_seasons(data, threshold = 1, detrend = 3, log = True):
    l = len(data)
    lower, upper = 2, l // 2
    data = remove_trend(data, detrend)
    data = get_acf(data)
    data = [data[i] for i in range(lower, upper + 1)]
    mean, std = np.mean(data), np.std(data)
    data = [(el - mean)/ std for el in data]
    periods, properties = find_peaks(data, height = threshold, width = 0, rel_height = 0.5)
    periods += lower
    heights = properties["peak_heights"]
    lp = len(periods); rp = range(lp)
    periods, heights = transpose(sorted(transpose([periods, heights]), key=lambda el: -el[1]), 2)
    print('season  height') if log and lp > 0 else None
    [print("{:<7} {:.2f}".format(periods[i], heights[i])) for i in rp] if log else None
    periods = np.transpose(sorted(np.transpose([periods, heights]), key = lambda el: -el[1]))[0] if lp > 0 else []
    return [int(el) for el in periods]

def get_minimum(data, qualities):
    m = min([el for el in qualities if el is not None], default = None)
    return data[qualities.index(m)] if m is not None else None


transpose = lambda data, length = 1: [[]] * length if data == [] else list(map(list, zip(*data)))

    
