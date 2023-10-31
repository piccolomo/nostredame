from cassandra.backup import copy_class
import numpy as np

class quality_class(copy_class):
    def __init__(self):
        self.zero()

    def zero(self):
        self.set()
        self.update_label()

    def set(self, true = None, pred = None):
        data_ok = true is not None and pred is not None
        self.rms = rms_quality(true, pred) if data_ok else None
        self.mape = 100 * mape(true, pred) if data_ok else None
        self.r2 = 100 * r2(true, pred) if data_ok else None

    def update_label(self):
        self.label = None if self.rms is None else 'RMS {:4.2f}'.format(self.rms) + ' | R2 {:+4.2f}'.format(self.r2) + ' | MAPE {:3.2f}'.format(self.mape)

        
# Utilities
rms_quality = lambda true, pred: rms(true - pred)
mape = lambda true, pred: np.mean(np.abs(true - pred) / true)
r2 = lambda true, pred: (1 - (rms(true - pred) / np.std(true)) ** 2)

rms = lambda data: np.mean(np.array(data) ** 2) ** 0.5

function_names = ['rms', 'mape', 'r2']
functions = [rms_quality, mape, r2]

