__author__ = 'clobo'
import gettext


class _(str):
    """
    This is a wrapper to the gettext translation function _(). This wrapper allows kivy properties to be automatically
    updated when the language (translation function) changes. In this way, all labels will be retranslated automatically.
    Example taken from : https://github.com/tito/kivy-gettext-example.

    :Usage: In main.py import this class and set _.locale_dir to the path of the locale directory of the app.
            Import this class into every file that requires translations. For importing into kv files add #:import _ PyUIFramework.Translations._
            This class binds to the 'language' property of SSI_App. Upon changes to 'language' the _.switch_language function
            is called with the language value. It searches the locale/languages/LC_MESSAGES/ directory for a .mo file with the name of language and loads it.
    """
    locale_dir = ''
    observers = []
    lang = None

    def __new__(cls, s, *args, **kwargs):
        if _.lang is None:
            pass  #_.switch_lang('French')
        s = _.translate(s, *args, **kwargs)
        return super(_, cls).__new__(cls, s)

    @staticmethod
    def translate(s, *args, **kwargs):
        if _.lang is None:
            return s.format(args, kwargs)
        else:
            return _.lang(s).format(args, kwargs)

    @staticmethod
    def bind(**kwargs):
        _.observers.append(kwargs['_'])

    @staticmethod
    def switch_lang(lang):
        # get the right locales directory, and instanciate a gettext
        #locale_dir = os.path.join(os.path.dirname(__file__), 'data', 'locales')
        if lang == 'English':
            _.lang = None
        else:
            locales = gettext.translation(lang, _.locale_dir, languages=['languages'])
            _.lang = locales.ugettext
        # update all the kv rules attached to this text
        for callback in _.observers:
            callback()

if __name__ == '__main__':

    def func():
        asd = _('do something cool')
    qwe = _('no I dont want to')
    func()
    sdfsd=3