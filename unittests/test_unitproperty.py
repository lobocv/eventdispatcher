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
    # p = UnitProperty(random.randint(0, 1000), 'm')
    # p2 = UnitProperty(random.random(), 'm')
    p = UnitProperty(100, 'm')
    p2 = UnitProperty(1, 'ft')
class PropertyTest(unittest.TestCase):

    def __init__(self, *args):
        super(PropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher.bind(p=self.assert_callback,
                             p2=self.assert_callback)
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
        for p in ["p", "p2"]:
            prop = UnitProperty.get_property(d, p)
            prop_units = prop.units
            prop_value = getattr(d, p)
            if prop_units == units:
                c = 1.
            else:
                c = ConversionFactors['{}_to_{}'.format(prop_units, units)]
            previous[p] = prop_value
            after[p] = prop_value * c
            prop.convert_to('ft')

        self.assertEqual(self.dispatch_count, 1)
        UnitProperty.convert_all('m')
        self.assertEqual(self.dispatch_count, 3)
        UnitProperty.convert_all('ft')
        self.assertEqual(self.dispatch_count, 5)

        for p in ["p", "p2"]:
            value = getattr(d, p)
            self.assertAlmostEqual(value, after[p], 3)





unittest.main()