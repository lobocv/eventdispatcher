__author__ = 'calvin'
from functools import partial

class BaseProperty(object):
    "Emulate PyProperty_Type() in Objects/descrobject.c"

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.default_value = None
        self.prev_value = None
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.prev_value = self.fget(obj)
        if value != self.prev_value:
            self.fset(obj, value)
            obj.dispatch(self.name, obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)



class Property(BaseProperty):

    def __init__(self, default_value):
        super(Property, self).__init__(self.fget, self.fset, None, doc=None)
        self.default_value = default_value

    def fget(self, obj):
        return obj.eventdispatcher_property_values[self.name]

    def fset(self, obj, value):
        obj.eventdispatcher_property_values[self.name] = value




class ObservableDict(object):

    def __init__(self, iterable, property, **kwargs):
        self.dictionary = iterable.copy()
        self._property = property

    def __get__(self, instance, owner):
        return self.dictionary

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
            self.eventdispatcher.dispatch(self._property.name, self.eventdispatcher,  self.dictionary)

    def update(self, E=None, **F):
        self.dictionary.update(E, **F)
        self.eventdispatcher.dispatch(self._property.name, self.eventdispatcher, self.dictionary)

    def keys(self):
        return self.dictionary.keys()

    def values(self):
        return self.dictionary.values()

    def items(self):
        return self.dictionary.items()

    def iteritems(self):
        return self.dictionary.iteritems()


class DictProperty(BaseProperty):

    def __init__(self, default_value, **kwargs):
        super(DictProperty, self).__init__(fget=self.fget, fset=self.fset, **kwargs)

        if isinstance(default_value, dict):
            self.default_value = ObservableDict(default_value, self)
        else:
            raise ValueError('DictProperty takes dict only.')

    def fget(self, obj):
        return obj.eventdispatcher_property_values[self.name]

    def fset(self, obj, value):
        self.__init__(value)
        self.default_value.eventdispatcher = obj
        obj.eventdispatcher_property_values[self.name] = self.default_value




