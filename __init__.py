__author__ = 'calvin'

from PygameWidgets.core.eventdispatcher.properties import Property

class BindException(Exception):
    pass

class EventDispatcher(object):

    def __init__(self):
        self.properties = {}
        self.callbacks = {}
        bindings = {}
        for key, value in self.__class__.__dict__.iteritems():
            if isinstance(value, Property):
                if hasattr(self, 'on_{}'.format(key)):
                    func = getattr(self, 'on_{}'.format(key))
                else:
                    func = lambda *args: False
                self.register_event(key)
                bindings.update({key: func})
        self.bind(**bindings)

    def dispatch(self, key, *args):
        for callback in self.callbacks[key]:
            if callback(*args):
                break

    def register_event(self, name):
        self.properties[name] = []
        self.callbacks[name] = []

    def bind(self, **kwargs):
        for prop, func in kwargs.iteritems():
            if prop not in self.properties:
                raise BindException("'{}' is not a registered property.")
            self.callbacks[prop].append(func)
