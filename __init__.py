__author__ = 'calvin'

from PygameWidgets.core.eventdispatcher.properties import Property

class BindException(Exception):
    pass

class EventDispatcher(object):

    def __init__(self):
        self.properties = {}
        self.property_values = {}
        self.callbacks = {}
        bindings = {}
        # Walk through the MRO looking for Property attributes in the classes. Then register and bind them to
        # 'on_<prop_name>' if it exists.
        for cls in self.__class__.__mro__:
            for prop_name, prop in cls.__dict__.iteritems():
                # prop = getattr(self, prop_name)
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
        for callback in self.callbacks[key]:
            if callback(*args):
                break

    def register_event(self, name, property, default_value):
        self.properties[name] = property
        self.property_values[name] = default_value
        self.callbacks[name] = []

    def bind(self, **kwargs):
        for prop, func in kwargs.iteritems():
            if prop not in self.properties:
                raise BindException("'{}' is not a registered property.")
            self.callbacks[prop].append(func)

    def setter(self, prop_name):
        p = self.properties[prop_name]
        return p.fset
