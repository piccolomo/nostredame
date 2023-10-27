from statsmodels.tsa.stattools import acf
from scipy.signal import find_peaks
import numpy as np


# Time Utilities
to_time_class_function = lambda function: (lambda time: np.array([function(el) for el in time.index]))


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
    return np.vectorize(function)(data)
    
remove_trend = lambda data, order = 2: data if order is None else data - get_trend_data(data, order)


# Season Utilities
transpose = lambda matrix: list(map(list, zip(*matrix)))

def get_season_function(data, period):
    data = get_partial_season(data, period)
    function = lambda el: data[el % period]
    return function
    
def get_partial_season(data, period):
    period = [np.mean(data[i : : period]) for i in range(period)]
    return np.array(period)

get_acf = lambda data: acf(data, nlags = len(data))

from cassandra.string import bold

def find_seasons(data, trend = 2, log = True, plot = True, threshold = 1):
    l = len(data)
    lower, upper = 2, l // 2
    data = remove_trend(data, trend)
    data = get_acf(data)
    data = [data[i] for i in range(lower, upper + 1)]
    mean, std = np.mean(data), np.std(data)
    data = [(el - mean)/ std for el in data]
    positions, properties = find_peaks(data, height = threshold, width = 0, rel_height = 0.5)
    positions += lower
    heights = properties["peak_heights"]
    lp = len(positions)
    if log:
        print(bold("seasonalites found"))
        print("detrend", trend)
        print('season\theight [stds]')
        for i in range(lp):
            print(positions[i], '\t', round(heights[i],2))
        if lp == 0:
            print("no peaks found: see ya!")
    return list(positions)



