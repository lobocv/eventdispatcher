

__all__ = ['EventDispatcherException', 'BindError', 'InvalidOptionError']


class EventDispatcherException(Exception):
    pass


class BindError(EventDispatcherException):
    pass


class InvalidOptionError(EventDispatcherException):
    def __init__(self, value, options):
        self.value = value
        self.options = options

    def __str__(self):
        return "'%s' is not one of the following allowed options: %s" % (self.value, [i for i in self.options])
