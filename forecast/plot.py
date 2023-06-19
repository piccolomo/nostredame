from forecast.tools import plt, enclose_squared, get_acf, get_fft_inter, set_plot_size
from time import sleep

width_data = 1.5
width_back = 1
#alpha = 0.6

color_data = "steelblue"
#color_back = "sienna"
color_back = "forestgreen"

class plot_data():
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
        title = "Data" if self.name is None else self.name.title()

        plt.clf()
        plt.plot(x, y, c = color_data, lw = width_data, label = self.name)
        plt.plot(x, yb, c = color_back, lw = width_back, label = self._short_label) if self.background_ok else None

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)

        plt.legend()
        plt.show(block = 0)
        return self

    def plot_acf(self):
        set_plot_size()
        plt.clf()
        plt.plot(get_acf(self.get_residuals()), c = color_data, lw = width_data)
        plt.xlabel("Period")
        plt.ylabel("ACF")
        plt.title("Autocorrelation Plot of " + self._residuals_label)
        plt.show(block = 0)
        return self

    def plot_fft(self):
        set_plot_size()
        plt.clf()
        plt.plot(get_fft_inter(self.get_residuals()), c = color_data, lw = width_data)
        #plt.yscale("log")
        plt.xlabel("Period")
        plt.ylabel("FFT")
        plt.title("Fourier Plot of " + self._residuals_label)
        plt.show(block = 0)
        return self

    def save_plot(self, name = None):
        path = self._get_path(name) + ".jpg"
        sleep(0.5)
        plt.savefig(path)
