__author__ = 'Calvin'

from pyperform import BenchmarkedClass, BenchmarkedFunction

from eventdispatcher import EventDispatcher, Property, ListProperty, DictProperty  #!
from unit_tests import EventDispatcherTest #!

from eventdispatcher import __version__
print __version__

@BenchmarkedClass(classname='Dispatcher')
class Dispatcher(EventDispatcher):
    # p = ListProperty([1,2,3])
    p = Property(1)
    # p = DictProperty({1: 'asd'})
    N_dispatches = 1000

    def __init__(self):
        super(Dispatcher, self).__init__()
        self.bind(p=self.callback)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=10, timeit_number=100)
    def run_setter(self):
        for i in xrange(Dispatcher.N_dispatches):
            self.p = EventDispatcherTest.create_different_value(self.p)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=10, timeit_number=100)
    def run_dispatch(self):
        for i in xrange(Dispatcher.N_dispatches):
            self.dispatch('p', self, i)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=10, timeit_number=100)
    def run_getter(self):
        for i in xrange(Dispatcher.N_dispatches):
            f = self.p

    def callback(self, inst, number):
        pass

if __name__ == '__main__':
    d = Dispatcher()
    print d.p
    p = d.p
    dsfgh=4
