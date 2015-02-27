__author__ = 'calvin'

import collections
from functools import partial

from . import Property


class ObservableList(collections.MutableSequence):
    def __init__(self, l, dispatch_method):
        if not type(l) == list and not type(l) == tuple and not isinstance(l, ObservableList):
            raise ValueError('Observable list must only be initialized with lists as arguments')
        self.list = list(l[:])
        self.dispatch = dispatch_method

    def __get__(self, instance, owner):
        return self.list

    def __getitem__(self, item):
        return self.list[item]

    def __setitem__(self, key, value):
        if self.list[key] != value:
            self.list[key] = value
            self.dispatch(self.list)

    def __reversed__(self):
        return reversed(self.list)

    def __delitem__(self, key):
        del self.list[key]
        self.dispatch(self.list)

    def __len__(self):
        return len(self.list)

    def __iter__(self):
        return iter(self.list)

    def __nonzero__(self):
        return bool(self.list)

    def insert(self, index, value):
        self.list.insert(index, value)
        self.dispatch(self.list)

    def append(self, value):
        self.list.append(value)
        self.dispatch(self.list)

    def extend(self, values):
        self.list.extend(values)
        self.dispatch(self.list)

    def pop(self, index=-1):
        value = self.list.pop(index)
        self.dispatch(self.list)

        return value

    def __eq__(self, other):
        return self.list == other

    def __ne__(self, other):
        return self.list != other

    def __nonzero__(self):
        return bool(self.list)


class ListProperty(Property):

    def register(self, instance, property_name, value, **kwargs):
        self.value = ObservableList(value, dispatch_method=partial(instance.dispatch, property_name, instance))
        super(ListProperty, self).register(instance, property_name, self.value, **kwargs)

    def __set__(self, obj, value):
        p = self.instances[obj]
        do_dispatch = p['value'].list != value              # Check if we need to dispatch
        self.instances[obj]['value'].list[:] = value        # Assign to ObservableList's value
        if do_dispatch:
            for callback in p['callbacks']:
                if callback(obj, value):
                    break
