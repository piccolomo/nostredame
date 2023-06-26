from forecast.values import rms, mean, has_nan
from forecast.backup import copy_class

from forecast.string import is_like_list, pad_round, pad, nl, percentage
from sklearn.metrics import mean_absolute_percentage_error as mape
from sklearn.metrics import r2_score as r2

import numpy as np


class quality_class(copy_class):
    def __init__(self):
        self.zero()

    def zero(self):
        self.update([], [])

    def update(self, y_true, y_pred):
        self.r2, self.mape, self.rms = get_qualities(y_true, y_pred)
        self.ir2 = 1 - self.r2
        self.rms_length = len(str(round(self.rms, 2)))
        self.update_label()


    def update_label(self):
        self.update_short_label()
        self.update_long_label()

    def update_short_label(self):
        label  =  "Mape " + self.get_mape_label(5) + " %"
        label += " iR2 "  + self.get_ir2_label(5) + " %"
        label += " Rms "  + self.get_rms_label()
        self.short_label = label

    def update_long_label(self):
        label =  pad("Mape", 11)   + self.get_mape_label() + " %" + nl
        label += pad("iR2", 11) + self.get_ir2_label()  + " %" + nl
        label += pad("Rms", 11)    + self.get_rms_label()
        self.long_label = label
        
    def get_mape_label(self, length = 5):
        return pad_round(percentage(self.mape), length) 

    def get_ir2_label(self, length = 5):
        return pad_round(percentage(self.ir2), length)

    def get_rms_label(self, length = 5):
        return pad_round(self.rms, length)
        
    def __str__(self):
        #self.update_label()
        return self.long_label


# Utilities
nan = np.nan
no_nan = lambda data: not has_nan(data)

def get_qualities(y_true, y_pred):
    length = len(y_true)
    good_data = no_nan(y_pred) and no_nan(y_true) and length > 0
        
    r2_score = r2(y_true, y_pred) if good_data else nan
    mape_score = mape(y_true, y_pred) if good_data else nan
    rms_score = rms(y_true - y_pred) if good_data else nan
    
    return r2_score, mape_score, rms_score
