__author__ = 'calvin'
from functools import partial
import weakref
import copy

def finalized(*args):
    print 'object {} finalized'.format(args)

class BaseProperty(object):
    "Emulate PyProperty_Type() in Objects/descrobject.c"
    all_properties = weakref.WeakKeyDictionary()

    def __init__(self, default_value, fdel=None, doc=None):
        self.fdel = fdel
        self.default_value = default_value
        self.value = copy.deepcopy(default_value)
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
        prop = BaseProperty.all_properties[instance][property_name]
        return prop

class Property(BaseProperty):

    def __init__(self, default_value):
        super(Property, self).__init__(default_value, None, doc=None)
        self.default_value = default_value


class ObservableDict(object):

    def __init__(self, dictionary, dispatch_method, **kwargs):
        self.dictionary = dictionary.copy()
        self.dispatch = dispatch_method
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
            self.dispatch(self.dictionary)

    def update(self, E=None, **F):
        self.dictionary.update(E, **F)
        self.dispatch(self.dictionary)

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
            pass
            # self.default_value = ObservableDict(default_value, self)
        else:
            raise ValueError('DictProperty takes dict only.')

    def register(self, instance, property_name, value, **kwargs):
        self.value = ObservableDict(value,
                                    dispatch_method=partial(instance.dispatch, property_name, instance))
        super(DictProperty, self).register(instance, property_name, weakref.ref(self.value), **kwargs)


    def fset(self, instance, value):
        """
        Due to dictionaries being mutable objects, re-register the value
        :param instance: object the property belongs to
        :param value: value of the property
        """
        cb = self.instances[instance]['callbacks'][:]
        self.register(instance, self.name, value)
        self.instances[instance]['callbacks'] = cb



ConversionFactors = dict(km_to_mi=0.621371,
                         m_to_ft=3.28084, m_to_inches=39.3701, m_to_mm=1000., m_to_cm=100.,
                         mm_to_ft=0.00328084, mm_to_inches=0.0393701, mm_to_m=0.001,
                         mi_to_km=1.60934,
                         ft_to_mm=304.8, ft_to_m=0.3048, ft_to_inches=12.,
                         inches_to_ft=1/12., inches_to_mm=25.4, inches_to_m=0.0254, )


class UnitProperty(BaseProperty):
    unit_properties = weakref.WeakKeyDictionary()

    def __init__(self, default_value, units, fdel=None, doc=None):
        self.units = units
        super(UnitProperty, self).__init__(default_value)

    @staticmethod
    def convert_all(units):
        """
        Iterate through all instances of UnitProperty, performing conversions
        :param units:
        """
        for unitproperty, instance in UnitProperty.unit_properties.iteritems():
            if unitproperty.units == units:
                continue
            c = ConversionFactors["{}_to_{}".format(unitproperty.units, units)]
            setattr(instance, unitproperty.name, c * unitproperty.instances[instance]['value'])
            unitproperty.units = units

    def convert_to(self, units):
        if self.units == units:
            return
        c = ConversionFactors["{}_to_{}".format(self.units, units)]
        for instance in self.instances:
            setattr(instance, self.name, c * self.instances[instance]['value'])
            self.units = units

    def register(self, instance, property_name, default_value, **kwargs):
        kwargs['units'] = self.units
        super(UnitProperty, self).register(instance, property_name, default_value, **kwargs)
        # Keep track of all the UnitProperties so that we can change them all when the unit system changes
        self.unit_properties[self] = instance



