from cassandra.backup import copy_class
import numpy as np

class quality_class(copy_class):
    def __init__(self):
        self.zero()

    def zero(self):
        self.set_function()
        self.set()
        self.update_label()

    def set_function(self, name = 'rms'):
        self.function_name = name if name in function_names else 'rms'
        self.function = functions[function_names.index(name)]

    def update_label(self):
        self.label = self.function_name + ': ' + str(round(self.quality, 2))

    def set(self, true = None, pred = None):
        data_ok = true is not None and pred is not None
        self.quality = self.function(true, pred) if data_ok else np.nan

# Utilities

rms_quality = lambda true, pred: rms(true - pred)
mape = lambda true, pred: np.mean(np.abs(true - pred) / true)
r2 = lambda true, pred: (1 - (rms(true - pred) / np.std(true)) ** 2)

rms = lambda data: np.mean(np.array(data) ** 2) ** 0.5

function_names = ['rms', 'mape', 'r2']
functions = [rms_quality, mape, r2]

