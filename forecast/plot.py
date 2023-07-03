from forecast.string import enclose_squared
from forecast.platform import platform, get_screen_size
from scipy.interpolate import interp1d as interpolate
from statsmodels.tsa.stattools import acf
from scipy.fft import rfft as rfft 
import matplotlib.pyplot as plt
from matplotlib import rcParams as plot_parameters
from math import ceil
import numpy as np
import os



w, h = get_screen_size()
tbh = round(0.08 * h) # toolbar height
pw, ph = 3 * w // 4, 3 * (h - tbh) // 4

width_data = round(1.2  * w / 1600)
width_back = round(1.00 * w / 1600)
font_size = round(pw / 90)

color_data = "steelblue"
#color_back = "sienna"
color_back = "forestgreen"


class plot_class():
    def __init__(self):
        pass

    def plot(self):
        self._update_label()
        x, y = self.get_time(), self.get_data()
        yb = self.get_background()
        
        name = self.get_name()
        unit = enclose_squared(self.get_unit())
        xlabel = "Time" #+ enclose(self.time.form.replace('%', ''))
        ylabel = name + " " + unit

        set_plot(name)
        plt.plot(x, y, c = color_data, lw = width_data, label = name)
        plt.plot(x, yb, c = color_back, lw = width_back, label = self._label_short) if self.background_ok else None

        plt.ylabel(ylabel)
        plt.legend()
        show()
        return self

    def plot_acf(self):
        title = "Autocorrelation Plot of " + self._residuals_label.title()
        set_plot(title)
        plt.plot(get_acf(self.get_residuals()), c = color_data, lw = width_data)
        plt.xlabel("Period")
        #plt.ylabel("ACF")
        show()
        return self

    def plot_fft(self):
        title = "Fourier Plot of " + self._residuals_label.title()
        set_plot(title)
        plt.plot(get_fft_inter(self.get_residuals()), c = color_data, lw = width_data)
        #plt.yscale("log")
        plt.xlabel("Period")
        #plt.ylabel("FFT")
        show()
        return self

    def save_plot(self, name = None, log = True):
        path = self._get_path(name) + ".jpg"
        #sleep(0.5)
        plt.savefig(path)
        print("plot saved in", path) if log else None
        return self

    
def set_plot(title):
    plot_parameters['toolbar'] = 'None'
    fig = plt.figure(constrained_layout = True)
    style = plt.style.available[-2]
    plt.style.use(style)
    plt.rcParams.update({'font.size': font_size, "font.family": "sans-serif"})

    mngr = plt.get_current_fig_manager();
    mngr.set_window_title(title)

    try:
        size_temp = "{}x{}+{}+{}".format(pw//2, ph//2, 0, h - ph - tbh)
        mngr.window.geometry(size_temp); show()
        size = "{}x{}+{}+{}".format(pw, ph, 0, h - ph - tbh)
        mngr.window.geometry(size); show()
    except:
        print("Unable to set plot window size using window.geometry()")

    plt.clf()
    plt.title(title)
    

def show():
    plt.pause(0.01);
    plt.show(block = 0)

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
