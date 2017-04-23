__author__ = 'calvin'
import unittest
import random

from eventdispatcher import EventDispatcher, BindError
from eventdispatcher import StringProperty, _
from . import EventDispatcherTest

class Dispatcher(EventDispatcher):
    p1 = StringProperty(_('abc'))
    p2 = StringProperty(_('xyz'))


class StringPropertyTest(EventDispatcherTest):

    def __init__(self, *args):
        super(StringPropertyTest, self).__init__(*args)
        self.dispatcher = Dispatcher()
        self.dispatcher2 = Dispatcher()
        self.dispatcher.bind(p1=self.assert_callback, p2=self.assert_callback)

    def tearDown(self):
        # Always switch the language back to English, make sure to unbind first.
        try:
            self.dispatcher.unbind(p1=self.assert_callback, p2=self.assert_callback)
        except BindError:
            pass
        StringProperty.remove_translation()
        self.dispatcher.bind(p1=self.assert_callback, p2=self.assert_callback)

    @staticmethod
    def create_different_value(value):
        different_value = str(random.random())
        return different_value

    def test_translate(self):
        d = self.dispatcher
        self.assertEquals(d.p1, 'abc')
        self.assertEquals(d.p2, 'xyz')
        StringProperty.load_fake_translation()
        self.assertEquals(d.p1, '#abc#')
        self.assertEquals(d.p2, '#xyz#')

    def test_additionals(self):
        d = self.dispatcher
        d.p1 = _('abc') + ' def ' + _('ghi')
        StringProperty.load_fake_translation()
        # Notice that 'abc' and 'ghi' get translated but 'def' does not
        self.assertEquals(d.p1, '#abc# def #ghi#')
        StringProperty.remove_translation()
        self.assertEquals(d.p1, 'abc def ghi')

if __name__ == '__main__':
    unittest.main()
