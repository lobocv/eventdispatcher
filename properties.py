__author__ = 'calvin'
from functools import partial
import weakref
import copy
import collections


from_meter_conversions = {'km': 1 / 1000., 'm': 1, 'cm': 100., 'mm': 1000.,
                          'ft': 3.28084, 'yards': 1.09361, 'miles': 0.000621371, 'inches': 39.3701}
ConversionFactors = {}

for v, v_per_meter in from_meter_conversions.iteritems():
    # For each entry, add the conversion to and from meters
    fmt1 = "m_to_{}".format(v)
    inv1 = "{}_to_m".format(v)
    ConversionFactors[fmt1] = v_per_meter
    ConversionFactors[inv1] = 1. / v_per_meter

    for q, q_per_meter in from_meter_conversions.items():
        # for each entry, add the conversion to and from other entries
        v_per_q = v_per_meter / q_per_meter
        fmt2 = "{}_to_{}".format(q, v)
        inv2 = "{}_to_{}".format(v, q)
        ConversionFactors[fmt2] = v_per_q
        ConversionFactors[inv2] = 1. / v_per_q


class BaseProperty(object):
    "Emulate PyProperty_Type() in Objects/descrobject.c"
    all_properties = weakref.WeakKeyDictionary()

    def __init__(self, default_value, fdel=None, doc=None):
        self.fdel = fdel
        self.default_value = default_value
        self.value = copy.deepcopy(default_value)
        if doc is None:
            doc = self.fget.__doc__
        self.__doc__ = doc

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

    def copy(self):
        return self.__class__(self.dictionary, self.dispatch)

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


    def __set__(self, obj, value):
        cb = self.instances[obj]['callbacks'][:]
        self.register(obj, self.name, value)
        self.instances[obj]['callbacks'] = cb
        obj.dispatch(self.name, obj, value)


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

class ObservableList(collections.MutableSequence):

    def __init__(self, l, dispatch_method):
        if not type(l) == list and not type(l) == tuple:
            raise ValueError('Observable list must only be initialized with lists as arguments')
        self._list = list(l)
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

class ListProperty(BaseProperty):

    def register(self, instance, property_name, value, **kwargs):
        self.value = ObservableList(value, dispatch_method=partial(instance.dispatch, property_name, instance))
        super(ListProperty, self).register(instance, property_name, self.value, **kwargs)

    def __set__(self, obj, value):
        cb = self.instances[obj]['callbacks'][:]
        self.register(obj, self.name, value)
        self.instances[obj]['callbacks'] = cb
        obj.dispatch(self.name, obj, self.value._list)
