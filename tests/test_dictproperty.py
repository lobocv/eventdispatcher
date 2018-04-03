__author__ = 'calvin'
import unittest
import random
import json

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher, PropertyEncoder
from eventdispatcher.dictproperty import DictProperty


class Dispatcher(EventDispatcher):
    p1 = DictProperty({})


class DictPropertyTest(EventDispatcherTest, unittest.TestCase):

    def __init__(self, *args):
        super(DictPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback)

    def create_different_value(self, value):
        different_value = {str(i): random.randint(0, 1000) for i in xrange(10)}
        while different_value == value:
            return self.create_different_value(value)
        else:
            return different_value

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

    def test_iter(self):
        self.dispatcher.p1 = {i: chr(i) for i in range(5)}
        key = 0
        for k in self.dispatcher.p1:
            self.assertEqual(k, key)
            key += 1

        for k, v in self.dispatcher.p1.iteritems():
            self.assertEqual(chr(k), v)

        key = 0
        for v in self.dispatcher.p1.itervalues():
            self.assertEqual(chr(key), v)
            key += 1

    def test_serialize(self):
        self.dispatcher.p1 = {1: 'one', 'two': 2, 3: 3, 4: None, 5: [], 6: 2353.}
        s = json.dumps(self.dispatcher.p1, cls=PropertyEncoder)
        assert isinstance(s, basestring)


if __name__ == '__main__':
    unittest.main()
