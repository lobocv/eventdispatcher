__author__ = 'calvin'
from functools import partial

from . import Property


class ObservableDict(object):
    def __init__(self, dictionary, dispatch_method):
        self.dictionary = dictionary.copy()
        self.dispatch = dispatch_method

    def __get__(self, instance, owner):
        return self.dictionary

    def __contains__(self, item):
        return item in self.dictionary

    def __getitem__(self, item):
        return self.dictionary[item]

    def __setitem__(self, key, value):
        try:
            prev = self.dictionary[key]
            check = prev != value
        except KeyError:
            check = True
        self.dictionary[key] = value
        if check:
            self.dispatch(self.dictionary)

    def __eq__(self, other):
        return self.dictionary == other

    def __cmp__(self, other):
        return self.dictionary == other

    def __ne__(self, other):
        return self.dictionary != other

    def __nonzero__(self):
        return bool(self.dictionary)

    def __delitem__(self, key):
        del self.dictionary[key]
        self.dispatch(self.dictionary)

    def copy(self):
        return self.__class__(self.dictionary, self.dispatch)

    def update(self, E=None, **F):
        if E and self.dictionary != E:
            self.dictionary.update(E)
            self.dispatch(self.dictionary)
        elif F and self.dictionary != F:
            self.dictionary.update(F)
            self.dispatch(self.dictionary)

    def keys(self):
        return self.dictionary.keys()

    def values(self):
        return self.dictionary.values()

    def items(self):
        return self.dictionary.items()

    def iteritems(self):
        return self.dictionary.iteritems()

    def pop(self, key):
        item = self.dictionary.pop(key)
        self.dispatch(self.dictionary)
        return item


class DictProperty(Property):

    def __init__(self, default_value, **kwargs):
        super(DictProperty, self).__init__(default_value, **kwargs)
        if not isinstance(default_value, dict):
            raise ValueError('DictProperty takes dict only.')

    def register(self, instance, property_name, value, **kwargs):
        self.value = ObservableDict(value, dispatch_method=partial(instance.dispatch, property_name, instance))
        super(DictProperty, self).register(instance, property_name, self.value, **kwargs)

    def __set__(self, obj, value):
        p = self.instances[obj]
        do_dispatch = p['value'] != value
        p['value'].dictionary.clear()
        p['value'].dictionary.update(value)          # Assign to the ObservableDict's value
        if do_dispatch:
            for callback in p['callbacks']:
                if callback(obj, value):
                    break