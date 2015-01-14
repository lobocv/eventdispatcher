__author__ = 'calvin'
import unittest
import random

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher import Property


class Dispatcher(EventDispatcher):
    p = Property(10)
    p2 = Property(20)


class PropertyTest(EventDispatcherTest):
    def __init__(self, *args):
        super(PropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher.bind(p=self.assert_callback, p2=self.assert_callback)


    def test_get_property(self):
        p = self.dispatcher.get_dispatcher_property('p')
        dispatcher = self.dispatcher
        dispatcher.p = 123456789
        self.assertTrue(type(p) == Property)
        self.assertEqual(dispatcher.p, 123456789)
        test_dict = {'a': random.randint(0, 1000), 'b': random.randint(0, 1000), 'c': random.randint(0, 1000)}
        dispatcher.d = test_dict
        d = self.dispatcher.get_dispatcher_property('p2')
        for key in test_dict.keys():
            test_against = test_dict[key]
            obs_dict_value = dispatcher.d[key]
            self.assertEqual(test_against, obs_dict_value)
        self.assertTrue(type(d) == Property)

    def test_setter(self):
        expected_dispatches = 3
        self.dispatcher.bind(p=self.dispatcher.setter('p2'))
        self.dispatcher.p2 = 14
        self.dispatcher.p = 234
        self.assertEqual(self.dispatcher.p, self.dispatcher.p2)
        self.assertEqual(self.dispatch_count, expected_dispatches)


if __name__ == '__main__':
    unittest.main()
