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
    def default(self, m = 1, max_order = 2):
        return {"m": m, "max_order": max_order}
    
    def all(self, periods, order = 5):
        return [self.default(m, max_order) for m in periods for max_order in range(order + 1)]

    def random(self):
        return choice(self.all())

  
class arima_dictionaries():
    def default(self, p = 1, d = 1, q = 1, P = 1, D = 1, Q = 1, s = 12):
        return {"order": (p, d, q), "seasonal_order": (P, D, Q, s)} 
    
    def all(self, periods, order = 2):
        data = list(range(0, order + 1))
        return [self.default(p, d, q, P, D, Q, s) for p in data for d in data for q in data for P in data for D in data for Q in data for s in periods]

    def random(self, periods, order = 2):
        return choice(self.all(periods, order))


class es_dictionaries():
    def default(self, p = 12):
        return {"seasonal_periods": p, "seasonal": "add"}
    
    def all(self, periods):
        return [self.default(p) for p in periods]

    def random(self, periods):
        return choice(self.all(periods))


class uc_dictionaries():
    def __init__(self):
        self.levels = ['random walk', 'local linear trend', 'smooth trend', 'local level', 'deterministic constant', 'deterministic trend', "fixed intercept", "fixed slope", "local linear deterministic trend", "ntrend", 'random trend', 'random walk with drift']

    def default(self, l = 'random walk', c = True, s = 12, a = 1, sc = True):
        return {'level': l, 'cycle': c, 'seasonal': s, 'autoregressive': a, 'stochastic_cycle': sc}
        
    def all(self, periods, order = 2):
        A = list(range(0, order + 1))
        C = [True, False]
        return [self.default(l, c, s, a, sc) for l in self.levels for c in C for s in periods for a in A for sc in C]

    def random(self, periods, order = 2):
        return choice(self.all(periods, order))


class prophet_dictionaries():
    def default(self, y = True, n = 12):
        return {"yearly_seasonality": y, "n_changepoints": n}
    
    def all(self, order = 10):
        Y = [True, False]
        N = list(range(0, order + 1))
        return [self.default(y, n) for y in Y for n in N]

    def random(self, order = 10):
        return choice(self.all(order))

    
class cubist_dictionaries():
    def default(self, nc = 0, n = 1, c = True, u = True):
        return {"n_committees": nc, "neighbors": n, "composite": c, "unbiased": u} 
        
    def all(self, order = 10):
        NC = list(range(0, order + 1))
        N = range(1, 9)
        C = [True, False]
        return [self.default(nc, n, c, u) for nc in NC for n in N for c in C for u in C]

    def random(self, order = 10):
        return choice(self.all(order))


dictionary = dictionaries_class()
