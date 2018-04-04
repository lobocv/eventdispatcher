author = 'calvin'
import gettext
from builtins import str as basestring, str as unicode

from eventdispatcher import Property

# The translation (gettext) function to be used

def no_translation(s):
    return s
translator = no_translation


def fake_translation(s):
    """
    A fake translation function to 'french' that can help you verify that you have tagged all text in the program
    """
    return '#%s#' % s if s != '\n' else '\n'


class StringProperty(Property):
    observers = set()

    def __init__(self, default_value):
        super(StringProperty, self).__init__(default_value)
        self.translatables = set()
        if not isinstance(default_value, (str, basestring, unicode)):
            raise ValueError('StringProperty can only accepts strings.')

    def register(self, instance, property_name, default_value):
        super(StringProperty, self).register(instance, property_name, default_value)
        if isinstance(default_value, _):
            prop = instance.event_dispatcher_properties[property_name]
            prop.update({'_': default_value, 'obj': instance})
            StringProperty.observers.add(self.translate)
            self.translatables.add(instance)

    def __get__(self, obj, owner):
        value = obj.event_dispatcher_properties[self.name]['value']
        if isinstance(value, _):
            return _.translate(value)
        else:
            return value

    def __set__(self, obj, value):
        prop = obj.event_dispatcher_properties[self.name]
        if isinstance(value, _):
            # If it is tagged as translatable, register this object as an observer
            prop.update({'_': value, 'obj': obj})
            StringProperty.observers.add(self.translate)
            self.translatables.add(obj)
        else:
            if obj in self.translatables:
                self.translatables.remove(obj)
            if '_' in prop:
                del prop['_']
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
    def remove_translation():
        """
        Remove the currently set translation function and return the language back to english (or default)
        """
        StringProperty.set_translator(no_translation)

    @staticmethod
    def get_translation_function():
        global translator
        return translator

    @staticmethod
    def load_fake_translation(func=None):
        """
        Load a fake translation function to that can help you verify that you have tagged all text in the program.
        Adds 'Le' to the beginning of every string.
        """
        StringProperty.set_translator(func or fake_translation)

    @staticmethod
    def get_translator(domain, localedir=None, languages=None, class_=None, fallback=False, codeset=None):
        # Create the translation class from gettext
        translation = gettext.translation(domain, localedir, languages, class_, fallback, codeset)
        return translation.ugettext

    @staticmethod
    def set_translator(translator_func):
        global translator
        translator = translator_func

        # Dispatch the changes to all the observers
        for callback in StringProperty.observers:
            callback()


class _(unicode):
    """
    This is a wrapper to the gettext translation function _(). This wrapper allows the eventdispatcher.StringProperty
    to be automatically updated when the language (translation function) changes. In this way, all labels will be
    re-translated automatically.

    """
    def __new__(cls, s, *args, **kwargs):
        if isinstance(s, _):
            s = unicode(s.untranslated)
        if translator:
            trans = translator(s, *args, **kwargs)
            obj = super(_, cls).__new__(cls, trans, *args, **kwargs)
        else:
            obj = super(_, cls).__new__(cls, s, *args, **kwargs)
        obj.untranslated = unicode(s)
        obj._additionals = []
        return obj

    def __eq__(self, other):
        """
        Compare the fully joined string (summation of the _additionals) if comparing _ objects, otherwise compare
        the untranslated strings
        """
        if isinstance(other, _):
            return (self.untranslated == other.untranslated) and \
                   (self._additionals == other._additionals)
        else:
            return self.untranslated == other

    def __ne__(self, other):
        """
        Compare the fully translated string (including the _additionals) if comparing _ objects, otherwise compare
        the english strings
        """
        s = _.translate(self)
        if isinstance(other, _):
            return s != _.translate(other)
        else:
            return s != other

    def __add__(self, other):
        """
        Rather than creating a new _ instance of the sum of the two strings, keep the added string as a reference so
        that we can translate each individually. In this way we can make sure the following translates correctly:

            eg.

                _('Show Lines') + '\n' + (_('On') if show_lines else _('Off'))

        """
        if isinstance(other, _):
            self._additionals.append(other)
            self._additionals.extend(other._additionals)
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
            self._additionals.extend([self] * other)
        else:
            raise TypeError("can't multiply sequence by non-int of type %s" % type(other))

    def __repr__(self):
        return u"{trans} ({orig})".format(trans=_.translate(self), orig=self.untranslated)

    def __str__(self):
        return _.translate(self)

    def __unicode__(self):
        return _.translate(self)

    def __contains__(self, item):
        return item in self.untranslated or any(item in a for a in self._additionals)

    def center(self, width, fillchar=None):
        s = _.translate(self)
        return s.center(width, fillchar)

    @staticmethod
    def join_additionals(s, func=None):
        """
        Translate and return a string that contains the _ instance plus anything that was added to it.
        :param s: _ instance
        :param func: translation function
        :return: joined unicode string
        """
        l = [(func or translator)(s.untranslated)]
        for a in s._additionals:
            l.append((func or translator)(a.untranslated) if isinstance(a, _) else a)
        return u''.join(l)

    @property
    def translated(self):
        """ Return the string translated into the globally set language. """
        return _.translate(self)

    @classmethod
    def translate(cls, s, func=None):
        """ Translate a string with the specified translation function, otherwise use the globally set language. """
        if isinstance(s, cls):
            # If we were passed a translatable string object _
            if s._additionals:
                return cls.join_additionals(s, func)
            else:
                return (func or translator)(s.untranslated)
        else:
            return (func or translator)(s)

    @classmethod
    def join(cls, sep, iterable):
        """
        Method used for joining _ objects such that they return translatable strings.
        :param sep:
        :param iterable:
        :return:
        """
        for ii, s in enumerate(iterable):
            if ii == 0:
                t = cls(s)
                if isinstance(s, _):
                    t._additionals = s._additionals[:]
            else:
                t += sep
                t += s
        try:
            return t
        except UnboundLocalError:
            return _('\r')