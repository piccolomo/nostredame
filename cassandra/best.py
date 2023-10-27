from cassandra.season import find_seasons
from cassandra.dictionary import dictionary
from cassandra.string import bold, indicator, pad
from cassandra.study import study_class


class find_best_class():
    
    def find_seasons(self, detrend = None, source = "acf", threshold = 2.5, apply_result = True, log = True, plot = False):
        detrend = self.correct_detrend_order(detrend)
        seasons = find_seasons(self._values.data, detrend_order = detrend, source = source, log = log, plot = plot, threshold = threshold)
        self.update_season(*seasons, detrend = detrend) if apply_result else None
        print("seasons applied to data\n") if apply_result and log and len(seasons) > 0 else None
        print() if log and not apply_result else None
        return seasons

    def all_seasons(self, detrend = None, threshold = 1, log = False):
        acf = self.find_seasons(detrend = detrend, source = "acf", log = log, threshold = threshold, apply_result = False)
        fft = self.find_seasons(detrend = detrend, source = "fft", log = log, threshold = threshold, apply_result = False)
        return list(set(acf + fft))
    
    def _find_best(self, function_name, arguments, test_length = None, method = "Data", log = True):
        print("optimizing function", bold(function_name)) if log else None
        data = self.copy()
        data.zero_prediction()
        data.backup("before-function")
        results = []
        l = len(arguments)
        for i in range(l):
            argument = arguments[i]
            data.restore("before-function")
            eval("data." + function_name + "(**argument)")
            study = study_class(data, test_length, method)
            study.update()
            results.append([argument, study])
            indicator(i + 1, l) if log else None

        results.sort(key = lambda el: el[1].quality)
        result = results[0] if len(results) > 0 else None
        
        if log and result is not None:
            result_study = result[1]
            arg_length = max([len(str(arg)) for arg in arguments])
            spaces = ' ' * (arg_length + 1)
            method_label = "method: " + result_study.method
            length_label = result_study.get_length()
            title = result_study._label_short_title
            print(length_label)
            print(method_label)
            print(spaces + title)
            [print(pad(argument, arg_length), study._label_short) for (argument, study) in results]
        results = [(arg, study.quality) for (arg, study) in results]
        return results

    def _apply_result(self, function_name, results, has_weight = True, log = True):
        (result, weight) = results[0] if len(results) > 0 else (None, None)
        apply_result = result is not None
        command = 'self.' + function_name + '(**result' + (', weight = weight)' if has_weight else ')')
        eval(command) if apply_result else None
        print("best result applied to data\n") if apply_result and log else None
    
    def find_trend(self, order = 15, test_length = None, method = "test", apply_result = True, log = True):
        arguments = [{'order': i} for i in range(0, order + 1)]
        results = self._find_best(function_name = "update_trend", arguments = arguments, test_length = test_length, method = method, log = log)
        self._apply_result("update_trend", results, False, log) if apply_result else None
        return results

    def find_naive(self, test_length = None, method = "Data", apply_result = True, log = True):
        arguments = dictionary.naive.all()
        results = self._find_best(function_name = "add_naive", arguments = arguments, test_length = test_length, method = method, log = log)
        self._apply_result("add_naive", results, True, log) if apply_result else None
        return results
    
    def find_es(self, seasons = None, test_length = None, method = "Data", apply_result = True, log = True):
        seasons = self.all_seasons(threshold = 1.5) if seasons is None else seasons
        arguments = dictionary.es.all(seasons)
        results = self._find_best(function_name = "add_es", arguments = arguments, test_length = test_length, method = method, log = log)
        self._apply_result("add_es", results, True, log) if apply_result else None
        return results
    
    def find_prophet(self, order = 10, test_length = None, method = "Data", apply_result = True, log = True):
        arguments = dictionary.prophet.all(order)
        results = self._find_best(function_name = "add_prophet", arguments = arguments, test_length = test_length, method = method, log = log)
        self._apply_result("add_prophet", results, True, log) if apply_result else None
        return results
    
    def find_arima(self, seasons = None, order = 1, test_length = None, method = "Data", apply_result = True, log = True):
        seasons = self.all_seasons(threshold = 2.8) if seasons is None else seasons
        arguments = dictionary.arima.all(seasons, order)
        results =  self._find_best(function_name = "add_arima", arguments = arguments, test_length = test_length, method = method, log = log)
        self._apply_result("add_arima", results, True, log) if apply_result else None
        return results
    
    def find_uc(self, seasons = None, order = 1, test_length = None, method = "Data", apply_result = True, log = True):
        seasons = self.all_seasons(threshold = 2.8) if seasons is None else seasons
        arguments = dictionary.uc.all(seasons, order)
        results =  self._find_best(function_name = "add_uc", arguments = arguments, test_length = test_length, method = method, log = log)
        self._apply_result("add_uc", results, True, log) if apply_result else None
        return results
    
    def find_cubist(self, order = 10, test_length = None, method = "Data", apply_result = True, log = True):
        arguments = dictionary.cubist.all(order)
        results =  self._find_best(function_name = "add_cubist", arguments = arguments, test_length = test_length, method = method, log = log)    
        self._apply_result("add_cubist", results, True, log) if apply_result else None
        return results

