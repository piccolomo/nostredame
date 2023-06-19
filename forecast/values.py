from forecast.backup import copy_class
#from plot_classes import values_plot
import forecast.tools as tl
import numpy as np

class values_class(copy_class):
    def __init__(self, data = []):
        self.set(data)
        #self.sorted = False
        super().__init__()
        
    def set(self, data):
        self.data = np.array(data) #if tl.is_like_list(data) else zero(self.length) + data
        self.update_metrics()
        return self

    def update_metrics(self):
        self.length = self.l = len(self.data)
        self.max = max(self.data) if self.length > 0 else None
        self.min = min(self.data) if self.length > 0 else None
        self.delta = self.max - self.min if self.length > 0 else None
        self.first = self.data[0] if self.length > 0 else None
        self.last = self.data[-1] if self.length > 0 else None
        self.mean = np.mean(self.data) if self.length > 0 else None
        self.rms = tl.rms(self.data) if self.length > 0 else None
        self.std = np.std(self.data) if self.length > 0 else None
        data = list(self.data) + [self.mean, self.std, self.rms]
        self.pad_length = max([len(tl.str_round(el, 2)) for el in data])

    def __mul__(self, constant):
        return self.copy().set(self.data * constant)

    def forecast(self, length):
        return values_class([tl.nan] * length)

    def append(self, values):
        data = np.concatenate((self.data, values.data))
        return values_class(data)

    def extend(self, length):
        return self.append(self.forecast(length))

    def part(self, begin, end):
        data = self.data[begin : end]
        new = values_class(data)
        return new

    def white(self):
        return self.set(np.random.normal(self.mean, self.std, self.length))


    # def __truediv__(self, constant):
    #     return self * (1 / constant)


    # def sort(self, index_to_sort):
    #     if not self.sorted:
    #         self.data = [self.data[i] for i in index_to_sort]
    #         self.array = self.array[index_to_sort]
    #         self.sorted = True

    # def split(self, size):
    #     train, test = self.split_method(size)
    #     train.update_metrics(); test.update_metrics();
    #     return train, test
    
    # def set(self, data):
    #     data = list(data) 
    #     self.set_data(data)

    # def add(self, data): # add vertically
    #     return self.set(self.array + np.array(data))

    # def sub(self, data):
    #     return self.add(-np.array(data))

    # def invert(self):
    #     self.set(-self.array)
    #     return self
    
    # def zero(self):
    #     return self.set(zero(self.length))
    
    # def white(self):
    #     return self.set(np.random.normal(self.mean, self.std, self.length))

    # def append(self, values): # add horizontally
    #     self.copy_from(self + values)

    # def __add__(self, values):
    #     return values_class(self.data + values.data)

    # def __len__(self):
    #     return self.length
