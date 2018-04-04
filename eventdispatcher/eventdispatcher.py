__author__ = 'calvin'

import contextlib
from future.utils import iteritems
from .property import Property
from .exceptions import *


class EventDispatcher(object):
    def __init__(self, *args, **kwargs):
        self.event_dispatcher_event_callbacks = {}
        self.event_dispatcher_properties = {}
        bindings = EventDispatcher.register_properties(self)
        self.bind(**bindings)

    @staticmethod
    def register_properties(obj, properties=None):
        """
        Walk backwards through the MRO looking for event dispatcher Property attributes in the classes.
        Then register and bind them to the default handler 'on_<prop_name>' if it exists.
        Walking backwards allows you to override the default value for a superclass.

        If the 'properties' argument is given, then only register the properties in the dictionary
        'properties' must be a dictionary of keys being the attribute name and values being the eventdispatcher
        Property object.
        """
        bindings = {}
        if properties is None:
            for cls in reversed(obj.__class__.__mro__):
                for prop_name, prop in iteritems(cls.__dict__):
                    if isinstance(prop, Property):
                        prop.name = prop_name
                        prop.register(obj, prop_name, prop.default_value)
                        if hasattr(obj, 'on_%s' % prop_name):
                            bindings[prop_name] = getattr(obj, 'on_{}'.format(prop_name))
        else:
            for prop_name, prop in iteritems(properties):
                prop.name = prop_name
                prop.register(obj, prop_name, prop.default_value)
                if hasattr(obj, 'on_%s' % prop_name):
                    bindings[prop_name] = getattr(obj, 'on_{}'.format(prop_name))

        return bindings

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
        """
        Dispatch a property. This calls all functions bound to the property.
        :param event: property name
        :param args: arguments to provide to the bindings
        :param kwargs: keyword arguments to provide to the bindings
        """
        for callback in self.event_dispatcher_properties[key]['callbacks']:
            if callback(*args, **kwargs):
                break

    def dispatch_event(self, event, *args, **kwargs):
        """
        Dispatch an event. This calls all functions bound to the event.
        :param event: event name
        :param args: arguments to provide to the bindings
        :param kwargs: keyword arguments to provide to the bindings
        """
        for callback in self.event_dispatcher_event_callbacks[event]:
            if callback(*args, **kwargs):
                break

    def register_event(self, *event_names):
        """
        Create an event that can be bound to and dispatched.
        :param event_names: Name of the event
        """
        for event_name in event_names:
            default_dispatcher = getattr(self, 'on_{}'.format(event_name), None)
            if default_dispatcher:
                self.event_dispatcher_event_callbacks[event_name] = [default_dispatcher]
            else:
                self.event_dispatcher_event_callbacks[event_name] = []

    def unbind(self, **kwargs):
        """
        Unbind the specified callbacks associated with the property / event names
        :param kwargs: {property name: callback} bindings
        """
        all_properties = self.event_dispatcher_properties
        for prop_name, callback in iteritems(kwargs):
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
        """
        Unbind all callbacks associated with the specified property / event names
        :param args: property / event names
        """
        all_properties = self.event_dispatcher_properties
        for prop_name in args:
            if prop_name in all_properties:
                del all_properties[prop_name]['callbacks'][:]
            elif prop_name in self.event_dispatcher_event_callbacks:
                del self.event_dispatcher_event_callbacks[prop_name][:]
            else:
                raise BindError("No such property or event '%s'" % prop_name)

    def bind(self, **kwargs):
        """
        Bind a function to a property or event.
        :param kwargs: {property name: callback} bindings
        """
        for prop_name, callback in iteritems(kwargs):
            if prop_name in self.event_dispatcher_properties:
                # Queue the callback into the property
                self.event_dispatcher_properties[prop_name]['callbacks'].append(callback)
            elif prop_name in self.event_dispatcher_event_callbacks:
                # If a property was not found, search in events
                self.event_dispatcher_event_callbacks[prop_name].append(callback)
            else:
                raise BindError("No property or event by the name of '%s'" % prop_name)

    def bind_once(self, **kwargs):
        """
        Bind a function to a property or event and unbind it after the first time the function has been called
        :param kwargs: {property name: callback} bindings
        """
        for prop_name, callback in iteritems(kwargs.copy()):
            def _wrapped_binding(*args):
                callback()
                self.unbind(**{prop_name: _wrapped_binding})

            self.bind(**{prop_name: _wrapped_binding})
            kwargs.pop(prop_name)
            if kwargs:
                self.bind_once(**kwargs)
                return

    def setter(self, prop_name):
        return lambda inst, value: setattr(self, prop_name, value)

    def get_dispatcher_property(self, prop_name):
        return self.event_dispatcher_properties[prop_name]['property']

    @contextlib.contextmanager
    def temp_unbind(self, **bindings):
        """
        Context manager to temporarily suspend dispatching of a specified callback.
        :param bindings: keyword argument of property_name=callback_func
        """
        # Enter / With
        all_properties = self.event_dispatcher_properties
        callbacks = {}
        for prop_name, binding in iteritems(bindings):
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
        for prop_name, cb in iteritems(callbacks):
            if prop_name in all_properties:
                all_properties[prop_name]['callbacks'] = cb
            elif prop_name in self.event_dispatcher_event_callbacks:
                self.event_dispatcher_event_callbacks[prop_name] = callbacks[prop_name]

    @contextlib.contextmanager
    def temp_unbind_all(self, *prop_name):
        """
        Context manager to temporarily suspend dispatching of the listed properties or events. Assigning a different
        value to these properties or dispatching events inside the with statement will not dispatch the bindings.
        :param prop_name: property or event names to suspend
        """
        # Enter / With
        property_callbacks = {}
        event_callbacks = {}
        for name in prop_name:
            if name in self.event_dispatcher_properties:
                property_callbacks[name] = self.event_dispatcher_properties[name]['callbacks']
                self.event_dispatcher_properties[name]['callbacks'] = []
            if name in self.event_dispatcher_event_callbacks:
                event_callbacks[name] = self.event_dispatcher_event_callbacks[name]
                self.event_dispatcher_event_callbacks[name] = []
        # Inside of with statement
        yield None
        # Finally / Exit
        for name in prop_name:
            if name in property_callbacks:
                self.event_dispatcher_properties[name]['callbacks'] = property_callbacks[name]
            if name in event_callbacks:
                self.event_dispatcher_event_callbacks[name] = event_callbacks[name]
