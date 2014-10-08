__author__ = 'calvin'

from properties import Property

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
                if isinstance(prop, Property):
                    prop.name = prop_name
                    if hasattr(self, 'on_{}'.format(prop_name)):
                        func = getattr(self, 'on_{}'.format(prop_name))
                    else:
                        func = lambda *args: False
                    self.register_event(prop_name, prop, prop.default_value)
                    bindings.update({prop_name: func})

        self.bind(**bindings)

    def dispatch(self, key, *args):
        for callback in self.eventdispatcher_callbacks[key]:
            if callback(*args):
                break

    def register_event(self, name, property, default_value):
        self.eventdispatcher_properties[name] = property
        self.eventdispatcher_property_values[name] = default_value
        self.eventdispatcher_callbacks[name] = []

    def bind(self, **kwargs):
        for prop, func in kwargs.iteritems():
            if prop not in self.eventdispatcher_properties:
                raise BindException("'{}' is not a registered property.".format(prop))
            self.eventdispatcher_callbacks[prop].append(func)

    def setter(self, prop_name):
        p = self.eventdispatcher_properties[prop_name]
        return p.fset
