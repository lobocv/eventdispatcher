__author__ = 'calvin'

from copy import deepcopy


class Property(object):

    def __init__(self, default_value, **additionals):
        self.instances = {}
        self.default_value = default_value
        self.value = deepcopy(default_value)
        self._additionals = additionals

    def __get__(self, obj, objtype=None):
        return obj.event_dispatcher_properties[self.name]['value']

    def __set__(self, obj, value):
        if value != obj.event_dispatcher_properties[self.name]['value']:
            prop = obj.event_dispatcher_properties[self.name]
            prop['value'] = value
            for callback in prop['callbacks']:
                if callback(obj, value):
                    break

    def __delete__(self, obj):
        raise AttributeError("Cannot delete properties")

    def register(self, instance, property_name, default_value):
        info = self._additionals.copy()
        info.update({'property': self, 'value': default_value, 'name': property_name, 'callbacks': []})
        # Create the instances dictionary at registration so that each class has it's own instance of it.
        self.instances[instance] = info
        instance.event_dispatcher_properties[property_name] = info

    def get_dispatcher_property(self, property_name):
        return self.instances[self][property_name]


