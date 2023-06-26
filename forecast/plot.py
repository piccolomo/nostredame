from forecast.string import platform, enclose_squared
from scipy.interpolate import interp1d as interpolate
from statsmodels.tsa.stattools import acf
from scipy.fft import rfft as rfft 
import matplotlib.pyplot as plt
from math import ceil
import numpy as np
import os


width_data = 1.5
width_back = 1
#alpha = 0.6

color_data = "steelblue"
#color_back = "sienna"
color_back = "forestgreen"


class plot_class():
    def __init__(self):
        pass

    def plot(self):
        self._update_label()
        set_plot_size()
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
        set_plot_size()
        plt.clf()
        plt.plot(get_acf(self.get_residuals()), c = color_data, lw = width_data)
        plt.xlabel("Period")
        #plt.ylabel("ACF")
        plt.title("Autocorrelation Plot of " + self._residuals_label.title())
        show()
        return self

    def plot_fft(self):
        set_plot_size()
        plt.clf()
        plt.plot(get_fft_inter(self.get_residuals()), c = color_data, lw = width_data)
        #plt.yscale("log")
        plt.xlabel("Period")
        #plt.ylabel("FFT")
        plt.title("Fourier Plot of " + self._residuals_label.title())
        show()
        return self

    def save_plot(self, name = None):
        path = self._get_path(name) + ".jpg"
        #sleep(0.5)
        plt.savefig(path)

        
# Plot Utilities
def get_screen_size():
    try:
        if platform == "unix":
            process = os.popen("xrandr -q -d :0")
            screen = process.readlines()[0]
            process.close()
            width = screen.split()[7]
            height = screen.split()[9][:-1]
        elif platform == "windows":
            #process = os.popen("wmic desktopmonitor get screenheight, screenwidth")
            process = os.popen("wmic PATH Win32_VideoController GET CurrentVerticalResolution,CurrentHorizontalResolution")
            lines = process.readlines()
            process.close()
            #height, width = lines[4].split()
            width, height = lines[4].split()
        else:
            height, width = None, None
        width, height = int(width), int(height)
    except:
        width, height = 1920, 1080
        print("screen size failed in", platform, ": defaulting to", width, height)
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
