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
from eventdispatcher.properties import Property, DictProperty
import random

class Dispatcher(EventDispatcher):
    p = Property(10)
    p2 = Property(20)
    d = DictProperty({1: 'one', 2: 'two'})
    d2 = DictProperty({'one': 1, 'two': 2})

class PropertyTest(unittest.TestCase):


    def setUp(self):
        self.dispatcher = Dispatcher()
        self.dispatcher.bind(p=self.assert_callback,
                             d=self.assert_callback,
                             d2=self.assert_callback)
        self.dispatch_count = 0

    def tearDown(self):
        self.dispatch_count = 0

    def assert_callback(self, inst, value):
        self.dispatch_count += 1
        print 'dispatching value {}'.format(value)

    def test_get_property(self):
        p = Property.get_property(self.dispatcher, 'p')
        dispatcher = self.dispatcher
        dispatcher.p = 123456789
        self.assertTrue(type(p) == Property)
        self.assertEqual(dispatcher.p, 123456789)
        test_dict = {'a': random.randint(0, 1000), 'b': random.randint(0, 1000), 'c': random.randint(0, 1000)}
        dispatcher.d = test_dict
        d = Property.get_property(self.dispatcher, 'd')
        for key in test_dict.keys():
            self.assertEqual(test_dict[key], dispatcher.d[key])

        self.assertTrue(type(d) == DictProperty)

    def test_property_dispatch(self):
        """
        Tests that the callback is called ONLY when the value changes.
        """
        expected_dispatches = 5
        self.dispatcher.p = 1
        self.dispatcher.p = 'two'
        self.dispatcher.p = 2
        self.dispatcher.p = 3
        self.dispatcher.p = None
        self.assertEqual(self.dispatch_count, expected_dispatches)

    def test_dictproperty_dispatch(self):
        """
        Tests that the callback is called ONLY when the value changes.
        """
        expected_dispatches = 8

        self.dispatcher.d[1] = 1
        self.dispatcher.d.update({1: 1, 2: 2})
        self.dispatcher.d[3] = 3
        self.dispatcher.d[3] = 3
        self.dispatcher.d = {4: 'Test'}

        self.dispatcher.d2['one'] = 'one'
        self.assertEqual(self.dispatcher.d[4], 'Test')
        self.dispatcher.d2.update({'one': 'one', 'two': 'two'})
        self.assertEqual(self.dispatcher.d[4], 'Test')
        self.dispatcher.d2['three'] = 'three'
        self.assertEqual(self.dispatcher.d[4], 'Test')
        self.dispatcher.d2['three'] = 'three'
        self.assertEqual(self.dispatcher.d[4], 'Test')
        self.dispatcher.d2 = {4: 'Test'}

        self.assertEqual(self.dispatch_count, expected_dispatches)



unittest.main()