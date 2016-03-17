__author__ = 'calvin'
import collections
from functools import partial
from . import Property


class ObservableSet(collections.MutableSet):

    def __init__(self, dictionary, dispatch_method):
        self.set = dictionary.copy()
        self.dispatch = dispatch_method

    def __repr__(self):
        return self.set.__repr__()

    def __get__(self, instance, owner):
        return self.set

    def __contains__(self, item):
        return item in self.set

    def __len__(self):
        return len(self.set)

    def __getitem__(self, item):
        return self.set[item]

    def __setitem__(self, key, value):
        try:
            prev = self.set[key]
            check = prev != value
        except KeyError:
            check = True
        self.set[key] = value
        if check:
            self.dispatch(self.set)

    def __eq__(self, other):
        # Must be this order and not self.set == other, otherwise unittest.assertEquals fails
        return other == self.set

    def __cmp__(self, other):
        return self.set == other

    def __ne__(self, other):
        return self.set != other

    def __delitem__(self, key):
        del self.set[key]
        self.dispatch(self.set)

    def __iter__(self):
        return iter(self.set)

    def __nonzero__(self):
        return bool(self.set)

    def add(self, value):
        self.set.add(value)

    def discard(self, value):
        self.set.discard(value)

    def copy(self):
        return self.__class__(self.set, self.dispatch)

    def get(self, key, default=None):
        self.set.get(key, default)

    def remove(self, item):
        self.set.remove(item)
        self.dispatch(self.set)

    def update(self, *items):
        if self.set != items:
            self.set.update(*items)
            self.dispatch(self.set)

    def pop(self):
        item = self.set.pop()
        self.dispatch(self.set)
        return item

    def difference(self, items):
        return self.set.difference(items)


class SetProperty(Property):

    def __init__(self, default_value, **kwargs):
        super(SetProperty, self).__init__(default_value, **kwargs)
        if not isinstance(default_value, set):
            raise ValueError('SetProperty takes sets only.')

    def register(self, instance, property_name, value):
        self.value = ObservableSet(value, dispatch_method=partial(instance.dispatch, property_name, instance))
        super(SetProperty, self).register(instance, property_name, self.value)

    def __set__(self, obj, value):
        p = self.instances[obj]
        do_dispatch = p['value'] != value
        p['value'].set.clear()
        p['value'].set.update(value)          # Assign to the ObservableDict's value
        if do_dispatch:
            for callback in p['callbacks']:
                if callback(obj, value):
                    break