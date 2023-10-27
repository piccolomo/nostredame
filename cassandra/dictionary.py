from random import choice

get_range = lambda order: list(range(0, order + 1))
B = [True, False]


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


class es_dictionaries():
    def default(self, seasonal_periods = 12, seasonal = "add"):
        return {"seasonal_periods": seasonal_periods, "seasonal": seasonal}
    
    def all(self, all_seasonal_periods):
        return [self.default(p) for p in all_seasonal_periods]

    def random(self, all_seasonal_periods):
        return choice(self.all(all_seasonal_periods))


class prophet_dictionaries():
    def default(self, yearly_seasonality = True, n_changepoints = 12):
        return {"yearly_seasonality": yearly_seasonality, "n_changepoints": n_changepoints}
    
    def all(self, max_n_changepoints):
        N = get_range(max_n_changepoints)
        return [self.default(y, n) for y in B for n in N]

    def random(self, max_n_changepoints):
        return choice(self.all(max_n_changepoints))

    
class auto_arima_dictionaries():
    def default(self, m = 1, max_order = 2):
        return {"m": m, "max_order": max_order}


class arima_dictionaries():
    def default(self, order = (1, 0, 1), seasonal_order = (0, 1, 0, 0)):
        return {"order": order, "seasonal_order": seasonal_order} 
    
    def all(self, seasons, order):
        data = get_range(order)
        return [self.default((p, d, q), (P, D, Q, m)) for p in data for d in data for q in data for P in data for D in data for Q in data for m in seasons]

    def random(self, periods, order):
        return choice(self.all(periods, order))


class uc_dictionaries():
    def __init__(self):
        self.levels = ['random walk', 'local linear trend', 'smooth trend', 'local level', 'deterministic constant', 'deterministic trend', "fixed intercept", "fixed slope", "local linear deterministic trend", "ntrend", 'random trend', 'random walk with drift']

    def default(self, level = 'random walk', cycle = True, seasonal = 12, autoregressive = 1, stochastic_cycle = True):
        return {'level': level, 'cycle': cycle, 'seasonal': seasonal, 'autoregressive': autoregressive, 'stochastic_cycle': stochastic_cycle}
        
    def all(self, periods, order):
        levels = range(len(self.levels))
        A = get_range(order)
        return [self.default(l, c, s, a, sc) for l in levels for c in B for s in periods for a in A for sc in B]

    def random(self, periods, order):
        return choice(self.all(periods, order))

    
class cubist_dictionaries():
    def default(self, n_committees = 0, neighbors = 1, composite = True, unbiased = True):
        return {"n_committees": n_committees, "neighbors": neighbors, "composite": composite, "unbiased": unbiased} 
        
    def all(self, order):
        NC = get_range(order)
        N = range(1, 9)
        return [self.default(nc, n, c, u) for nc in NC for n in N for c in B for u in B]

    def random(self, order):
        return choice(self.all(order))


dictionary = dictionaries_class()
uc_levels = dictionary.uc.levels
uc_levels = {i:uc_levels[i] for i in range(len(uc_levels))}
