from . import Property
from .exceptions import InvalidOptionError


class OptionProperty(Property):

    def __init__(self, default_value, options, handler=None):
        super(OptionProperty, self).__init__(default_value, options=options, handler=None)
        self.handler = handler
        self.options = set(options) if options else set()
        if default_value not in self.options:
            raise ValueError('Default value must be one of the defined options.')

    def __set__(self, obj, value):
        if value in self.options:
            super(OptionProperty, self).__set__(obj, value)
        elif self.handler:
            self.handler(obj, value)
        else:
            raise InvalidOptionError(value, self.options)

    @staticmethod
    def set_options(inst, name, options):
        inst.event_dispatcher_properties[name]['options'].options = set(options)

    @staticmethod
    def set_handler(inst, name, handler):
        inst.event_dispatcher_properties[name]['handler'].handler = handler