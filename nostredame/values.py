from nostredame.backup import copy_class
import numpy as np

class values_class(copy_class):
    def __init__(self, data = []):
        self.set(data)
        super().__init__()
        
    def set(self, data):
        self.data = np.array(data)
        self.update_metrics()
        return self

    def update_metrics(self):
        self.length = self.l = len(self.data)
        self.first = self.data[0] if self.length > 0 else None
        self.last = self.data[-1] if self.length > 0 else None
        self.mean = np.mean(self.data) if self.length > 0 else None
        self.min = np.nanmin(self.data)
        self.max = np.nanmax(self.data)
        data = [len(str(int(el))) for el in self.data if not np.isnan(el)]
        self.digits = max(data, default = 0)

    def forecast(self, length):
        return values_class(np.zeros(length) * np.nan)

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

    def add(self, data):
        self.set(self.data + data)

