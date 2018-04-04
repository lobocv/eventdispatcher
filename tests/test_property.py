__author__ = 'calvin'
import unittest
import random

from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher import Property


class Dispatcher(EventDispatcher):
    p1 = Property(10)
    p2 = Property(20)


class PropertyTest(EventDispatcherTest, unittest.TestCase):

    def setUp(self):
        super(PropertyTest, self).setUp()
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback, p2=self.assert_callback)
