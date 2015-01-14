__author__ = 'calvin'

import unittest

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher.unitproperty import UnitProperty, ConversionFactors


class Dispatcher(EventDispatcher):
    p1 = UnitProperty(1, 'm')
    p2 = UnitProperty(10, 'm')
    p3 = UnitProperty(100, 'm')


class UnitPropertyTest(EventDispatcherTest):
    property_names = {'p', 'p2', 'p3'}

    def __init__(self, *args):
        super(UnitPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback,
                             p2=self.assert_callback,
                             p3=self.assert_callback)

    def test_change_units(self):
        d = self.dispatcher
        units = 'ft'
        previous = {}
        after = {}
        for p in d.event_dispatcher_properties.iterkeys():
            prop = d.get_dispatcher_property(p)
            prop_units = prop.units
            prop_value = getattr(d, p)
            if prop_units == units:
                c = 1.
            else:
                c = ConversionFactors['{}_to_{}'.format(prop_units, units)]
            previous[p] = prop_value
            after[p] = prop_value * c
            # Change property's units individually
            prop.convert_to('ft')

        for p in d.event_dispatcher_properties.iterkeys():
            value = getattr(d, p)
            self.assertAlmostEqual(value, after[p], 3)

        # Change all properties units
        self.assertEqual(self.dispatch_count, 3)
        self._check_conversion('m')
        self._check_conversion('inches')
        self._check_conversion('mm')
        self._check_conversion('inches')
        self._check_conversion('yards')
        self._check_conversion('km')
        self._check_conversion('cm')
        self._check_conversion('m')

    def _check_conversion(self, units):
        d = self.dispatcher
        before = {}
        after = {}
        for prop_name in d.event_dispatcher_properties.iterkeys():
            p = self.dispatcher.get_dispatcher_property(prop_name)
            before[prop_name] = getattr(self.dispatcher, prop_name)
            c = ConversionFactors["{}_to_{}".format(p.units, units)]
            after[prop_name] = before[prop_name] * c
        UnitProperty.convert_all(units)
        for prop_name in d.event_dispatcher_properties.iterkeys():
            result = getattr(self.dispatcher, prop_name)
            self.assertAlmostEqual(result, after[prop_name], 3)


if __name__ == '__main__':
    unittest.main()
