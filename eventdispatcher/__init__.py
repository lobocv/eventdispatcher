__author__ = 'Calvin Lobo'
__version__ = '1.79'

from .property import Property
from .dictproperty import DictProperty
from .listproperty import ListProperty
from .unitproperty import UnitProperty
from .setproperty import SetProperty
from .limitproperty import LimitProperty
from .weakrefproperty import WeakRefProperty
from .stringproperty import StringProperty, _
from .scheduledevent import ScheduledEvent

import contextlib
from collections import defaultdict

class BindError(Exception):
    pass


class EventDispatcher(object):
    def __init__(self, *args, **kwargs):
        self.event_dispatcher_event_callbacks = {}
        self.event_dispatcher_properties = {}
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

    def force_dispatch(self, prop_name, value):
        """
        Assigns the value to the property and then dispatches the event, regardless of whether that value is the same
        as the previous value.
        :param prop_name: property name
        :param value: value to assign to the property
        """
        previous_value = getattr(self, prop_name)
        if previous_value == value:
            self.dispatch(prop_name, self, previous_value)
        else:
            setattr(self, prop_name, value)

    def dispatch(self, key, *args, **kwargs):
        for callback in self.event_dispatcher_properties[key]['callbacks']:
            if callback(*args, **kwargs):
                break

    def dispatch_event(self, event, *args, **kwargs):
        for callback in self.event_dispatcher_event_callbacks[event]:
            if callback(*args, **kwargs):
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

    @contextlib.contextmanager
    def temp_unbind(self, **bindings):
        # Enter / With
        all_properties = self.event_dispatcher_properties
        callbacks = {}
        for prop_name, binding in bindings.iteritems():
            if prop_name in all_properties:
                # Make a copy of the callback sequence so we can revert back
                callbacks[prop_name] = all_properties[prop_name]['callbacks'][:]
                # Remove the specified bindings
                if binding in all_properties[prop_name]['callbacks']:
                    all_properties[prop_name]['callbacks'].remove(binding)
            elif prop_name in self.event_dispatcher_event_callbacks:
                callbacks[prop_name] = self.event_dispatcher_event_callbacks[prop_name][:]
                self.event_dispatcher_event_callbacks[prop_name].remove(binding)
        # Inside of with statement
        yield None
        # Finally / Exit
        for prop_name, cb in callbacks.iteritems():
            if prop_name in all_properties:
                all_properties[prop_name]['callbacks'] = cb
            elif prop_name in self.event_dispatcher_event_callbacks:
                self.event_dispatcher_event_callbacks[prop_name] = callbacks[prop_name]
