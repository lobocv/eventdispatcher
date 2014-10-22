__author__ = 'calvin'
__version__ = '1.0.1'

from properties import BaseProperty, DictProperty, ObservableDict

class BindException(Exception):
    pass

class EventDispatcher(object):

    def __init__(self, **kwargs):
        self.eventdispatcher_properties = {}
        self.eventdispatcher_property_values = {}
        self.eventdispatcher_callbacks = {}
        bindings = {}
        # Walk through the MRO looking for Property attributes in the classes. Then register and bind them to
        # 'on_<prop_name>' if it exists.
        for cls in self.__class__.__mro__:
            for prop_name, prop in cls.__dict__.iteritems():
                if isinstance(prop, BaseProperty):
                    prop.name = prop_name
                    self.register_property(prop_name, prop, prop.default_value)
                    if hasattr(self, 'on_{}'.format(prop_name)):
                        func = getattr(self, 'on_{}'.format(prop_name))
                        bindings.update({prop_name: func})

        self.bind(**bindings)

    def dispatch(self, key, *args):
        for callback in self.eventdispatcher_callbacks[key]:
            if callback(*args):
                break

    def register_property(self, name, property, default_value):
        if isinstance(property, DictProperty):
            default_value = ObservableDict(default_value.dictionary, property)
            default_value.eventdispatcher = self

        self.eventdispatcher_properties[name] = property
        self.eventdispatcher_property_values[name] = default_value
        self.eventdispatcher_callbacks[name] = []

    def register_event(self, name):
        self.eventdispatcher_callbacks[name] = [getattr(self, 'on_{}'.format(name))] if\
                                                hasattr(self, 'on_{}'.format(name)) else []

    def bind(self, **kwargs):
        for prop, func in kwargs.iteritems():
            if prop not in self.eventdispatcher_callbacks:
                raise BindException("'{}' is not a registered property.".format(prop))
            self.eventdispatcher_callbacks[prop].append(func)

    def setter(self, prop_name):
        p = self.eventdispatcher_properties[prop_name]
        return p.fset
