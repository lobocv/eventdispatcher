__author__ = 'calvin'
''' Work-around to allow imports of a high level package.'''
import sys
import os
cwd = os.path.dirname(os.path.realpath(__file__))
module_path = os.path.split(cwd)[0]
module_parent_dir = os.path.split(module_path)[0]
if __name__ == '__main__':

    sys.path.append(module_parent_dir)


import unittest
from eventdispatcher import EventDispatcher
from eventdispatcher.properties import UnitProperty, ConversionFactors
import random


class Dispatcher(EventDispatcher):
    p = UnitProperty(1, 'm')
    p2 = UnitProperty(10, 'm')
    p3 = UnitProperty(100, 'm')

class PropertyTest(unittest.TestCase):
    property_names = {'p', 'p2', 'p3'}
    def __init__(self, *args):
        super(PropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher.bind(p=self.assert_callback,
                             p2=self.assert_callback,
                             p3=self.assert_callback)
    def setUp(self):
        self.dispatch_count = 0

    def tearDown(self):
        self.dispatch_count = 0

    def assert_callback(self, inst, value):
        self.dispatch_count += 1
        print 'dispatching value {}'.format(value)

    def test_change_units(self):
        d = self.dispatcher
        units = 'ft'
        previous = {}
        after = {}
        for p in self.property_names:
            prop = UnitProperty.get_property(d, p)
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

        for p in self.property_names:
            value = getattr(d, p)
            self.assertAlmostEqual(value, after[p], 3)

        # Change all properties units
        self.assertEqual(self.dispatch_count, 3)
        self._check_conversion('m')
        self._check_conversion('inch')
        self._check_conversion('mm')
        self._check_conversion('inch')
        self._check_conversion('km')
        self._check_conversion('cm')
        self._check_conversion('m')

    def _check_conversion(self, units):
        before = {}
        after = {}
        for prop_name in self.property_names:
            p = UnitProperty.get_property(self.dispatcher, prop_name)
            before[prop_name] = getattr(self.dispatcher, prop_name)
            c = ConversionFactors["{}_to_{}".format(p.units, units)]
            after[prop_name] = before[prop_name] * c
        UnitProperty.convert_all(units)
        for prop_name in self.property_names:
            result = getattr(self.dispatcher, prop_name)
            self.assertAlmostEqual(result, after[prop_name], 3)





unittest.main()