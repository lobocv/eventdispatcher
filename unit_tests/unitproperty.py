__author__ = 'calvin'

import unittest

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher.unitproperty import UnitProperty, ConversionFactors


class Dispatcher(EventDispatcher):
    p1 = UnitProperty(1, 'm')
    p2 = UnitProperty(1, 'm')
    p3 = UnitProperty(10, 'm')


class UnitPropertyTest(EventDispatcherTest):
    property_names = {'p', 'p2', 'p3'}

    def __init__(self, *args):
        super(UnitPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback,
                             p2=self.assert_callback,
                             p3=self.assert_callback)

    def test_property_independence(self):
        d = self.dispatcher
        d2 = self.dispatcher2

        for name in d.event_dispatcher_properties.keys():
            self._check_conversion(d, name, 'm')
            self._check_conversion(d2, name, 'm')
            self.assert_callback_count = 0
            # Check that when we convert the same property in d2, d1's value does not change
            d2_value = getattr(d2, name)
            self._check_conversion(d, name, 'ft')
            d_value = getattr(d, name)
            self.assertNotEqual(d2_value, d_value)
            self.assertEquals(self.assert_callback_count, 1)

    def test_change_units(self):
        d = self.dispatcher
        for name in d.event_dispatcher_properties.keys():
            # Change all properties units
            self._check_conversion(d, name, 'm')
            self._check_conversion(d, name, 'inches')
            self._check_conversion(d, name, 'mm')
            self._check_conversion(d, name, 'inches')
            self._check_conversion(d, name, 'yards')
            self._check_conversion(d, name, 'km')
            self._check_conversion(d, name, 'cm')
            self._check_conversion(d, name, 'm')
        self.assertEquals(self.assert_callback_count, 7 * len(d.event_dispatcher_properties))

    def _check_conversion(self, dispatcher, prop_name, units):
        """
        Manually conver the from current units to `units` and ensure that UnitProperty.convert_to function results in
        the same value
        """
        before = getattr(dispatcher, prop_name)
        current_units = UnitProperty.get_units(dispatcher, prop_name)
        c = ConversionFactors["{}_to_{}".format(current_units, units)]
        after = before * c
        UnitProperty.convert_to(dispatcher, prop_name, units)
        result = getattr(self.dispatcher, prop_name)
        self.assertAlmostEqual(result, after, 3)


if __name__ == '__main__':
    unittest.main()
