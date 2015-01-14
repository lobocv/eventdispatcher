__author__ = 'Calvin'

from pyperform import BenchmarkedClass, BenchmarkedFunction

from eventdispatcher import EventDispatcher, Property  #!


@BenchmarkedClass(classname='Dispatcher')
class Dispatcher(EventDispatcher):
    number = Property(1)

    def __init__(self):
        super(Dispatcher, self).__init__()
        self.bind(number=self.callback)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=10, timeit_number=100)
    def run_setter(self):
        for i in xrange(1000):
            self.number = i

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=10, timeit_number=100)
    def run_dispatch(self):
        for i in xrange(1000):
            self.dispatch('number', self, i)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=10, timeit_number=100)
    def run_getter(self):
        for i in xrange(1000):
            f = self.number

    def callback(self, inst, number):
        pass

