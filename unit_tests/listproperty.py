__author__ = 'calvin'

import unittest

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher import ListProperty


class Dispatcher(EventDispatcher):
    l = ListProperty([])


class ListPropertyTest(EventDispatcherTest):
    def __init__(self, *args):
        super(ListPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(l=self.assert_callback)
        self.dispatcher2.bind(l=self.assert_callback)

    def test_mutability(self):
        d, d2 = self.dispatcher, self.dispatcher2
        d.l = [1, 2, 3]
        d2.l = [4, 5, 6]
        self.assertNotEquals(d.l, d2.l)
        self.assertEqual(self.dispatch_count, 2)

        d.l.append(1)
        d2.l.append(2)
        self.assertNotEquals(d.l, d2.l)
        self.assertEqual(self.dispatch_count, 4)

    def test_append(self):
        d, d2 = self.dispatcher, self.dispatcher2
        d.l.append(1)
        d.l.append(2)
        d.l.append(3)
        self.assertEqual(d.l, [1, 2, 3])
        self.assertEqual(self.dispatch_count, 3)

    def test_set_new_list(self):
        d, d2 = self.dispatcher, self.dispatcher2
        d.l = [1, 2, 3]
        d2.l = [4, 5, 6]
        self.assertEquals(d.l, [1, 2, 3])
        self.assertEquals(d2.l, [4, 5, 6])
        self.assertEqual(self.dispatch_count, 2)

    def test_pop(self):
        d, d2 = self.dispatcher, self.dispatcher2
        d.l = [1, 2, 3]
        last = d.l.pop()
        self.assertEqual(last, 3)
        self.assertEqual(len(d.l), 2)
        self.assertEqual(len(d2.l), 0)
        self.assertEqual(self.dispatch_count, 2)

    def test_extend(self):
        d, d2 = self.dispatcher, self.dispatcher2
        d.l.extend([1, 2, 3])
        self.assertEqual(d.l, [1, 2, 3])
        d.l.extend([1, 2, 3])
        self.assertEqual(d.l, [1, 2, 3] * 2)
        self.assertEqual(self.dispatch_count, 2)


if __name__ == '__main__':
    unittest.main(module=__file__)

