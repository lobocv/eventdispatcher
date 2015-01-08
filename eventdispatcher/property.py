__author__ = 'calvin'

import weakref
import copy


class Property(object):
    "Emulate PyProperty_Type() in Objects/descrobject.c"
    all_properties = weakref.WeakKeyDictionary()

    def __init__(self, default_value):
        self.default_value = default_value
        self.value = copy.deepcopy(default_value)

    def fget(self, obj):
        return self.instances[obj]['value']

    def fset(self, obj, value):
        self.instances[obj]['value'] = value

    def __get__(self, obj, objtype=None):
        return self.instances[obj]['value']

    def __set__(self, obj, value):
        prev_value = self.instances[obj]['value']
        if value != prev_value:
            self.instances[obj]['value'] = value
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
        # Property.get_property(instance, name)
        # all_properties keeps track of the properties of an EventDispatcher by it's property names.
        if instance in self.all_properties:
            self.all_properties[instance].update({property_name: self})
        else:
            self.all_properties[instance] = {property_name: self}

        info = {'value': self.value, 'name': property_name, 'callbacks': []}
        info.update(kwargs)
        try:
            self.instances[instance] = info
        except AttributeError:
            # Create the instances dictionary at registration so that each class has it's own instance of it.
            self.instances = weakref.WeakKeyDictionary()
            self.instances[instance] = info

    @staticmethod
    def get_property(instance, property_name):
        prop = Property.all_properties[instance][property_name]
        return prop


