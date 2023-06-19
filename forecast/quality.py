import forecast.tools as tl
from forecast.backup import copy_class
# from prettytable import PrettyTable

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
        label  =  "Mape " + self.get_mape_string(5) + " %"
        label += " iR2 "  + self.get_ir2_string(5) + " %"
        label += " Rms "  + self.get_rms_string()
        self.short_label = label

    def update_long_label(self):
        label =  tl.pad("Mape", 11)   + self.get_mape_string() + " %" + tl.nl
        label += tl.pad("iR2", 11) + self.get_ir2_string()  + " %" + tl.nl
        label += tl.pad("Rms", 11)    + self.get_rms_string()
        self.long_label = label
        
    def get_mape_string(self, length = 5):
        return tl.pad_round(tl.percentage(self.mape), length) 

    def get_ir2_string(self, length = 5):
        return tl.pad_round(tl.percentage(self.ir2), length)

    def get_rms_string(self, length = 5):
        return tl.pad_round(self.rms, length)
        
    def __str__(self):
        #self.update_label()
        return self.long_label
    
def get_qualities(y_true, y_pred):
    length = len(y_true)
    good_data = tl.no_nan(y_pred) and tl.no_nan(y_true) and length > 0
        
    ir2 = tl.r2(y_true, y_pred) if good_data else tl.nan
    mape = tl.mape(y_true, y_pred) if good_data else tl.nan
    rms = tl.rms(y_true - y_pred) if good_data else tl.nan
    
    return ir2, mape, rms

def mean_quality(qualities, weights):
    new = quality_class()
    new.r2 = tl.mean([el.r2 for el in qualities], weights)
    new.ir2 = tl.mean([el.ir2 for el in qualities], weights)
    new.mape = tl.mean([el.mape for el in qualities], weights)
    new.rms = tl.mean([el.rms for el in qualities], weights)
    new.update_label()
    return new
