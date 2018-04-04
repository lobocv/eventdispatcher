__author__ = 'calvin'
import unittest
import random

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher.setproperty import SetProperty


class Dispatcher(EventDispatcher):
    p1 = SetProperty(set())


class SetPropertyTest(EventDispatcherTest, unittest.TestCase):

    def __init__(self, *args):
        super(SetPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback)

    def create_different_value(self, value):
        different_value = set([random.randint(0, 1000) for i in range(10)])
        while different_value == value:
            return self.create_different_value(value)
        else:
            return different_value

    def test_get_property(self):
        dispatcher = self.dispatcher
        set_items = [str(random.randint(0, 1000)), str(random.randint(0, 1000)), str(random.randint(0, 1000))]
        test_set = set(set_items)
        dispatcher.p1 = test_set
        p1 = dispatcher.get_dispatcher_property('p1')
        for key in test_set:
            self.assertIn(key, dispatcher.p1)

        self.assertTrue(type(p1) == SetProperty)

    def test_setproperty_dispatch(self):
        """
        Tests that the callback is called ONLY when the value changes.
        """
        expected_dispatches = 5
        self.dispatcher.p1 = {}
        self.assert_callback_count = 0
        self.dispatcher.p1.update('a',  'b')                # Dispatch 1
        self.dispatcher.p1.update('a', 'b')
        self.dispatcher.p1.update('c')                      # Dispatch 2
        self.dispatcher.p1.remove('a')                      # Dispatch 3
        self.dispatcher.p1.update('a')                      # Dispatch 5

        self.assertEqual(self.assert_callback_count, expected_dispatches)

if __name__ == '__main__':
    unittest.main()
