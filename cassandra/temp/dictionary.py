from random import choice

get_range = lambda order: list(range(0, order + 1))
B = [True, False]


class dictionaries_class():
    def __init__(self):
        self.naive = naive_dictionaries()
        self.es = es_dictionaries()


class naive_dictionaries():
    def default(self, level = "mean"):
        return {"level": level}
    
    def all(self):
        return [self.default(level) for level in ["first", "mean", "last"]]

    def random(self):
        return choice(self.all())


class es_dictionaries():
    def default(self, seasonal_periods = 12, seasonal = "add"):
        return {"seasonal_periods": seasonal_periods, "seasonal": seasonal}
    
    def all(self, all_seasonal_periods):
        return [self.default(p) for p in all_seasonal_periods]

    def random(self, all_seasonal_periods):
        return choice(self.all(all_seasonal_periods))


dictionary = dictionaries_class()
