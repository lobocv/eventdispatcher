__author__ = 'calvin'

import gettext

from eventdispatcher import Property


translator = None

def fake_translation(s):
    return 'Le %s' % s if s != '\n' else '\n'

class StringProperty(Property):
    observers = set()

    def __init__(self, default_value):
        super(StringProperty, self).__init__(default_value)
        self.translatables = set()
        if not isinstance(default_value, basestring):
            raise ValueError('StringProperty can only accepts strings.')

    def register(self, instance, property_name, default_value):
        super(StringProperty, self).register(instance, property_name, default_value)
        if isinstance(default_value, _):
            prop = instance.event_dispatcher_properties[property_name]
            prop.update({'_': default_value, 'obj': instance})
            StringProperty.observers.add(self.translate)
            self.translatables.add(instance)

    def __set__(self, obj, value):
        prop = obj.event_dispatcher_properties[self.name]
        if isinstance(value, _):
            # If it is tagged as translatable, register this object as an observer
            prop.update({'_': value, 'obj': obj})
            StringProperty.observers.add(self.translate)
            self.translatables.add(obj)
        if value != prop['value']:
            prop['value'] = value
            for callback in prop['callbacks']:
                if callback(obj, value):
                    break

    def translate(self):
        for obj in self.translatables:
            prop = obj.event_dispatcher_properties[self.name]
            prop['value'] = _.translate(prop['_'])
            for callback in prop['callbacks']:
                callback(prop['obj'], prop['value'])

    @staticmethod
    def switch_lang(lang):
        global translator
        # get the right locales directory, and instanciate a gettext
        #locale_dir = os.path.join(os.path.dirname(__file__), 'data', 'locales')
        if lang == 'english':
            translator = None
        else:
            # locales = gettext.translation(lang, _.locale_dir, languages=['languages'])
            # _.lang = locales.ugettext
            translator = lang

        # Dispatch the changes to all the observers
        for callback in StringProperty.observers:
            callback()


class _(str):
    """
    This is a wrapper to the gettext translation function _(). This wrapper allows the eventdispatcher.StringProperty
    to be automatically updated when the language (translation function) changes. In this way, all labels will be
    re-translated automatically.

    """

    def __new__(cls, s, *args, **kwargs):
        if translator:
            trans = translator(s, *args, **kwargs)
            obj = super(_, cls).__new__(cls, trans, *args, **kwargs)
        else:
             obj = super(_, cls).__new__(cls, s, *args, **kwargs)
        obj.untranslated = s
        return obj

    def __eq__(self, other):
        """
        Compare the fully translated string (including the _additionals) if comparing _ objects, otherwise compare
        the english strings
        """
        if isinstance(other, _):
            return _.translate(self) == _.translate(other)
        else:
            return super(_, self).__eq__(other)

    def __ne__(self, other):
        """
        Compare the fully translated string (including the _additionals) if comparing _ objects, otherwise compare
        the english strings
        """
        if isinstance(other, _):
            return _.translate(self) != _.translate(other)
        else:
            return super(_, self).__ne__(other)

    def __add__(self, other):
        """
        Rather than creating a new _ instance of the sum of the two strings, keep the added string as a reference so
        that we can translate each individually. In this way we can make sure the following translates correctly:

            eg.

                _('Show Lines') + '\n' + (_('On') if show_lines else _('Off'))

        """
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
        if translator is None:
            return ''.join([s.untranslated] + s._additionals)
        else:
            l = [translator(s.untranslated)]
            for a in s._additionals:
                l.append(translator(a.untranslated) if isinstance(a, _) else a)
            return ''.join(l)

    @staticmethod
    def translate(s, *args, **kwargs):
        if hasattr(s, '_additionals'):
            return _.join_additionals(s)
        else:
            if translator is None:
                return s.untranslated.format(args, kwargs)
            else:
                return translator(s).format(args, kwargs)


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

    def to_french(s):
        return 'Le ' + s

    def to_G(s):
        return 'G_' + s

    StringProperty.switch_lang(to_french)
    t = Trans()
    t2 = Trans()
    t2.s, t2.g

    s = _('{} {} {}'.format('1', 'two', '3'))
    t.s = s
    t.g = _('abc {}')
    StringProperty.switch_lang(to_G)
    StringProperty.switch_lang(to_french)


    # Test adding _'s
    asd = _('asd')
    qwe = _('qwe')

    asdqwe = asd + qwe
    assert isinstance(asdqwe, _)


    StringProperty.switch_lang(to_G)
    sdf=3

