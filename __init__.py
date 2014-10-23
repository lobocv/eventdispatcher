__author__ = 'calvin'
__version__ = '1.1.0'

from properties import BaseProperty, DictProperty, ObservableDict
import copy

class BindException(Exception):
    pass

class EventDispatcher(object):

    def __init__(self, **kwargs):
        self._events = {}
        bindings = {}
        # Walk through the MRO looking for Property attributes in the classes. Then register and bind them to
        # 'on_<prop_name>' if it exists.
        for cls in self.__class__.__mro__:
            for prop_name, prop in cls.__dict__.iteritems():
                if isinstance(prop, BaseProperty):
                    prop.name = prop_name
                    prop.register(self, prop_name, prop.default_value)
                    if hasattr(self, 'on_{}'.format(prop_name)):
                        func = getattr(self, 'on_{}'.format(prop_name))
                        bindings.update({prop_name: func})

        self.bind(**bindings)

    def dispatch(self, key, *args):
        prop = BaseProperty.get_property(self, key)
        for callback in prop.instances[self]['callbacks']:
            if callback(*args):
                break

    def dispatch_event(self, event, *args):
        for callback in self._events[event]:
            if callback(*args):
                break

    def register_event(self, name):
        self._events[name] = [getattr(self, 'on_{}'.format(name))] if hasattr(self, 'on_{}'.format(name)) else []

    def bind(self, **kwargs):
        for prop_name, callback in kwargs.iteritems():
            try:
                # Queue the callback into the property
                prop = BaseProperty.get_property(self, prop_name)
                prop.instances[self]['callbacks'].append(callback)
            except KeyError:
                # If a property was not found, search in events
                self._events[prop_name].append(callback)


    def setter(self, prop_name):
        p = self.eventdispatcher_properties[prop_name]
        return p.fset
