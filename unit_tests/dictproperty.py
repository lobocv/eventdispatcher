__author__ = 'calvin'
import unittest
import random

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher.dictproperty import DictProperty


class Dispatcher(EventDispatcher):
    p1 = DictProperty({})


class DictPropertyTest(EventDispatcherTest):

    def __init__(self, *args):
        super(DictPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback)

    def test_get_property(self):
        dispatcher = self.dispatcher
        test_dict = {'a': random.randint(0, 1000), 'b': random.randint(0, 1000), 'c': random.randint(0, 1000)}
        dispatcher.p1 = test_dict
        p1 = dispatcher.get_dispatcher_property('p1')
        for key in test_dict.keys():
            test_against = test_dict[key]
            obs_dict_value = dispatcher.p1[key]
            self.assertEqual(test_against, obs_dict_value)
        self.assertTrue(type(p1) == DictProperty)

    def test_dictproperty_dispatch(self):
        """
        Tests that the callback is called ONLY when the value changes.
        """
        expected_dispatches = 5
        self.dispatcher.p1 = {}
        self.assert_callback_count = 0
        self.dispatcher.p1.update({'a': 1, 'b': 2})         # Dispatch 1
        self.dispatcher.p1.update({'a': 1, 'b': 2})
        self.dispatcher.p1.update(a=1, b=2)
        self.dispatcher.p1.update(c=3)                      # Dispatch 2
        self.dispatcher.p1[3] = 3                           # Dispatch 3
        self.dispatcher.p1[3] = 3
        del self.dispatcher.p1[3]                           # Dispatch 4
        self.dispatcher.p1 = {4: 'Test'}                    # Dispatch 5

        self.assertEqual(self.assert_callback_count, expected_dispatches)


if __name__ == '__main__':
    unittest.main()
