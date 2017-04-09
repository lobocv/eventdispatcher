__author__ = 'calvin'
import unittest
import random

from pyperform import timer


from . import EventDispatcherTest
from eventdispatcher import EventDispatcher
from eventdispatcher import Property



class Dispatcher(EventDispatcher):
    p1 = Property(10)
    p2 = Property(20)



class PropertyTest(EventDispatcherTest): #!

    def __init__(self, *args):
        super(PropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback, p2=self.assert_callback)

    @staticmethod
    def create_different_value(value):
        if isinstance(value, float):
            different_value = random.random()
        elif isinstance(value, int):
            different_value = random.randint(0, 1000)
        while different_value == value:
            return PropertyTest.create_different_value(value)
        else:
            return different_value




class PropertySpeedTest(EventDispatcher):
    N_dispatches = 10000
    p = Property(10)

    @timer
    def run_setter(self):
        for i in xrange(PropertySpeedTest.N_dispatches):
            self.p = PropertyTest.create_different_value(self.p)

    @timer
    def run_dispatch(self):
        for i in xrange(PropertySpeedTest.N_dispatches):
            self.dispatch('p', self, i)

    @timer
    def run_getter(self):
        for i in xrange(PropertySpeedTest.N_dispatches):
            f = self.p


speedtest = PropertySpeedTest()
speedtest.run_getter()
speedtest.run_setter()
speedtest.run_dispatch()



if __name__ == '__main__':
    unittest.main()
