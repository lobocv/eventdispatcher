__author__ = 'calvin'

import gettext

from eventdispatcher import Property


class StringProperty(Property):
    observers = set()
    lang = None

    def __init__(self, default_value):
        super(StringProperty, self).__init__(default_value)
        self.translatables = []
        if not isinstance(default_value, basestring):
            raise ValueError('StringProperty can only accepts strings.')

    def __set__(self, obj, value):
        prop = obj.event_dispatcher_properties[self.name]
        if isinstance(value, _):
            # If it is tagged as translatable, register this object as an observer
            prop.update({'_': value, 'obj': obj})
            StringProperty.observers.add(self.translate)
            value = _.translate(value)
            self.translatables.append(prop)
        if value != prop['value']:
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
    count = 0

    def __init__(self, s, *args, **kwargs):
        super(_, self).__init__(s, *args, **kwargs)

    ''' Make comparisons of _ instances always equal False in order to correctly dispatch Properties that contain
        _ instances such as DictProperty and ListProperty. Otherwise it will only compare the _ value and not it's
        _additionals, which might change.

        For example, assigning the value of the following expression will not trigger a dispatch when the value of
        screen_saver changes, because the resultant _ object is still equal to "Screen Saver" but the _._additionals
        change from _("ON") to _("OFF")

            _("Screen Saver") + '\n' + (_('ON' if screen_saver else _('OFF')))
        '''
    def __eq__(self, other):
        if isinstance(other, _):
            return False
        else:
            return super(_, self).__eq__(other)

    def __ne__(self, other):
        if isinstance(other, _):
            return True
        else:
            return super(_, self).__ne__(other)

    def __add__(self, other):
        if not hasattr(self, '_additionals'):
            self._additionals = []

        if isinstance(other, _):
            self._additionals.append(other)
        else:
            self._additionals.append(other)

        return self

    def __mul__(self, other):
        if type(other) is bool:
            if other:
                return self
            else:
                return ''
        if type(other) is int:
            if not hasattr(self, '_additionals'):
                self._additionals = []
            self._additionals.extend([self] * other)
        else:
            raise TypeError("can't multiply sequence by non-int of type %s" % type(other))

    @staticmethod
    def join_additionals(s):
        if _.lang is None:
            return ''.join([s] + s._additionals)
        else:
            l = [s]
            for a in s._additionals:
                l.append(_.lang(a) if isinstance(a, _) else a)
            return ''.join(l)

    @staticmethod
    def translate(s, *args, **kwargs):
        if hasattr(s, '_additionals'):
            return _.join_additionals(s)
        else:
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

    # Test adding _'s
    asd = _('asd')
    qwe = _('qwe')

    asdqwe = asd + qwe
    assert isinstance(asdqwe, _)

    StringProperty.switch_lang(to_T)
    StringProperty.switch_lang(to_G)
    sdf=3

