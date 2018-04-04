from __future__ import print_function
from builtins import range
from pyperform import BenchmarkedClass, BenchmarkedFunction

from eventdispatcher import EventDispatcher, Property, ListProperty, DictProperty, SetProperty, UnitProperty  #!
from eventdispatcher import StringProperty, LimitProperty #!
from tests.test_property import PropertyTest             #!
from tests.test_dictproperty import DictPropertyTest     #!
from tests.test_listproperty import ListPropertyTest     #!
from tests.test_setproperty import SetPropertyTest       #!
from tests.test_unitproperty import UnitPropertyTest     #!
from tests.test_stringproperty import StringPropertyTest #!
from tests.test_limitproperty import LimitPropertyTest   #!


from eventdispatcher import __version__
print("EventDispatcher Version: %s" % __version__)
print("=" * 50)


TIMEIT_REPEAT = 1
TIMEIT_NUMBER = 1
INNER_LOOP = int(1e5)  #!


@BenchmarkedClass(classname='Dispatcher')
class Dispatcher(EventDispatcher):
    listp = ListProperty([1, 2, 3])
    prop = Property(1)
    dictp = DictProperty({1: 'asd', 2: 'qwe'})
    setp = SetProperty(set(range(5)))
    unitp = UnitProperty(1.0, 'm')
    stringp = StringProperty('test')
    limitp = LimitProperty(5, min=0, max=10)

    def __init__(self):
        super(Dispatcher, self).__init__()
        self.bind(listp=self.callback, prop=self.callback, dictp=self.callback)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=TIMEIT_REPEAT, timeit_number=TIMEIT_NUMBER)
    def run_setter_prop(self):
        prev_value = self.prop
        for i in range(INNER_LOOP):
            self.prop = prev_value = PropertyTest.create_different_value(prev_value)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=TIMEIT_REPEAT, timeit_number=TIMEIT_NUMBER)
    def run_setter_listp(self):
        prev_value = self.listp
        for i in range(INNER_LOOP):
            self.listp = prev_value = ListPropertyTest.create_different_value(prev_value)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=TIMEIT_REPEAT, timeit_number=TIMEIT_NUMBER)
    def run_setter_dictprop(self):
        prev_value = self.dictp
        for i in range(INNER_LOOP):
            self.dictp = prev_value = DictPropertyTest.create_different_value(prev_value)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=TIMEIT_REPEAT, timeit_number=TIMEIT_NUMBER)
    def run_setter_setprop(self):
        prev_value = self.setp
        for i in range(INNER_LOOP):
            self.setp = prev_value = SetPropertyTest.create_different_value(prev_value)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=TIMEIT_REPEAT, timeit_number=TIMEIT_NUMBER)
    def run_setter_stringprop(self):
        prev_value = self.stringp
        for i in range(INNER_LOOP):
            self.stringp = prev_value = StringPropertyTest.create_different_value(prev_value)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=TIMEIT_REPEAT, timeit_number=TIMEIT_NUMBER)
    def run_setter_limitprop(self):
        prev_value = self.limitp
        for i in range(INNER_LOOP):
            self.limitp = prev_value = LimitPropertyTest.create_different_value(prev_value)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=TIMEIT_REPEAT, timeit_number=TIMEIT_NUMBER)
    def run_setter_unitprop(self):
        prev_value = self.unitp
        for i in range(INNER_LOOP):
            self.unitp = prev_value = UnitPropertyTest.create_different_value(prev_value)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=TIMEIT_REPEAT, timeit_number=TIMEIT_NUMBER)
    def run_dispatch(self):
        dispatch = self.dispatch
        for i in range(INNER_LOOP):
            dispatch('prop', self, self.prop)
            dispatch('dictp', self, self.dictp)
            dispatch('listp', self, self.listp)
            dispatch('setp', self, self.setp)
            dispatch('stringp', self, self.stringp)
            dispatch('limitp', self, self.limitp)
            dispatch('unitp', self, self.unitp)

    @BenchmarkedFunction(classname='Dispatcher', timeit_repeat=TIMEIT_REPEAT, timeit_number=TIMEIT_NUMBER)
    def run_getter(self):
        for i in range(INNER_LOOP):
            prop = self.prop
            listprop = self.listp
            dictprop = self.dictp

    def callback(self, inst, number):
        pass
