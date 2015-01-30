__author__ = 'Calvin'

import unittest
import random

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher.dictproperty import DictProperty


class Dispatcher(EventDispatcher):
    p1 = DictProperty({})

    def __init__(self):
        super(Dispatcher, self).__init__()
        self.register_event('event1')
        self.register_event('event2')
        self.event1_call_count = 0
        self.event2_call_count = 0

    def on_event1(self, *args):
        self.event1_call_count += 1

    def on_event2(self, *args):
        self.event2_call_count += 1

class EventTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(EventTest, self).__init__(*args, **kwargs)
        self.d = Dispatcher()
        self.count = 0

    def increase_count(self, *args):
        self.count += 1

    def tearDown(self):
        self.d.event1_call_count = 0
        self.d.event2_call_count = 0
        self.count = 0

    def test_dispatch_event(self):
        d = self.d
        self.assertEqual(d.event1_call_count, 0)
        self.assertEqual(d.event2_call_count, 0)
        d.dispatch_event('event1')
        d.dispatch_event('event2')
        self.assertEqual(d.event1_call_count, 1)
        self.assertEqual(d.event2_call_count, 1)

    def test_bind_event(self):
        d = self.d
        d.bind(event1=self.increase_count)
        self.assertEqual(self.count, 0)
        d.dispatch_event('event1')
        self.assertEqual(self.count, 1)
        d.unbind(event1=self.increase_count)
        d.dispatch_event('event1')
        self.assertEqual(self.count, 1)

if __name__ == '__main__':
    unittest.main()