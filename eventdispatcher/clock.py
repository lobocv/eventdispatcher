__author__ = 'calvin'


from collections import deque, Counter


class Clock(object):

    clock = None

    def __init__(self, *args, **kwargs):
        self.scheduled_funcs = Counter()
        self.queue = deque([])
        self._running = 0
        Clock.clock = self
        super(Clock, self).__init__(*args, **kwargs)

    @staticmethod
    def get_running_clock():
        return Clock.clock

    def _run_scheduled_events(self):
        events = self.queue
        funcs = self.scheduled_funcs
        popleft = events.popleft
        for i in xrange(len(events)):
            f = popleft()
            funcs[f] -= 1
            f()

    def run(self):
        # Use all local variables to speed up the loop
        _run_scheduled_events = self._run_scheduled_events
        self._running = 1
        while self._running:
            _run_scheduled_events()
