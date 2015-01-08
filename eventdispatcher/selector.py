__author__ = 'calvin'

from . import EventDispatcher
from .dictproperty import DictProperty


class Selector(EventDispatcher):
    current = DictProperty({})

    def __init__(self, options=[], keys=[], wrap=True, **kwargs):
        super(Selector, self).__init__(**kwargs)
        self.wrap = wrap
        self.keys = []
        self.options = []
        self.register_event('value')
        self.register_event('index')
        self.register_event('key')
        self.set_options(options, keys)

    def set_options(self, options, keys=[]):
        self.options = options
        if keys:
            self.keys = keys
        else:
            self.keys = [str(opt) for opt in options]
        if options:
            self.current.update({'index': 0, 'value': self.options[0], 'key': self.keys[0]})
            # self.dispatch_event('index', self, self.index)

    @property
    def index(self):
        return self.current['index']

    @index.setter
    def index(self, i):
        self.current.update({'index': i, 'value': self.options[i], 'key': self.keys[i]})

    @property
    def value(self):
        return self.current['value']

    @value.setter
    def value(self, x):
        i = self.options.index(x)
        self.current.update({'index': i, 'value': x, 'key': self.keys[i]})

    @property
    def key(self):
        return self.current['key']

    @key.setter
    def key(self, x):
        i = self.keys.index(x)
        self.current.update({'index': i, 'value': self.options[i], 'key': x})

    def on_current(self, inst, current):
        self.dispatch_event('value', inst, current['value'])
        self.dispatch_event('index', inst, current['index'])
        self.dispatch_event('key', inst, current['key'])

    def next(self, *args):
        index = self.index + 1
        if index < len(self.options):
            self.index = index
        elif self.wrap:
            self.index = 0

    def prev(self, *args):
        index = self.index - 1
        if index >= 0:
            self.index = index
        elif self.wrap:
            self.index = len(self.options) - 1

    @property
    def json_repr(self):
        options = [obj.json_repr if hasattr(obj, 'json_repr') else obj for obj in self.options]
        return {'options': options, 'keys': self.keys, 'index': self.index}