__author__ = 'Calvin Lobo'
__version__ = '1.63'

from .property import Property
from .dictproperty import DictProperty
from .listproperty import ListProperty
from .unitproperty import UnitProperty


class BindError(Exception):
    pass


class EventDispatcher(object):
    def __init__(self, **kwargs):
        self.event_dispatcher_event_callbacks = {}
        bindings = {}
        # Walk backwards through the MRO looking for Property attributes in the classes. Then register and bind them to
        # 'on_<prop_name>' if it exists. Walking backwards allows you to override the default value for a superclass.
        for cls in reversed(self.__class__.__mro__):
            for prop_name, prop in cls.__dict__.iteritems():
                if isinstance(prop, Property):
                    prop.name = prop_name
                    prop.register(self, prop_name, prop.default_value)
                    if hasattr(self, 'on_{}'.format(prop_name)):
                        func = getattr(self, 'on_{}'.format(prop_name))
                        bindings.update({prop_name: func})

        self.bind(**bindings)

    def dispatch(self, key, *args):
        for callback in self.event_dispatcher_properties[key]['callbacks']:
            if callback(*args):
                break

    def dispatch_event(self, event, *args):
        for callback in self.event_dispatcher_event_callbacks[event]:
            if callback(*args):
                break

    def register_event(self, name):
        if hasattr(self, 'on_{}'.format(name)):
            self.event_dispatcher_event_callbacks[name] = [getattr(self, 'on_{}'.format(name))]
        else:
            self.event_dispatcher_event_callbacks[name] = []

    def unbind(self, **kwargs):
        all_properties = self.event_dispatcher_properties
        for prop_name, callback in kwargs.iteritems():
            if prop_name in all_properties:
                try:
                    all_properties[prop_name]['callbacks'].remove(callback)
                except ValueError:
                    raise BindError("No binding for {} in property '{}'".format(callback.__name__, prop_name))
            elif prop_name in self.event_dispatcher_event_callbacks:
                try:
                    self.event_dispatcher_event_callbacks[prop_name].remove(callback)
                except ValueError:
                    raise BindError("No binding for {} in event '{}'".format(callback.__name__, prop_name))
            else:
                raise BindError('No property or event by the name of %s' % prop_name)

    def unbind_all(self, *args):
        all_properties = self.event_dispatcher_properties
        for prop_name in args:
            if prop_name in all_properties:
                del all_properties[prop_name]['callbacks'][:]
            elif prop_name in self.event_dispatcher_event_callbacks:
                del self.event_dispatcher_event_callbacks[prop_name][:]
            else:
                raise BindError("No such property or event '%s'" % prop_name)

    def bind(self, **kwargs):
        for prop_name, callback in kwargs.iteritems():
            if prop_name in self.event_dispatcher_properties:
                # Queue the callback into the property
                self.event_dispatcher_properties[prop_name]['callbacks'].append(callback)
            elif prop_name in self.event_dispatcher_event_callbacks:
                # If a property was not found, search in events
                self.event_dispatcher_event_callbacks[prop_name].append(callback)
            else:
                raise BindError("No property or event by the name of '%s'" % prop_name)

    def setter(self, prop_name):
        return lambda inst, value: setattr(self, prop_name, value)

    def get_dispatcher_property(self, prop_name):
        return self.event_dispatcher_properties[prop_name]['property']

