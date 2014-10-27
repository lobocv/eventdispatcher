__author__ = 'calvin'
''' Work-around to allow imports of a high level package.'''
import sys
import os
cwd = os.path.dirname(os.path.realpath(__file__))
module_path = os.path.split(cwd)[0]
module_parent_dir = os.path.split(module_path)[0]
if __name__ == '__main__':

    sys.path.append(module_parent_dir)


import unittest
from eventdispatcher import EventDispatcher
from eventdispatcher.properties import Property, DictProperty, ListProperty


import unittest


class Dispatcher(EventDispatcher):
    l = ListProperty([])

class TestListProperty(unittest.TestCase):

    def __init__(self, *args):
        super(TestListProperty, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(l=self.assert_callback)
        self.dispatcher2.bind(l=self.assert_callback)

    def assert_callback(self, inst, value):
        self.dispatch_count += 1
        print 'TestListProperty: Dispatching value {}'.format(value)


    def setUp(self):
        self.dispatch_count = 0

    def tearDown(self):
        self.dispatch_count = 0

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



unittest.main()