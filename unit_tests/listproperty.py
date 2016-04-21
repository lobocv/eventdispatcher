__author__ = 'calvin'

import unittest
import random
import json

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher, ListProperty, PropertyEncoder


class Dispatcher(EventDispatcher):
    p1 = ListProperty([])
    p2 = ListProperty([])


class ListPropertyTest(EventDispatcherTest):
    def __init__(self, *args):
        super(ListPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback, p2=self.assert_callback)
        self.dispatcher2.bind(p1=self.assert_callback, p2=self.assert_callback)

    def create_different_value(self, value):
        different_value = [random.randint(0, 1000) for i in xrange(10)]
        while different_value == value:
            return self.create_different_value(value)
        else:
            return different_value

    def test_mutability(self):
        d, d2 = self.dispatcher, self.dispatcher2
        d.p1 = [1, 2, 3]
        d2.p1 = [4, 5, 6]
        self.assertNotEquals(d.p1, d2.p1)
        self.assertEqual(self.assert_callback_count, 2)

        d.p1.append(1)
        d2.p1.append(2)
        self.assertNotEquals(d.p1, d2.p1)
        self.assertEqual(self.assert_callback_count, 4)

    def test_append(self):
        d, d2 = self.dispatcher, self.dispatcher2
        d.p1.append(1)
        d.p1.append(2)
        d.p1.append(3)
        self.assertEqual(d.p1, [1, 2, 3])
        self.assertEqual(self.assert_callback_count, 3)

    def test_pop(self):
        d, d2 = self.dispatcher, self.dispatcher2
        d.p1 = [1, 2, 3]
        last = d.p1.pop()
        self.assertEqual(last, 3)
        self.assertEqual(len(d.p1), 2)
        self.assertEqual(len(d2.p1), 0)
        self.assertEqual(self.assert_callback_count, 2)

    def test_extend(self):
        d, d2 = self.dispatcher, self.dispatcher2
        d.p1.extend([1, 2, 3])
        self.assertEqual(d.p1, [1, 2, 3])
        d.p1.extend([1, 2, 3])
        self.assertEqual(d.p1, [1, 2, 3] * 2)
        self.assertEqual(self.assert_callback_count, 2)

    def test_insert(self):
        d, d2 = self.dispatcher, self.dispatcher2
        d.p1 = [1, 3]
        self.assert_callback_count = 0
        d.p1.insert(1, 2)
        self.assertEqual(d.p1, [1, 2, 3])
        self.assertEqual(self.assert_callback_count, 1)

    def test_serialize(self):
        self.dispatcher.p1 = range(10)
        s = json.dumps(self.dispatcher.p1, cls=PropertyEncoder)
        assert isinstance(s, basestring)


if __name__ == '__main__':
    unittest.main(module=__file__)

