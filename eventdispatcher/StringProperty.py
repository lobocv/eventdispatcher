__author__ = 'calvin'

import gettext

from eventdispatcher import Property
from weakref import WeakSet


class StringProperty(Property):
    observers = []
    lang = None

    def __init__(self, default_value):
        super(StringProperty, self).__init__(default_value)
        self.translatables = []
        if not isinstance(default_value, basestring):
            raise ValueError('StringProperty can only accepts strings.')

    def __set__(self, obj, value):
        if isinstance(value, _):
            prop = obj.event_dispatcher_properties[self.name]
            if '_' in prop:
                value = value.translate()
            else:
                # If it is tagged as translatable, register this object as an observer
                prop.update({'_': value, 'obj': obj})
                StringProperty.observers.append(self.translate)
                value = _.translate(value)
                self.translatables.append(prop)

        if value != obj.event_dispatcher_properties[self.name]['value']:
            prop = obj.event_dispatcher_properties[self.name]
            prop['value'] = value
            for callback in prop['callbacks']:
                if callback(obj, value):
                    break

    def translate(self):
        for prop in self.translatables:
            prop['value'] = _.translate(prop['_'])
            for callback in prop['callbacks']:
                callback(prop['obj'], prop['value'])

    @staticmethod
    def switch_lang(lang):
        # get the right locales directory, and instanciate a gettext
        #locale_dir = os.path.join(os.path.dirname(__file__), 'data', 'locales')
        if lang == 'english':
            _.lang = None
        else:
            # locales = gettext.translation(lang, _.locale_dir, languages=['languages'])
            # _.lang = locales.ugettext
            _.lang = lang
        for callback in StringProperty.observers:
            callback()



class _(str):
    """
    This is a wrapper to the gettext translation function _(). This wrapper allows the eventdispatcher.StringProperty
    to be automatically updated when the language (translation function) changes. In this way, all labels will be
    re-translated automatically.

    """
    lang = None

    def __init__(self, s, *args, **kwargs):
        super(_, self).__init__(s, *args, **kwargs)

    @staticmethod
    def translate(s, *args, **kwargs):
        if _.lang is None:
            return s.format(args, kwargs)
        else:
            return _.lang(s).format(args, kwargs)

if __name__ == '__main__':

    from eventdispatcher import EventDispatcher

    class Trans(EventDispatcher):
        s = StringProperty('testing')
        g = StringProperty('cheese')

        def on_s(self, inst, s):
            print s

        def on_g(self, inst, g):
            print g

    class Trans2(EventDispatcher):
        s = StringProperty('blah')
        g = StringProperty('blue')

    @staticmethod
    def to_T(s):
        return 'T_' + s

    @staticmethod
    def to_G(s):
        return 'G_' + s

    t = Trans()
    t2 = Trans()
    t2.s, t2.g
    t.s = _('{} {} {}'.format('1', 'two', '3'))
    t.g = _('abc {}')

    StringProperty.switch_lang(to_T)
    StringProperty.switch_lang(to_G)
    sdf=3

