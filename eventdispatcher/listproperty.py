__author__ = 'calvin'

import collections

from . import Property
from functools import partial

class ObservableList(collections.MutableSequence):

    def __init__(self, l, dispatch_method):
        if not type(l) == list and not type(l) == tuple and not isinstance(l, ObservableList):
            raise ValueError('Observable list must only be initialized with lists as arguments')
        self._list = list(l[:])
        self.dispatch = dispatch_method

    def __get__(self, instance, owner):
        return self._list

    def __getitem__(self, item):
        return self._list[item]

    def __setitem__(self, key, value):
        if self._list[key] != value:
            self._list[key] = value
            self.dispatch(self._list)

    def __reversed__(self):
        return reversed(self._list)

    def __delitem__(self, key):
        del self._list[key]
        self.dispatch(self._list)

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return iter(self._list)

    def insert(self, index, value):
        self._list.insert(index, value)
        self.dispatch(self._list)

    def append(self, value):
        self._list.append(value)
        self.dispatch(self._list)

    def extend(self, values):
        self._list.extend(values)
        self.dispatch(self._list)

    def pop(self, index=-1):
        value = self._list.pop(index)
        self.dispatch(self._list)
        return value

    def __eq__(self, other):
        return self._list == other

    def __ne__(self, other):
        return self._list != other

class ListProperty(Property):

    def register(self, instance, property_name, value, **kwargs):
        self.value = ObservableList(value, dispatch_method=partial(instance.dispatch, property_name, instance))
        super(ListProperty, self).register(instance, property_name, self.value, **kwargs)

    def __set__(self, obj, value):
        cb = self.instances[obj]['callbacks'][:]
        self.register(obj, self.name, value)
        self.instances[obj]['callbacks'] = cb
        obj.dispatch(self.name, obj, self.value._list)
