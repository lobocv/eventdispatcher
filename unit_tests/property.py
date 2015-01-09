__author__ = 'calvin'
import unittest
import random

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher import Property, DictProperty, ListProperty


class Dispatcher(EventDispatcher):
    p = Property(10)
    p2 = Property(20)


class PropertyTest(EventDispatcherTest):
    def __init__(self, *args):
        super(PropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher.bind(p=self.assert_callback, p2=self.assert_callback)


    def test_get_property(self):
        p = Property.get_property(self.dispatcher, 'p')
        dispatcher = self.dispatcher
        dispatcher.p = 123456789
        self.assertTrue(type(p) == Property)
        self.assertEqual(dispatcher.p, 123456789)
        test_dict = {'a': random.randint(0, 1000), 'b': random.randint(0, 1000), 'c': random.randint(0, 1000)}
        dispatcher.d = test_dict
        d = Property.get_property(self.dispatcher, 'p2')
        for key in test_dict.keys():
            test_against = test_dict[key]
            obs_dict_value = dispatcher.d[key]
            self.assertEqual(test_against, obs_dict_value)

        self.assertTrue(type(d) == Property)

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

if __name__ == '__main__':
    unittest.main()
