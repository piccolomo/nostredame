from cassandra.string import enclose_squared
from scipy.interpolate import interp1d as interpolate
from matplotlib import rcParams as plot_parameters
from statsmodels.tsa.stattools import acf
from scipy.fft import rfft as rfft 
import matplotlib.pyplot as plt
from textwrap import wrap
from math import ceil
import numpy as np
import os


#color_data, color_back = "saddlebrown", "steelblue"
color_data, color_back = "black", "darkorchid"
# # "darkblue"
# color_data = "black"
# color_data = "navy"
# color_data = "teal"
# color_data = "steelblue"
# color_data = 
# #color_back = "sienna"
# color_back = "limegreen"
# color_back = "darkorchid"
# color_back = 



class plot_class():
    def plot(self):
        set_plot_window()
        self._update_label()
        x, y = self.get_time(), self.get_data()
        yb = self.get_background()
        
        name = self.get_name()
        unit = enclose_squared(self.get_unit())
        xlabel = "Time" #+ enclose(self.time.form.replace('%', ''))
        ylabel = name + " " + unit
        label_back = '\n'.join(wrap(self._label_short, wrap_length))

        plt.clf()
        plt.plot(x, y, c = color_data, lw = width_data, label = name)
        plt.plot(x, yb, c = color_back, lw = width_back, label = label_back) if self.background_ok else None

        plt.title(name)
        plt.ylabel(ylabel)
        plt.legend()
        plt.pause(0.01); plt.show(block = 0)
        return self

    def plot_acf(self):
        title = "Autocorrelation Plot of " + self._residuals_label.title()
        set_plot_window()
        plt.clf()
        plt.plot(get_acf(self.get_residuals()), c = color_data, lw = width_data)
        plt.title(title)
        plt.xlabel("Period")
        #plt.ylabel("ACF")
        plt.pause(0.01); plt.show(block = 0)
        return self

    def plot_fft(self):
        title = "Fourier Plot of " + self._residuals_label.title()
        set_plot_window()
        plt.clf()
        plt.plot(get_fft_inter(self.get_residuals()), c = color_data, lw = width_data)
        plt.title(title)
        #plt.yscale("log")
        plt.xlabel("Period")
        #plt.ylabel("FFT")
        plt.pause(0.01); plt.show(block = 0)
        return self

    def save_plot(self, name = None, log = True):
        path = self._get_path(name) + ".jpg"
        #sleep(0.5)
        plt.savefig(path)
        print("plot saved in", path) if log else None
        return self

def set_plot_window():
    from cassandra.platform import get_screen_size
    width, height = get_screen_size()
    global width_data, width_back, wrap_length
    
    toolbar_height = round(0.08 * height) # toolbar height
    plot_width = 3 * width // 4
    plot_height = 3 * (height - 0 * toolbar_height) // 4

    font_size = round(plot_width / 120)
    width_data = plot_width / 1100
    width_back = plot_width / 1100
    wrap_length = round(0.6 * plot_width / font_size)
    
    plot_parameters['toolbar'] = 'None'
    fig = plt.figure(constrained_layout = True)
        
    mngr = plt.get_current_fig_manager()
    try:
        y = height - plot_height - toolbar_height
        size_temp = "{}x{}+{}+{}".format(plot_width // 2, plot_height // 2, 0, y)
        mngr.window.geometry(size_temp); plt.pause(0.01); plt.show(block = 0)
        size = "{}x{}+{}+{}".format(plot_width, plot_height, 0, y)
        mngr.window.geometry(size)
    except:
        print("Unable to set plot window size using window.geometry()")

    # Window Style
    style = plt.style.available[-2]
    plt.style.use(style)
    plt.rcParams.update({'font.size': font_size, "font.family": "sans-serif"})
    mngr = plt.get_current_fig_manager()
    mngr.set_window_title("Forecast Plot")

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
