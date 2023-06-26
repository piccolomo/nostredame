from random import choice


class dictionaries_class():
    def __init__(self):
        self.naive = naive_dictionaries()
        self.auto_arima = auto_arima_dictionaries()
        self.arima = arima_dictionaries()
        self.es = es_dictionaries()
        self.uc = uc_dictionaries()
        self.prophet = prophet_dictionaries()
        self.cubist = cubist_dictionaries()


class naive_dictionaries():
    def default(self, level = "mean"):
        return {"level": level}
    
    def all(self):
        return [self.default(level) for level in ["first", "mean", "last"]]

    def random(self):
        return choice(self.all())


class auto_arima_dictionaries():
    def default(self, period = 1, order = 2):
        return {"m": period, "max_order": order}

get_range = lambda order: list(range(0, order + 1))
B = [True, False]
  
class arima_dictionaries():
    def default(self, p = 1, d = 1, q = 1, P = 1, D = 1, Q = 1, m = 12):
        return {"order": (p, d, q), "seasonal_order": (P, D, Q, m)} 
    
    def all(self, periods, order = 2):
        data = get_range(order)
        return [self.default(p, d, q, P, D, Q, m) for p in data for d in data for q in data for P in data for D in data for Q in data for m in periods]

    def random(self, periods, order = 2):
        return choice(self.all(periods, order))


class es_dictionaries():
    def default(self, period = 12):
        return {"seasonal_periods": period, "seasonal": "add"}
    
    def all(self, periods):
        return [self.default(p) for p in periods]

    def random(self, periods):
        return choice(self.all(periods))


class uc_dictionaries():
    def __init__(self):
        self.levels = ['random walk', 'local linear trend', 'smooth trend', 'local level', 'deterministic constant', 'deterministic trend', "fixed intercept", "fixed slope", "local linear deterministic trend", "ntrend", 'random trend', 'random walk with drift']

    def default(self, level = 0, cycle = True, seasonal = 12, autoregressive = 1, stochastic = True):
        return {'level': self.levels[level], 'cycle': cycle, 'seasonal': seasonal, 'autoregressive': autoregressive, 'stochastic_cycle': stochastic}
        
    def all(self, periods, order = 2):
        levels = range(len(self.levels))
        A = get_range(order)
        return [self.default(l, c, s, a, sc) for l in levels for c in B for s in periods for a in A for sc in B]

    def random(self, periods, order = 2):
        return choice(self.all(periods, order))


class prophet_dictionaries():
    def default(self, seasonality = True, points = 12):
        return {"yearly_seasonality": y, "n_changepoints": points}
    
    def all(self, order = 10):
        N = get_range(order)
        return [self.default(y, n) for y in B for n in N]

    def random(self, order = 10):
        return choice(self.all(order))

    
class cubist_dictionaries():
    def default(self, committees = 0, neighbors = 1, composite = True, unbiased = True):
        return {"n_committees": nc, "neighbors": n, "composite": c, "unbiased": u} 
        
    def all(self, order = 10):
        NC = get_range(order)
        N = range(1, 9)
        return [self.default(nc, n, c, u) for nc in NC for n in N for c in B for u in C]

    def random(self, order = 10):
        return choice(self.all(order))


dictionary = dictionaries_class()
