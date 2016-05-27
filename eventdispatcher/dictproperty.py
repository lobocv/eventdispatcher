__author__ = 'calvin'
import collections
import json

from functools import partial
from . import Property


class ObservableDict(collections.MutableMapping):

    def __init__(self, dictionary, dispatch_method):
        self.dictionary = dictionary.copy()
        self.dispatch = dispatch_method

    def __repr__(self):
        return self.dictionary.__repr__()

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

    def __len__(self):
        return len(self.dictionary)

    def __eq__(self, other):
        return self.dictionary == other

    def __cmp__(self, other):
        return self.dictionary == other

    def __ne__(self, other):
        return self.dictionary != other

    def __delitem__(self, key):
        del self.dictionary[key]
        self.dispatch(self.dictionary)

    def __iter__(self):
        return iter(self.dictionary)

    def __nonzero__(self):
        return bool(self.dictionary)

    def copy(self):
        return self.dictionary.copy()

    def get(self, key, default=None):
        return self.dictionary.get(key, default)

    def itervalues(self):
        return self.dictionary.itervalues()

    def iterkeys(self):
        return self.dictionary.iterkeys()

    def iteritems(self):
        return self.dictionary.iteritems()

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

    def pop(self, key):
        item = self.dictionary.pop(key)
        self.dispatch(self.dictionary)
        return item


class DictProperty(Property):

    def __init__(self, default_value, **kwargs):
        super(DictProperty, self).__init__(default_value, **kwargs)
        if not isinstance(default_value, dict):
            raise ValueError('DictProperty takes dict only.')

    def register(self, instance, property_name, value):
        self.value = ObservableDict(value, dispatch_method=partial(instance.dispatch, property_name, instance))
        super(DictProperty, self).register(instance, property_name, self.value)

    def __set__(self, obj, value):
        p = self.instances[obj]
        do_dispatch = p['value'] != value
        p['value'].dictionary.clear()
        p['value'].dictionary.update(value)          # Assign to the ObservableDict's value
        if do_dispatch:
            for callback in p['callbacks']:
                if callback(obj, value):
                    break