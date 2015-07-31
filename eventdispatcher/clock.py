__author__ = 'calvin'


from collections import deque, Counter


class Clock(object):

    clock = None

    def __init__(self, *args, **kwargs):
        self.scheduled_funcs = set()
        self.scheduled_events = deque([])
        Clock.clock = self
        super(Clock, self).__init__(*args, **kwargs)

    @staticmethod
    def get_running_clock():
        return Clock.clock

    def _run_scheduled_events(self):
        events = self.scheduled_events
        funcs = self.scheduled_funcs
        popleft = events.popleft
        remove = funcs.remove
        for i in xrange(len(events)):
            f = popleft()
            remove(f)
            f()

    def run(self):
        # Use all local variables to speed up the loop
        _run_scheduled_events = self._run_scheduled_events
        while self._running:
            _run_scheduled_events()
