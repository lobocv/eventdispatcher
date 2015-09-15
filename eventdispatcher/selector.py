__author__ = 'calvin'

from eventdispatcher import EventDispatcher, Property
from collections import deque, OrderedDict
from itertools import izip_longest


class Selector(EventDispatcher):
    current_set = Property('Default')

    def __init__(self, options=[], keys=[], name='default', wrap=True, **kwargs):
        super(Selector, self).__init__(**kwargs)
        self.wrap = wrap
        self.current_set = name
        self.option_sets = {}
        self.set_options(options, keys=keys, name=name)
        self.register_event('value')
        self.register_event('index')
        self.register_event('key')
        self.bind(current_set=self.dispatch_selection_change)

    def set_options(self, options, keys=[], name='default'):
        options = deque([o for o in izip_longest(options, keys, xrange(len(options)), fillvalue='')])
        self.option_sets[name] = options
        if 'default' in self.option_sets and len(self.option_sets['default']) == 0:
            del self.option_sets['default']
        if self.current_set == 'default':
            self.current_set = name

    def __iter__(self):
        return iter(self.option_sets[self.current_set])

    def __len__(self):
        return len(self.option_sets[self.current_set])

    def __copy__(self):
        s = Selector(wrap=self.wrap)
        for name, optset in self.option_sets.iteritems():
            options, keys, index = zip(*sorted(optset, key=lambda x: x[2]))
            s.set_options(options, keys, name)
        s.current_set = self.current_set
        return s

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
        if name is None:
            name = self.current_set
        keys = sorted(list(self.option_sets[name]), key=lambda x: x[2])
        return [k for v, k, i in keys]

    def values(self, name=None):
        if name is None:
            name = self.current_set
        values = sorted(list(self.option_sets[name]), key=lambda x: x[2])
        return [v for v, k, i in values]

    def dispatch_selection_change(self, *args):
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
        s = OrderedDict()
        option_set_names = self.option_sets.keys()
        option_set_names.remove(self.current_set)
        option_set_names.insert(0, self.current_set)
        for name in option_set_names:
            optset = self.option_sets[name]
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
