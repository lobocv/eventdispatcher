__author__ = 'calvin'
import collections
from future.utils import iteritems, iterkeys, itervalues
from functools import partial
from . import Property


class __DoesNotExist__:
    # Custom class used as a flag
    pass


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
        prev = self.dictionary.get(key, __DoesNotExist__)
        self.dictionary[key] = value
        try:
            # Ensure that the comparison evaluates as a scalar boolean (unlike numpy arrrays)
            dispatch = bool(prev != value)
        except Exception:
            dispatch = True
        if dispatch:
            self.dispatch(self.dictionary)

    def clear(self):
        if len(self.dictionary):
            self.dictionary.clear()
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

    def __getstate__(self):
        return self.dictionary

    def __reduce__(self):
        return dict, tuple(), None, None, iter(iteritems(self.dictionary))

    def copy(self):
        return self.dictionary.copy()

    def get(self, key, default=None):
        return self.dictionary.get(key, default)

    def itervalues(self):
        return itervalues(self.dictionary)

    def iterkeys(self):
        return iterkeys(self.dictionary)

    def iteritems(self):
        return iteritems(self.dictionary)

    def update(self, _dict=None, **kwargs):
        if _dict:
            try:
                not_equal = bool(self.dictionary != _dict)
            except Exception:
                not_equal = True
            if not_equal:
                self.dictionary.update(_dict)
                self.dispatch(self.dictionary)
        elif kwargs:
            try:
                not_equal = bool(self.dictionary != kwargs)
            except Exception:
                not_equal = True
            if not_equal:
                self.dictionary.update(kwargs)
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
        try:
            # Ensure that the comparison evaluates as a scalar boolean (unlike numpy arrrays)
            do_dispatch = bool(p['value'] != value)
        except Exception:
            do_dispatch = True
        if do_dispatch:
            p['value'].dictionary.clear()
            p['value'].dictionary.update(value)          # Assign to the ObservableDict's value
            for callback in p['callbacks']:
                if callback(obj, value):
                    break