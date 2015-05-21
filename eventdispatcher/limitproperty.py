__author__ = 'calvin'

from . import Property

class LimitProperty(Property):

    def __init__(self, default_value, min, max):
        super(LimitProperty, self).__init__(default_value, min=min, max=max)

    def __get__(self, obj, objtype=None):
        return obj.event_dispatcher_properties[self.name]['value']

    def __set__(self, obj, value):
        info = obj.event_dispatcher_properties[self.name]
        if value != info['value']:
            # Clip the value to be within min/max
            if value <= info['min']:
                value = info['min']
            elif value >= info['max']:
                value = info['max']
            prop = obj.event_dispatcher_properties[self.name]
            prop['value'] = value
            for callback in prop['callbacks']:
                if callback(obj, value):
                    break

    def __delete__(self, obj):
        raise AttributeError("Cannot delete properties")

    @staticmethod
    def get_min(inst, name):
        return inst.event_dispatcher_properties[name]['min']

    @staticmethod
    def set_min(inst, name, value):
        inst.event_dispatcher_properties[name]['min'] = value
        setattr(inst, name, value)

    @staticmethod
    def get_max(inst, name):
        return inst.event_dispatcher_properties[name]['max']

    @staticmethod
    def set_max(inst, name, value):
        inst.event_dispatcher_properties[name]['max'] = value
        setattr(inst, name, value)
