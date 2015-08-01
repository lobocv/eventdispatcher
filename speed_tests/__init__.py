__author__ = 'Calvin'

from pyperform import BenchmarkedClass, BenchmarkedFunction

from eventdispatcher import EventDispatcher, StringProperty, ListProperty, DictProperty  #!
from eventdispatcher import SetProperty
from tools import force_dispatcher  #!

from eventdispatcher import __version__

print 'EventDispatcher version %s' % __version__

TN = 1
TR = 1


class SpeedTester(EventDispatcher):
    p = DictProperty({1: 'asd'})

    def __init__(self):
        super(SpeedTester, self).__init__()
        self.bind(p=self.callback)
        property_class = self.get_dispatcher_property('p').__class__.__name__
        self.create_different_value = force_dispatcher[property_class]



@BenchmarkedFunction(classname='SpeedTester', timeit_repeat=TR, timeit_number=TN)
def run_setter():
    property_class = dispatcher.get_dispatcher_property('p').__class__.__name__
    create_different_value = force_dispatcher[property_class]
    for i in xrange(1000):
        dispatcher.p = create_different_value(dispatcher.p)

@BenchmarkedFunction(classname='SpeedTester', timeit_repeat=TR, timeit_number=TN)
def run_dispatch(self):
    for i in xrange(1000):
        self.dispatch('p', self, i)

@BenchmarkedFunction(classname='SpeedTester', timeit_repeat=TR, timeit_number=TN)
def run_getter(self):
    for i in xrange(1000):
        f = self.p

    def callback(self, inst, number):
        pass

BaseSpeedTester = SpeedTester
print '\nDictProperty'


@BenchmarkedClass(classname='SpeedTester')
class SpeedTester(SpeedTester):
    p = DictProperty({1: 'asd'})


print '\nListProperty'


@BenchmarkedClass(classname='SpeedTester')
class SpeedTester(BaseSpeedTester):
    p = ListProperty([1, 2, 3])


print '\nStringProperty'


@BenchmarkedClass(classname='SpeedTester')
class SpeedTester(SpeedTester):
    p = StringProperty('asd')


print '\nSetProperty'


@BenchmarkedClass(classname='SpeedTester')
class SpeedTester(SpeedTester):
    p = SetProperty({1})


if __name__ == '__main__':
    print 'Running speed tests:'
