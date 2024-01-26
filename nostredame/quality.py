from nostredame.backup import copy_class
import numpy as np


class quality_class(copy_class):
    def __init__(self, digits):
        self.digits = digits
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
        label =    'RMS ' + self.get_rms_string()
        label += '| R2 '  + self.get_r2_string()
        label += '| MAPE ' + self.get_mape_string()
        self.label = label

    def get_rms_string(self):
        rms = 'nan' if self.rms is None else 'bad' if self.rms < -99 else ('{:' + str(self.digits) + '.2f}').format(self.rms) 
        return rms.ljust(self.digits + 4)

    def get_r2_string(self):
        r2 = 'nan' if self.r2 is None else 'bad' if self.r2 < -99 else '{:2.2f}'.format(self.r2)
        return r2.ljust(7)
    
    def get_mape_string(self):
        mape = 'nan' if self.mape is None else 'bad' if self.mape > 100 else '{:3.2f}'.format(self.mape)
        return mape.ljust(6)


        
# Utilities
rms_quality = lambda true, pred: rms(true - pred)
mape = lambda true, pred: np.mean(np.abs(true - pred) / true)
r2 = lambda true, pred: (1 - (rms(true - pred) / np.std(true)) ** 2)

rms = lambda data: np.mean(np.array(data) ** 2) ** 0.5

function_names = ['rms', 'mape', 'r2']
functions = [rms_quality, mape, r2]

