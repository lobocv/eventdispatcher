__author__ = 'calvin'

from . import EventDispatcher
from properties import Property

class Selector(EventDispatcher):

    index = Property(None)
    value = Property(None)
    key = Property(None)

    def __init__(self, options, keys, **kwargs):
        super(Selector, self).__init__(**kwargs)
        self.options = options
        self.keys = keys
        self.index = 0

    def on_index(self, inst, index):
        self.key = self.keys[index]
        self.value = self.options[index]
        self.current = self.value

    def on_key(self, inst, key):
        self.index = self.keys.index(key)

    def on_value(self, inst, value):
        self.index = self.options.index(value)

    def next(self):
        index = self.index + 1
        if index < len(self.options):
            self.index = index

    def prev(self):
        index = self.index - 1
        if index > 0:
            self.index = index

