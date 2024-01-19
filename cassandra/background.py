from cassandra.trend import trend_class, np
from cassandra.season import season_class
from cassandra.prediction import prediction_class
from cassandra.list import find_seasons, get_minimum


class background_class():
    def __init__(self):
        self.trend = trend_class()
        self.season = season_class()
        self.prediction = prediction_class()

        
    def zero(self):
        self.zero_trend()
        self.zero_season()
        self.zero_prediction()
        return self

    def zero_trend(self):
        self.trend.zero()
        return self

    def zero_season(self):
        self.season.zero()
        return self

    def zero_prediction(self):
        self.prediction.zero()
        return self

    def fit_trend(self, data, order):
        self.trend.fit(data, order)

    def fit_seasons(self, data, periods):
        self.season.fit(self.get_trend_residuals(data), periods)

    def fit_naive(self, data, level = 'mean'):
        self.prediction.set_naive(level)
        self.fit_predictor(data)
        return self
     
    def fit_es(self, data, period):
        self.prediction.set_es(period)
        self.fit_predictor(data)
        return self

    def fit_predictor(self, data):
        self.prediction.fit(self.get_season_residuals(data))
    
    def retrain(self, data):
        self.fit_trend(data, self.trend.order) if self.trend.order is not None else None
        self.fit_seasons(data, self.season.periods) if self.season.periods is not None else None
        self.fit_predictor(data)


    def update_label(self):
        self.trend.update_label()
        self.season.update_label()
        self.prediction.update_label()
        labels = [self.trend.label, self.season.label, self.prediction.label]
        labels = [l for l in labels if l is not None]
        self.label = None if len(labels) == 0 else ' + '.join(labels)

        
    def project(self, time):
        new = background_class()
        new.trend = self.trend.project(time)
        new.season = self.season.project(time)
        new.prediction = self.prediction.project(time)
        return new

    def part(self, begin, end):
        new = background_class()
        new.trend = self.trend.part(begin, end)
        new.season = self.season.part(begin, end)
        new.prediction = self.prediction.part(begin, end)
        return new

    def append(self, background):
        new = self.copy()
        new.trend = new.trend.append(background.trend)
        new.season = new.season.append(background.season)
        new.prediction = new.prediction.append(background.prediction)
        return new

    def copy(self):
        new = background_class()
        new.trend = self.trend.copy()
        new.season = self.season.copy()
        new.prediction = self.prediction.copy()
        return new


    def find_seasons(self, data, threshold = 0, detrend = 3, log = True):
        data = data.get_data()
        return find_seasons(data, threshold, detrend, log)

    methods = ['data', 'Data', 'train', 'test']
    
    def find_trend(self, data, method = 'test', order = 5, log = True):
        method_index = self.methods.index(method) if method in self.methods else 3
        d = data.copy()#.zero_background()
        trends = range(0, order + 1)
        qualities = []
        for trend in trends:
            d.fit_trend(trend)
            T, t = d.split(retrain = True)
            D = T.append(t); D.set_name(data.get_name(), 'Train + Test'); D.update_label();
            (d.print(), D.print(), T.print(),  t.print(),  print()) if log else None
            quality = [d.quality.rms, D.quality.rms, T.quality.rms, t.quality.rms][method_index]
            qualities.append(quality)
        return get_minimum(trends, qualities)

    def find_es(self, data, method = 'data', depth = 2, log = True):
        method_index = self.methods.index(method) if method in self.methods else 3
        d = data.copy()#.zero_background()
        periods = self.get_es_seasons(data, depth)
        qualities = []
        for period in periods:
            d.fit_es(period)
            T, t = d.split(retrain = True)
            D = T.append(t); D.set_name(data.get_name(), 'Train + Test'); D.update_label();
            (d.print(), D.print(), T.print(),  t.print(),  print()) if log else None
            quality = [d.quality.rms, D.quality.rms, T.quality.rms, t.quality.rms][method_index]
            qualities.append(quality)
        return get_minimum(periods, qualities)

    def get_es_seasons(self, data, depth = 1):
        periods = self.find_seasons(data, 0, 4, 0)
        periods = [p + j for p in periods for j in range(-depth, depth + 1)]
        periods = [p for p in periods if p in range(data.length)]
        return list(set(periods))
            

    def find_all(self, data, log = True):
        data = data.copy().zero_background();
        
        t = data.find_trend(log = False)
        data.log() if log else None
        
        s = data.zero_background().find_seasons(threshold = 2.1, log = False)
        data.log() if log else None
        
        es = data.zero_background().find_es(log = False)
        data.log() if log else None
        
        s2 = data.zero_background().fit_trend(t).find_seasons(threshold = 2.1, log = False)
        data.log() if log else None

        data.zero_background().fit_trend(t).find_es(log = False)
        data.log() if log else None

        data.zero_background().fit_seasons(*s).find_es(log = False)
        data.log() if log else None
        
        data.zero_background().fit_trend(t).fit_seasons(*s2).find_es(log = False)
        data.log() if log else None


    def get_trend(self):
        return self.trend.data

    def get_season(self):
        return self.season.data

    def get_prediction(self):
        return self.prediction.data#.T[1] if self.prediction.data is not None else None

    def get_treason(self):
        res = [data for data in [self.get_trend(), self.get_season()] if data is not None]
        return np.sum(res, axis = 0) if len(res) != 0 else None

    def get_trend_residuals(self, data):
        trend = self.get_trend()
        return data.sub(trend) if trend is not None else data
    
    def get_season_residuals(self, data):
        treason = self.get_treason()
        return data.sub(treason) if treason is not None else data

    def get_total(self):
        res = [data for data in [self.get_treason(), self.get_prediction()] if data is not None]
        return np.sum(res, axis = 0) if len(res) != 0 else None


        
        
        
        
     


