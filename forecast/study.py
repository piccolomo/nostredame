from forecast.string import bold, pad, nl, percentage, pad_round


sl = 3
sp = ' ' * sl


class study_class():
    def __init__(self, data):
        self.data = data.copy()
        self.set_name()
        self.update()

    def update(self):
        self.update_split()
        self.update_quality()
        self.update_label()

    def update_split(self):
        self.train, self.test = self.data.split(retrain = True)
        self.Data = self.train.append(self.test)
        self.datas = [self.data, self.train, self.test, self.Data]

    def set_name(self):
        self.name = None if self.data.name is None else self.data.name + " study"

    def get_name(self):
        return self.name.title() if self.name is not None else "Study"

    def update_quality(self):
        self.quality = self.test._quality.rms
        #self.quality = self.test._quality.rms
        
    def update_label(self):
        self._update_short_label()
        self._update_long_label()

    def _update_short_label(self):
        mape = bold('mape') + sp + self.get_mape_string() + ' [%]' + sp
        mape_title = ' ' * (4 + sl) + self.get_title_string() + ' ' * (4 + sl)
        
        ir2 = bold('ir2') + sp + self.get_ir2_string() + ' [%]' + sp
        ir2_title = ' ' * (3 + sl) +  self.get_title_string() + ' ' * (4 + sl)

        rms_length = self.data._values.pad_length
        rms = bold('rms') + sp + self.get_rms_string(rms_length) + ' ' + self.data.get_unit(True)
        rms_title = ' ' * (3 + sl) + self.get_title_string(rms_length)

        #self._short_label_title = mape_title + ir2_title + rms_title
        self._short_label_title = rms_title
        #self._short_label = mape + ir2 + rms
        self._short_label = rms

    def get_length_string(self):
        train_length, test_length = percentage(self.train.l, self.data.l), percentage(self.test.l, self.data.l)
        return "test size: " + pad_round(test_length, 5) + "%"#" = " + str(self.test.l)

    def get_title_string(self, pad_length = 6):
        datas = ["data",  "Train", "Test", "Data"]
        return sp.join([bold(pad(el, pad_length)) for el in datas])
        
    def get_mape_string(self, pad_length = 6):
        mape = [el._quality.get_mape_string(pad_length) for el in self.datas]
        mape = sp.join(mape)
        return mape

    def get_ir2_string(self, pad_length = 6):
        ir2 = [el._quality.get_ir2_string(6) for el in self.datas]
        ir2 = sp.join(ir2) 
        return ir2

    def get_rms_string(self, pad_length = None):
        rms = [el._quality.get_rms_string(pad_length) for el in self.datas]
        rms = sp.join(rms)
        return rms
        
    def _update_long_label(self):
        #back = self.data._label_long + nl
        length = self.get_length_string() + nl
        rms_length = self.data._values.pad_length
        title = ' ' * (4 + sl) +  self.get_title_string(rms_length) + nl
        mape = bold('mape') + sp + self.get_mape_string(rms_length) + ' [%]' + sp + nl
        ir2 = bold('ir2 ') + sp + self.get_ir2_string(rms_length) + ' [%]' + sp + nl
        rms = bold('rms ') + sp + self.get_rms_string(rms_length) + ' ' + self.data.get_unit(True)
        self._long_label = length + title + mape + ir2 + rms

    def __str__(self):
        title = bold(self.get_name().title() + " Log")
        return title + nl + self._long_label
        
    def log(self):
        self.update_label()
        print(self)    
