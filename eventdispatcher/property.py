__author__ = 'calvin'

from copy import deepcopy
import os

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
IS_COMPILED = os.path.exists(os.path.join(MODULE_DIR, 'cpp', 'eventdispatcher.so'))

if IS_COMPILED:
    print 'Compiled version of EventDispatcher found.'
    from cpp import eventdispatcher as cED
    PropertyBase = cED.cProperty
else:
    PropertyBase = object


class Property(PropertyBase):

    def __init__(self, default_value, **additionals):
        super(Property, self).__init__(default_value)
        self.instances = {}
        self.default_value = default_value
        self._additionals = additionals

    if not IS_COMPILED:
        def __get__(self, obj, objtype=None):
            return obj.event_dispatcher_properties[self.name]['value']

        def __set__(self, obj, value):
            if value != obj.event_dispatcher_properties[self.name]['value']:
                prop = obj.event_dispatcher_properties[self.name]
                prop['value'] = value
                for callback in prop['callbacks']:
                    if callback(obj, value):
                        break

        def register(self, instance, property_name, default_value):
            info = self._additionals.copy()
            info.update({'property': self, 'value': default_value, 'name': property_name, 'callbacks': []})
            # Create the instances dictionary at registration so that each class has it's own instance of it.
            self.instances[instance] = info
            instance.event_dispatcher_properties[property_name] = info

    def __delete__(self, obj):
        raise AttributeError("Cannot delete properties")


    def get_dispatcher_property(self, property_name):
        return self.instances[self][property_name]


