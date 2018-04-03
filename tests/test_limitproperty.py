__author__ = 'calvin'
import unittest
import random

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher import LimitProperty


MIN = 0
MAX = 100

class Dispatcher(EventDispatcher):
    p1 = LimitProperty(10, min=MIN, max=MAX)
    p2 = LimitProperty(20, min=MIN, max=MAX)


class LimitPropertyTest(EventDispatcherTest, unittest.TestCase):

    def __init__(self, *args):
        super(LimitPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback, p2=self.assert_callback)

    def create_different_value(self, value):
        if isinstance(value, float):
            different_value = random.random()
        elif isinstance(value, int):
            different_value = random.randint(MIN, MAX)
        while different_value == value:
            return self.create_different_value(value)
        else:
            return different_value

    def test_lower_bound(self):
        d1 = self.dispatcher
        _min = LimitProperty.get_min(self.dispatcher, 'p1')
        new_val = _min - 10
        d1.p1 = new_val
        self.assertEquals(d1.p1, _min)

    def test_upper_bound(self):
        d1 = self.dispatcher
        _max = LimitProperty.get_max(self.dispatcher, 'p1')
        new_val = _max + 10
        d1.p1 = new_val
        self.assertEquals(d1.p1, _max)

    def test_get_min_max(self):
        _min = LimitProperty.get_min(self.dispatcher, 'p1')
        _max = LimitProperty.get_max(self.dispatcher, 'p1')
        self.assertEquals(MIN, _min)
        self.assertEquals(MAX, _max)

    def test_set_min_max(self):
        self.dispatcher.p1 = MIN
        NEW_MIN = MIN + 10
        LimitProperty.set_min(self.dispatcher, 'p1', NEW_MIN)
        self.assertEquals(self.dispatcher.p1, NEW_MIN)
        self.dispatcher.p1 = NEW_MIN - 1000
        self.assertEquals(self.dispatcher.p1, NEW_MIN)

        self.dispatcher.p1 = MAX
        NEW_MAX = MAX - 10
        LimitProperty.set_max(self.dispatcher, 'p1', NEW_MAX)
        self.assertEquals(self.dispatcher.p1, NEW_MAX)
        self.dispatcher.p1 = NEW_MAX + 1000
        self.assertEquals(self.dispatcher.p1, NEW_MAX)






if __name__ == '__main__':
    unittest.main()
