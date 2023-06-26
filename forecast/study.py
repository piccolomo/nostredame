from forecast.string import bold, pad, nl, percentage, pad_round


sl = 3
sp = ' ' * sl


class study_class():
    def __init__(self, data, test_length = None, method = "Data"):
        self.data = data.copy()
        self.set_name()
        self.set_test_length(test_length)
        self.set_method(method)
        self.update()

    def set_name(self):
        self.name = None if self.data.name is None else self.data.name + " study"

    def set_method(self, method):
        self.method = method if method in ["data", "train", "test", "Data", "average"] else "Data"

    def set_test_length(self, test_length):
        self.test_length = self.data.test_length if test_length is None else test_length if test_length > 1 else round(test_length * self.data.l)

    def update(self):
        self.update_split()
        self.update_quality()
        self.update_label()

    def update_split(self, test_length = None):
        self.train, self.test = self.data.split(self.test_length, retrain = True)
        self.Data = self.train.append(self.test)
        self.datas = [self.data, self.train, self.test, self.Data]

    def get_name(self):
        return self.name.title() if self.name is not None else "Study"

    def update_quality(self):
        if self.method == "data":
            self.quality = self.data._quality.rms
        elif self.method == "train":
            self.quality = self.train._quality.rms
        elif self.method == "test":
            self.quality = self.test._quality.rms
        elif self.method == "Data":
            self.quality = self.Data._quality.rms
        elif self.method == "average":
            self.quality = 0.5 * self.train._quality.rms + 0.5 * self.test._quality.rms
        
    def update_label(self):
        self._update_label_short()
        self._update_label_long()

    def _update_label_short(self):
        mape = bold('mape') + sp + self.get_mape_label() + ' [%]' + sp
        mape_title = ' ' * (4 + sl) + self.get_title_label() + ' ' * (4 + sl)
        
        ir2 = bold('ir2') + sp + self.get_ir2_label() + ' [%]' + sp
        ir2_title = ' ' * (3 + sl) +  self.get_title_label() + ' ' * (4 + sl)

        rms_length = self.data._values.pad_length
        rms = bold('rms') + sp + self.get_rms_label(rms_length) + ' ' + self.data.get_unit(True)
        rms_title = ' ' * (3 + sl) + self.get_title_label(rms_length)

        #self._label_short_title = mape_title + ir2_title + rms_title
        self._label_short_title = rms_title
        #self._label_short = mape + ir2 + rms
        self._label_short = rms

    def get_length_label(self):
        train_length, test_length = percentage(self.train.l, self.data.l), percentage(self.test.l, self.data.l)
        return "test size: " + pad_round(test_length, 5) + "%"#" = " + str(self.test.l)

    def get_title_label(self, pad_length = 6):
        datas = ["data",  "Train", "Test", "Data"]
        return sp.join([bold(pad(el, pad_length)) for el in datas])
        
    def get_mape_label(self, pad_length = 6):
        mape = [el._quality.get_mape_label(pad_length) for el in self.datas]
        mape = sp.join(mape)
        return mape

    def get_ir2_label(self, pad_length = 6):
        ir2 = [el._quality.get_ir2_label(pad_length) for el in self.datas]
        ir2 = sp.join(ir2) 
        return ir2

    def get_rms_label(self, pad_length = None):
        rms = [el._quality.get_rms_label(pad_length) for el in self.datas]
        rms = sp.join(rms)
        return rms
        
    def _update_label_long(self):
        #back = self.data._label_long + nl
        length = self.get_length_label() + nl
        rms_length = self.data._values.pad_length
        title = ' ' * (4 + sl) +  self.get_title_label(rms_length) + nl
        mape = bold('mape') + sp + self.get_mape_label(rms_length) + ' [%]' + sp + nl
        ir2 = bold('ir2 ') + sp + self.get_ir2_label(rms_length) + ' [%]' + sp + nl
        rms = bold('rms ') + sp + self.get_rms_label(rms_length) + ' ' + self.data.get_unit(True)
        self._label_long = length + title + mape + ir2 + rms

    def __str__(self):
        title = bold(self.get_name().title() + " Log")
        return title + nl + self._label_long
        
    def log(self):
        self.update_label()
        print(self)    
