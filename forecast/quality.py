from forecast.values import rms, mean, has_nan
from forecast.backup import copy_class

from forecast.string import is_like_list, str_round, pad, nl, percentage
#from sklearn.metrics import mean_absolute_percentage_error as mape
#from sklearn.metrics import r2_score as r2

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
        self.update_label_short()
        self.update_label_long()

    def update_label_short(self):
        label  =  "Mape " + self.get_mape() + " %"
        label += " iR2 "  + self.get_ir2() + " %"
        label += " Rms "  + self.get_rms()
        self.label_short = label

    def update_label_long(self):
        label =  pad("Mape", 5) + self.get_mape() + " %" + nl
        label += pad("iR2",  5) + self.get_ir2()  + " %" + nl
        label += pad("Rms",  5) + self.get_rms()
        self.label_long = label
        
    def get_mape(self):
        return str_round(percentage(self.mape), 2) 

    def get_ir2(self):
        return str_round(percentage(self.ir2), 2)

    def get_rms(self):
        return str_round(self.rms, 2)
        
    def __str__(self):
        #self.update_label()
        return self.label_long


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

def mape(true, pred):
    # true = np.array(true)
    # pred = np.array(pred)
    # non_zero = true != 0
    # true = true[non_zero]
    # pred = pred[non_zero]
    error = np.abs(true - pred)
    mape = error / true
    return np.mean(mape)

def r2(true, pred):
    return 1 - (rms(true - pred) / np.std(true)) ** 2
