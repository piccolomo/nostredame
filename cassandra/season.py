from cassandra.trend import trend_class, remove_trend, to_time_function, generate_trend
from cassandra.string import pad, enclose_circled, bold, str_round
from cassandra.plot import get_acf, get_fft_inter, plt, set_plot_window
from scipy.signal import find_peaks 
import numpy as np


class season_class(trend_class):
    def __init__(self):
        self.set_periods()
        trend_class.__init__(self)

    def set_periods(self, periods = None):
        self.periods = periods if periods is not None else []
      
    def fit_function(self, time, values, periods, detrend = None):
        y = values.data.copy()
        y = remove_trend(y, detrend)
        functions = []
        for period in periods:
            function = get_season_function(y, period) #+ trend
            functions.append(function)
        function = lambda el: np.sum([function(el) for function in functions])
        function = to_time_function(function)
        self.set_function(function)
        
    def fit(self, time, values, periods, detrend):
        periods = [p for p in periods if p not in [0, 1]]
        self.fit_function(time, values, periods, detrend)
        self.set_periods(periods)
        self.set_order(detrend)
        self.update_label()

    def update_label(self):
        no_label = self.periods is None or len(self.periods) == 0
        self.update_label_short(no_label)
        self.update_label_long(no_label)
        
    def update_label_short(self, no_label):
        label = "Season" + enclose_circled(', '.join(map(str,self.periods)))
        self.label_short = None if no_label else label

    def update_label_long(self, no_label):
        periods = list(map(str, self.periods))
        single_period = len(self.periods) == 1
        periods_string = "period = " if single_period else "periods = "
        periods_list = str(self.periods[0]) if single_period else enclose_circled(', '.join(periods))
        periods = periods_string + periods_list
        detrend = "detrend = " + str(self.order)
        label = pad("Season", 11) + periods + ", " + detrend
        self.label_long = None if no_label else label

    def project(self, time):
        new = self.copy()
        new.update_data(time)
        #new.update_label()
        return new


# Season Utilities
transpose = lambda matrix: list(map(list, zip(*matrix)))

def get_season_function(data, season):
    data = get_partial_season(data, season)
    function = lambda el: data[el % season]
    return function

def get_season(data, season):
    return repeat(get_partial_season(data, season), len(data))

def deseason(data, season):
    data = np.array(data) - get_season(data, season)
    #data = moving_average(data, season)
    return data

def get_partial_season(data, season):
    season = [np.mean(data[i : : season]) for i in range(season)]
    return np.array(season) #- np.mean(season)

def repeat(data, length):
    l = len(data)
    data = np.tile(data, (length // l) + 1)
    return data[ : length]

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

def find_seasons(data, detrend_order = None, source = "acf", log = True, plot = True, threshold = 2.5):
    proceed_manually = (plot == 1)
    length = len(data)
    source = "acf" if "a" in source else "fft"
    use_acf = source == "acf"

    data = remove_trend(data, detrend_order)
    
    acf_data = get_acf(data)
    peaks_data = acf_data if use_acf else get_fft_inter(acf_data)

    lower, upper = 2, length // (2 if use_acf else 3)
    x = range(lower, upper + 1)
    peaks_data = [peaks_data[i] for i in x]
    mean, std = np.mean(peaks_data), np.std(peaks_data)
    peaks_data = [(el - mean)/ std for el in peaks_data]
        
    peaks = get_peaks(peaks_data, threshold, 1)

    lp = len(peaks)
    (seasons, heights, _) = transpose(peaks) if lp != 0 else [[]] * 3
    seasons = [el + lower for el in seasons]

    if log:
        print(bold("searching seasons") + " in " + source)
        print("detrend order", detrend_order) if log else None
        for i in range(lp):
            season =  bold(pad(str(seasons[i]), 3))
            height =  pad(str_round(heights[i], 1), 3)
            print("season", bold(season), "height", height, "[stds]")
        if lp == 0:
            print("no peaks found: see ya!") if log else None

    if plot:
        set_plot_window()
        title = "AutoCorrelation Plot" if use_acf else "FFT Plot"
        plt.clf()
        plt.plot(x, peaks_data)
        plt.title(title)
        #plt.xscale("log") if not use_acf else None
        for season in seasons:
            plt.axvline(x = season, c = "g", lw = 1)
        plt.axhline(y = threshold, c = "r", lw = 1)
        plt.xlim(lower - 1, upper + 1)
        #plt.ylim(0, 1.05)
        plt.xlabel("Season")
        plt.show(block = 0)

    return seasons

def generate_season(season, amplitude, length, order = 4, noise = 1):
    repeat = length // season + 1
    signal = [generate_trend(0, amplitude, season, order, noise)] * repeat
    signal = flatten(signal)
    return np.array(signal[ : length])

def flatten(matrix): # flatten lists at first level
    return [el for row in matrix for el in row]
