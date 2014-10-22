__author__ = 'calvin'
from functools import partial

class BaseProperty(object):
    "Emulate PyProperty_Type() in Objects/descrobject.c"
    all_properties = {}
    def __init__(self, default_value, fdel=None, doc=None):
        self.fdel = fdel
        self.default_value = default_value
        self.prev_value = None
        if doc is None:
            doc = self.fget.__doc__
        self.__doc__ = doc


    def fget(self, obj):
        return self.instances[obj]['value']

    def fset(self, obj, value):
        self.instances[obj]['value'] = value

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

    def register(self, instance, property_name, default_value, **kwargs):
        # Keep a reference to the property as a class attribute so that we can get the property by calling
        # BaseProperty.get_property(instance, name)
        # all_properties keeps track of the properties of an EventDispatcher by it's property names.
        if instance in self.all_properties:
            self.all_properties[instance].update({property_name: self})
        else:
            self.all_properties[instance] = {property_name: self}

        info = {'value': default_value, 'name': property_name, 'callbacks': []}
        info.update(kwargs)
        try:
            self.instances[instance] = info
        except AttributeError:
            self.instances = {}
            self.instances[instance] = info
        sdf=43
    @staticmethod
    def get_property(instance, property_name):
        prop = BaseProperty.all_properties[instance][property_name]
        return prop

class Property(BaseProperty):

    def __init__(self, default_value):
        super(Property, self).__init__(default_value, None, doc=None)
        self.default_value = default_value



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
        super(DictProperty, self).__init__(default_value, **kwargs)

        if isinstance(default_value, dict):
            self.default_value = ObservableDict(default_value, self)
        else:
            raise ValueError('DictProperty takes dict only.')

    def register(self, instance, property_name, default_value, **kwargs):
        super(DictProperty, self).register(instance, property_name, default_value, **kwargs)
        self.default_value.eventdispatcher = instance

    def fset(self, obj, value):
        self.default_value = ObservableDict(value, self)
        cb = self.instances[obj]['callbacks'][:]
        self.register(obj, self.name, value)
        self.instances[obj]['callbacks'] = cb




