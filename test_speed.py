__author__ = 'Calvin'

from pyperform import BenchmarkedClass, BenchmarkedFunction

from eventdispatcher import EventDispatcher, Property #!

@BenchmarkedClass(classname='Dispatcher')
class Dispatcher(EventDispatcher):
    number = Property(1)

    def __init__(self):
        super(Dispatcher, self).__init__()
        self.bind(number=self.callback)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=10, timeit_number=1000)
    def run_dispatch(self):
        for i in xrange(100):
            self.number = i

    def callback(self, inst, number):
        pass
