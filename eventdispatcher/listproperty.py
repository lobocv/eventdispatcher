__author__ = 'calvin'

import collections
import json
from functools import partial

from . import Property


class ObservableList(collections.MutableSequence):
    def __init__(self, l, dispatch_method):
        if not type(l) == list and not type(l) == tuple and not isinstance(l, ObservableList):
            raise ValueError('Observable list must only be initialized with lists as arguments')
        self.list = list(l)
        self.dispatch = dispatch_method

    def __repr__(self):
        return self.list.__repr__()

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

    def register(self, instance, property_name, value):
        self.value = ObservableList(value, dispatch_method=partial(instance.dispatch, property_name, instance))
        super(ListProperty, self).register(instance, property_name, self.value)

    def __set__(self, obj, value):
        p = self.instances[obj]
        # Check if we need to dispatch
        do_dispatch = len(p['value'].list) != len(value) or not ListProperty.compare_sequences(p['value'], value)
        self.instances[obj]['value'].list[:] = value        # Assign to ObservableList's value
        if do_dispatch:
            for callback in p['callbacks']:
                if callback(obj, value):
                    break

    @staticmethod
    def compare_sequences(iter1, iter2):
        """
        Compares two iterators to determine if they are equal. Used to compare lists and tuples
        """
        iter1, iter2 = iter(iter1), iter(iter2)
        for i1 in iter1:
            try:
                i2 = next(iter2)
            except StopIteration:
                return False

            if i1 != i2:
                return False

        try:
            i2 = next(iter2)
        except StopIteration:
            return True

        return False