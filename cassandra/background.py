from cassandra.trend import trend_class, np
from cassandra.season import season_class
from cassandra.prediction import prediction_class


class background_class():
    def __init__(self):
        self.trend = trend_class()
        self.season = season_class()
        self.prediction = prediction_class()

    def zero_trend(self):
        self.trend.zero()
        return self

    def zero_season(self):
        self.season.zero()
        return self

    def zero_prediction(self):
        self.prediction.zero()
        return self

    def zero(self):
        self.zero_trend()
        self.zero_season()
        self.zero_prediction()
        return self

    def update_label(self):
        self.trend.update_label()
        self.season.update_label()
        self.prediction.update_label()
        labels = [self.trend.label, self.season.label, self.prediction.label]
        self.label = ' + '.join([l for l in labels if l is not None])


    def fit_trend(self, data, order):
        self.trend.fit(data, order)

    def fit_season(self, data, periods):
        self.season.fit(self.get_season_residuals(data), periods)

    def set_predictor(self, name, dictionary):
        self.prediction.set_predictor(name, dictionary)
        return self

    def fit_predictor(self, data):
        self.prediction.fit(self.get_prediction_residuals(data))
    
    def retrain(self, data):
        self.trend.fit(data, self.trend.order) if self.trend.order is not None else None
        self.season.fit(data, self.season.periods) if self.season.periods is not None else None
        self.fit_predictor(data) if self.prediction.predictor is not None else None


    def get_trend(self):
        return self.trend.data

    def get_season(self):
        return self.season.data

    def get_prediction(self):
        return self.prediction.data

    def get_treason(self):
        res = [data for data in [self.get_trend(), self.get_season()] if data is not None]
        return np.sum(res, axis = 0) if len(res) != 0 else None

    def get_season_residuals(self, data):
        trend = self.get_trend()
        return data - trend if trend is not None else data
    
    def get_prediction_residuals(self, data):
        treason = self.get_treason()
        return data - treason if treason is not None else data

    def get_total(self):
        res = [data for data in [self.get_treason(), self.get_prediction()] if data is not None]
        return np.sum(res, axis = 0) if len(res) != 0 else None


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

    # def __add__(self, constant):
    #     new = self.copy()
    #     back = [el.data for el in [new.trend, new.season, new.prediction] if el.data is not None][0]
    #     back += constant
    #     return new
    
    # def __mul__(self, constant):
    #     new = self.copy()
    #     new.trend *= constant 
    #     new.season *= constant 
    #     new.prediction *= constant 
    #     return new
        
        
        
     


