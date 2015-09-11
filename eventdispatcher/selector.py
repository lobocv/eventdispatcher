__author__ = 'calvin'

from eventdispatcher import EventDispatcher
from collections import deque
from itertools import izip_longest


class Selector(EventDispatcher):
    # current = DictProperty({})

    def __init__(self, options=[], keys=[], wrap=True, **kwargs):
        super(Selector, self).__init__(**kwargs)
        self.wrap = wrap
        self.current_set = 'default'
        self.option_sets = {}
        self.set_options(options, keys)
        self.register_event('value')
        self.register_event('index')
        self.register_event('key')

    def set_options(self, options, keys=[], name='default'):
        options = deque([o for o in izip_longest(options, keys, xrange(len(options)), fillvalue='')])
        self.option_sets[name] = options
        self.options = options

    def __iter__(self):
        return iter(self.option_sets[self.current_set])
    @property
    def index(self):
        return self.option_sets[self.current_set][0][2]

    @index.setter
    def index(self, i):
        options = self.option_sets[self.current_set]
        for j, (value, key, index) in enumerate(options):
            if i == index and j:
                options.rotate(len(options) - j)
                self.dispatch_selection_change()
                return

    @property
    def value(self):
        return self.option_sets[self.current_set][0][0]

    @value.setter
    def value(self, x):
        options = self.option_sets[self.current_set]
        for j, (value, key, index) in enumerate(options):
            if x == value and j:
                options.rotate(len(options) - j)
                self.dispatch_selection_change()
                return

    @property
    def key(self):
        return self.option_sets[self.current_set][0][1]

    @key.setter
    def key(self, x):
        options = self.option_sets[self.current_set]
        for j, (value, key, index) in enumerate(options):
            if x == key and j:
                options.rotate(len(options) - j)
                self.dispatch_selection_change()
                return

    def keys(self, name=None):
        return [k for v, k, i in self.option_sets[self.current_set]]

    def values(self, name=None):
        return [v for v, k, i in self.option_sets[self.current_set]]

    def dispatch_selection_change(self):
        value, key, index = self.option_sets[self.current_set][0]
        self.dispatch_event('value', self, value)
        self.dispatch_event('index', self, index)
        self.dispatch_event('key', self, key)

    def next(self, *args):
        self.option_sets[self.current_set].rotate(-1)
        self.dispatch_selection_change()

    def prev(self, *args):
        self.option_sets[self.current_set].rotate(1)
        self.dispatch_selection_change()

    @property
    def json_repr(self):
        s = {}
        for name, optset in self.option_sets.iteritems():
            s[name] = [(v.json_repr if hasattr(v, 'json_repr') else v, key, index) for v, key, index in optset]
        return s


if __name__ == '__main__':
    def callback(asd, v):
        print v

    s = Selector(options=[10, 20, 30, 40, 50], keys=['calvin', 'chris', 'adam', 'steve', 'salma'])
    s.bind(key=callback)
    s.index = 2
    s.value=50
    s.key = 'calvin'
