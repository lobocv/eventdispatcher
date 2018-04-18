__author__ = 'calvin'

import json
import random
import unittest
import numpy as np
from builtins import range
from eventdispatcher import EventDispatcher, ListProperty, PropertyEncoder
from . import EventDispatcherTest


class Dispatcher(EventDispatcher):
    p1 = ListProperty([])
    p2 = ListProperty([])


class ListPropertyTest(EventDispatcherTest, unittest.TestCase):
    def __init__(self, *args):
        super(ListPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback, p2=self.assert_callback)
        self.dispatcher2.bind(p1=self.assert_callback, p2=self.assert_callback)

    @staticmethod
    def create_different_value(value):
        different_value = [random.randint(0, 1000) for i in range(10)]
        while different_value == value:
            return ListPropertyTest.create_different_value(value)
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

    def test_tuple_assignment(self):
        value = self.create_different_value(self.dispatcher.p1)
        self.dispatcher.p1 = value
        self.assertEqual(self.assert_callback_count, 1)
        self.dispatcher.p1 = tuple(value)
        self.assertEqual(self.assert_callback_count, 1)
        self.dispatcher.p1 = self.create_different_value(self.dispatcher.p1)
        self.assertEqual(self.assert_callback_count, 2)
        self.dispatcher.p1 = tuple(self.create_different_value(self.dispatcher.p1))
        self.assertEqual(self.assert_callback_count, 3)

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
        self.assertIsInstance(s, str)

    def test_iterators(self):
        _list = [1, 2, 3, 4, 5]
        self.dispatcher.p1 = _list
        self.assertEqual(self.assert_callback_count, 1)
        for ii, v in enumerate(self.dispatcher.p1):
            self.assertEqual(v, _list[ii])

    def test_list_comparing(self):
        """
        Test comparing lists that have elements that may not be comparable (numpy arrays).
        Numpy arrays, when compared, do not give a scalar value.
        This should register as lists not equal even when they technically are.
        """

        # initialize a list value
        self.dispatcher.p1 = [1, 2, 3]
        self.assertEqual(self.assert_callback_count, 1)
        # Set the listproperty to an equal lengthed list (so it compares elements)
        self.dispatcher.p1 = [np.arange(8), np.arange(2), np.arange(3)]
        # Set an equivalent numpy array and check that it still dispatches
        # The individual numpy array elements equate to a non-scalar boolean. In that case we just assume they are !=
        self.dispatcher.p1 = [np.arange(8), np.arange(2), np.arange(3)]
        self.assertEqual(self.assert_callback_count, 3)
        # Check it still works for actually different arrays
        self.dispatcher.p1 = [np.arange(800), np.arange(200), np.arange(300)]
        self.assertEqual(self.assert_callback_count, 4)
        # Check that setting an item individually will dispatch (even though they are equal)
        self.dispatcher.p1[1] = self.dispatcher.p1[1]
        self.assertEqual(self.assert_callback_count, 5)


if __name__ == '__main__':
    unittest.main(module=__file__)

