__author__ = 'calvin'
import unittest
import random
import json
import numpy as np

from . import EventDispatcherTest
from builtins import range
from eventdispatcher import EventDispatcher, PropertyEncoder
from eventdispatcher.dictproperty import DictProperty, ObservableDict


class Dispatcher(EventDispatcher):
    p1 = DictProperty({})


class DictPropertyTest(EventDispatcherTest, unittest.TestCase):

    def __init__(self, *args):
        super(DictPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback)

    @staticmethod
    def create_different_value(value):
        different_value = {str(i): random.randint(0, 1000) for i in range(10)}
        while different_value == value:
            return DictPropertyTest.create_different_value(value)
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

    def test_serialize(self):
        self.dispatcher.p1 = {1: 'one', 'two': 2, 3: 3, 4: None, 5: [], 6: 2353.}
        s = json.dumps(self.dispatcher.p1, cls=PropertyEncoder)
        self.assertIsInstance(s, str)

    def test_iterate_dict(self):
        """
        For each iteration method create a set of expected items up front and then pop them off as we iterate
        at the end we should have an empty set.
        """
        values = range(10)
        keys = [str(v) for v in values]
        items = list(zip(keys, values))
        d = dict(items)
        self.dispatcher.p1 = d

        self.assertIsInstance(self.dispatcher.p1, ObservableDict)

        for method_name in ('keys', 'iterkeys', 'values', 'itervalues', 'items', 'iteritems', '__iter__'):
            if 'keys' in method_name or method_name == '__iter__':
                iterated_items = set(keys)
            elif 'values' in method_name:
                iterated_items = set(values)
            else:
                iterated_items = set(items)
            # Iterate and pop off items from expected list
            method = getattr(self.dispatcher.p1, method_name)
            for ii, k in enumerate(method()):
                iterated_items.remove(k)
            self.assertEqual(len(iterated_items), 0)

    def test_dict_update_with_dict(self):
        """ Test that the property dispatches correctly when using dict.update() method with a dict arguments"""
        self.assertEqual(self.assert_callback_count, 0)
        self.dispatcher.p1.update({1: 1, 2: 2})
        self.dispatcher.p1.update({1: 1, 2: 2})
        self.assertEqual(self.assert_callback_count, 1)
        self.dispatcher.p1.update({1: 1, 2: 2, 3: 3})
        self.assertEqual(self.assert_callback_count, 2)

    def test_dict_update_with_keyword(self):
        """ Test that the property dispatches correctly when using dict.update() method with keyword arguments"""
        self.assertEqual(self.assert_callback_count, 0)
        self.dispatcher.p1.update(one=1, two=2)
        self.dispatcher.p1.update(one=1, two=2)
        self.assertEqual(self.assert_callback_count, 1)
        self.dispatcher.p1.update(one=1, two=2, three=3)
        self.assertEqual(self.assert_callback_count, 2)

    def test_invalid_dict_comparison(self):
        """
        Test comparing dicts that have values that may not be comparable (numpy arrays).
        Numpy arrays, when compared, do not give a scalar value.
        This should register as lists not equal (even when they technically are) and dispatch the event.
        """
        d = {1: np.arange(8), 2: np.arange(2), 3: np.arange(3)}
        d2 = {1: np.arange(8), 2: np.arange(2), 3: np.arange(3)}

        self.assertEqual(self.assert_callback_count, 0)
        # Set the dictproperty to a dictionary with numpy arrays as values
        self.dispatcher.p1 = d
        # Set an equivalent numpy array and check that it still dispatches
        # The individual numpy array elements equate to a non-scalar boolean. In that case we just assume they are !=
        self.dispatcher.p1 = d2
        self.assertEqual(self.assert_callback_count, 2)

        # Check it still works for actually different arrays
        self.dispatcher.p1 = {'one': np.arange(8), 'two': np.arange(20), 'three': np.arange(3)}
        self.assertEqual(self.assert_callback_count, 3)

        # Check setting individual elements to equivalent numpy value still dispatches
        self.dispatcher.p1['two'] = self.dispatcher.p1['two'].copy()
        self.assertEqual(self.assert_callback_count, 4)

        # Check updating elements to equivalent numpy value still dispatches
        self.dispatcher.p1.update({'one': np.arange(8), 'two': np.arange(2), 'three': np.arange(3)})
        self.assertEqual(self.assert_callback_count, 5)
        # Check updating elements (via keyword) to equivalent numpy value still dispatches
        self.dispatcher.p1.update(one=np.arange(8), two=np.arange(2), three=np.arange(3))
        self.assertEqual(self.assert_callback_count, 6)



if __name__ == '__main__':
    unittest.main()
