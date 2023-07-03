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

width_data = round(1.2  * w / 1600)
width_back = round(1.00 * w / 1600)
font_size = round(w / 120)

color_data = "steelblue"
#color_back = "sienna"
color_back = "forestgreen"


class plot_class():
    def __init__(self):
        pass

    def plot(self):
        self._update_label()
        set_plot()
        x, y = self.get_time(), self.get_data()
        yb = self.get_background()
        
        name = self.get_name()
        unit = enclose_squared(self.get_unit())
        xlabel = "Time" #+ enclose(self.time.form.replace('%', ''))
        ylabel = name + " " + unit

        plt.clf()
        plt.plot(x, y, c = color_data, lw = width_data, label = name)
        plt.plot(x, yb, c = color_back, lw = width_back, label = self._label_short) if self.background_ok else None

        plt.ylabel(ylabel)
        plt.title(name)

        plt.legend()
        show()
        return self

    def plot_acf(self):
        set_plot()
        plt.clf()
        plt.plot(get_acf(self.get_residuals()), c = color_data, lw = width_data)
        plt.xlabel("Period")
        #plt.ylabel("ACF")
        plt.title("Autocorrelation Plot of " + self._residuals_label.title())
        show()
        return self

    def plot_fft(self):
        set_plot()
        plt.clf()
        plt.plot(get_fft_inter(self.get_residuals()), c = color_data, lw = width_data)
        #plt.yscale("log")
        plt.xlabel("Period")
        #plt.ylabel("FFT")
        plt.title("Fourier Plot of " + self._residuals_label.title())
        show()
        return self

    def save_plot(self, name = None, log = True):
        path = self._get_path(name) + ".jpg"
        #sleep(0.5)
        plt.savefig(path)
        print("plot saved in", path) if log else None
        return self

    
def set_plot():
    plot_parameters['toolbar'] = 'None'
    fig = plt.figure(0, constrained_layout = True)
    style = plt.style.available[-2]
    plt.style.use(style)

    plt.show(block = 0)
    mngr = plt.get_current_fig_manager();
    #x, y = get_screen_size()
    try:
        mngr.window.maximize()
    except:
        size = "{}x{}+{}+{}".format(w, h, 0, 0)
        mngr.window.geometry(size)
        
    mngr.set_window_title("Forecast Plot")
    #mngr.resize(x, y)
    #mngr.full_screen_toogle()

    plt.rcParams.update({'font.size': font_size, "font.family": "sans-serif"})

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
