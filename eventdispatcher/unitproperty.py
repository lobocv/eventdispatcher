__author__ = 'calvin'
from weakref import WeakSet

from . import Property


"""
Create a dictionary of conversion methods between US Standard and Metric distance unit systems.
"""
from_meter_conversions = {'km': 1 / 1000., 'm': 1, 'cm': 100., 'mm': 1000.,
                          'ft': 3.28084, 'yards': 1.09361, 'miles': 0.000621371, 'inches': 39.3701, 'in': 39.3701}
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


class UnitProperty(Property):
    unit_properties = WeakSet()

    def __init__(self, default_value, units):
        super(UnitProperty, self).__init__(default_value, units=units)

    @staticmethod
    def get_units(dispatcher, property_name):
        return dispatcher.event_dispatcher_properties[property_name]['units']

    @staticmethod
    def convert_to(dispatcher, property_name, units):
        info = dispatcher.event_dispatcher_properties[property_name]
        if info['units'] == units:
            return
        c = ConversionFactors["{}_to_{}".format(info['units'], units)]
        setattr(dispatcher, property_name, c * info['value'])
        info['units'] = units

    def register(self, instance, property_name, default_value):
        super(UnitProperty, self).register(instance, property_name, default_value)
        # Keep track of all the UnitProperties so that we can change them all when the unit system changes
        self.unit_properties.add(self)
