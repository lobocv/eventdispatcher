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


class Dispatcher(EventDispatcher):
    p = Property(10)
    d = DictProperty({1: 'one', 2: 'two'})

class PropertyTest(unittest.TestCase):


    def setUp(self):
        self.dispatcher = Dispatcher()
        self.dispatcher.bind(p=self.assert_callback, d=self.assert_callback)
        self.dispatch_count = 0

    def tearDown(self):
        self.dispatch_count = 0

    def assert_callback(self, inst, value):
        self.dispatch_count += 1

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
        expected_dispatches = 5

        self.dispatcher.d[1] = 1
        self.dispatcher.d[2] = 2
        self.dispatcher.d.update({1: 'one', 2: 'two'})
        self.dispatcher.d[3] = 'three'
        self.dispatcher.d[3] = 3
        self.assertEqual(self.dispatch_count, expected_dispatches)


unittest.main()