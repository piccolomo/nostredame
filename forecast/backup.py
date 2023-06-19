from copy import copy, deepcopy

initial = "origin"

class copy_class():
    def __init__(self):
        pass

    def copy(self):
        new = deepcopy(self)
        new.__dict__ = deepcopy(self.__dict__)
        return new

    def _copy_from(self, new):
        self.__dict__ = deepcopy(new.__dict__)
        return self

class backup_class():
    def __init__(self):
        self._set_empty_backup()
        self.backup()

    def _set_empty_backup(self):
        self._backup = {}
    
    def backup(self, name = initial, log = False):
        if name in self._backup and log:
            print("backup \'" + name + "\' overwritten")
        #elif name not in self._backup:
        self._backup[name] = self._get_dict()

    def restore(self, name = initial, log = False):
        print("backup \'" + name + "\' not present") if name not in self._backup and log else None
        if name in self._backup:
            self._set_dict(self._backup[name])
        self._clear_backup() if name == initial else None
        return self
            
    def _clear_backup(self):
        new = {}
        if initial in self._backup:
            new[initial] = self._backup[initial]
        self._backup = new

    def _get_dict(self):
        d = self.__dict__
        #d = {deepcopy(el): deepcopy(d[el])for el in d}
        d = deepcopy(d)
        d.pop("_backup")
        return d

    def _set_dict(self, d):
        new = {"_backup": self.__dict__["_backup"]}
        for el in d:
            if el != "_backup":
                new[el] = deepcopy(d[el])
        self.__dict__ = new

    def _get_initial_backup(self):
        return self._backup[initial]

