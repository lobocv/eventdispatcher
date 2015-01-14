__author__ = 'calvin'
import unittest
from . import EventDispatcherTest
import random

from eventdispatcher import EventDispatcher, DictProperty


class Dispatcher(EventDispatcher):
    d = DictProperty({})


class DictPropertyTest(EventDispatcherTest):
    def __init__(self, *args):
        super(DictPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher.bind(d=self.assert_callback)

    def test_get_property(self):
        dispatcher = self.dispatcher
        test_dict = {'a': random.randint(0, 1000), 'b': random.randint(0, 1000), 'c': random.randint(0, 1000)}
        dispatcher.d = test_dict
        d = dispatcher.get_dispatcher_property('d')
        for key in test_dict.keys():
            test_against = test_dict[key]
            obs_dict_value = dispatcher.d[key]
            self.assertEqual(test_against, obs_dict_value)

        self.assertTrue(type(d) == DictProperty)


    def test_dictproperty_dispatch(self):
        """
        Tests that the callback is called ONLY when the value changes.
        """
        expected_dispatches = 4
        self.dispatcher.d = {}
        self.dispatcher.d.update({1: 1, 2: 2})
        self.dispatcher.d[3] = 3
        self.dispatcher.d[3] = 3
        self.dispatcher.d = {4: 'Test'}

        self.assertEqual(self.dispatch_count, expected_dispatches)

if __name__ == '__main__':
    unittest.main()
