__author__ = 'calvin'

__author__ = 'calvin'

from time import time
import threading
from functools import partial

RUNNING = 1
KILL = 0

import weakref
from clock import Clock


class ScheduledEvent(object):

    """ Creates a trigger to the scheduler generator that is thread-safe."""
    objs = weakref.WeakValueDictionary({})

    def __init__(self, func, timeout=0):
        self.func = func
        self.t0 = time()
        self.timeout = timeout
        self.lock = threading.Lock()
        self._active = 1
        self.clock = Clock.get_running_clock()

    def __iter__(self):
        return self

    def stop(self):
        """
        Stops the scheduled event from being called.
        """
        self._active = 0

    def start(self):
        """
        Allows the scheduled event from being called again.
        """
        self._active = 1
        self.t0 = time()
        if self.next not in self.clock.scheduled_funcs:
            self.clock.scheduled_funcs.add(self.next)
            self.clock.scheduled_events.append(self.next)

    def kill(self):
        """
        Send a kill signal to the generator, kicking it out of it's while loop and closing the generator.
        We must catch the StopIteration exception so that the main loop does not fail.
        """

        def _kill():
            try:
                self.generator.send(KILL)
            except StopIteration:
                pass
        # We need to schedule the kill, in case it is being called from within the function/generator
        self.clock.schedule_event(_kill)

    def reset_timer(self):
        """
        Reset the time reference, delaying any scheduled events (schedule_once, schedule_interval).
        """
        self.t0 = time()

        # schedule the call to the generator, ensuring only one function is added to the queue
        if self.next not in self.clock.scheduled_funcs:
            self.clock.scheduled_funcs.add(self.next)
            self.clock.scheduled_events.append(self.next)

    def __repr__(self):
        return "ScheduledEvent for {}".format(self.func)

    def next(self, *args):
        with self.lock:
            try:
                self.call_generator()
            except StopIteration:
                pass

    @staticmethod
    def schedule_once(func, timeout=0, start=True):
        """
        Schedule a function to be called `interval` seconds later.
        :param func: Scheduled Function
        :param interval: Time interval in seconds
        """
        s = ScheduledEvent(func, timeout)
        s.generator = s._timeout_generator(func)
        s.call_generator = partial(s.generator.send, RUNNING)
        s.generator.next()
        s.start() if start else s.stop()
        return s

    @staticmethod
    def create_trigger(func):
        """
        Create a trigger that schedules a function to be called on the next cycle of the main loop.
        Calling the trigger more than once will not schedule the function multiple times.
        :param func: Scheduled Function
        """
        s = ScheduledEvent(func, timeout=0)
        # s.generator = s._trigger_generator(func).next
        s.generator = s._trigger_generator(func)
        s.call_generator = partial(s.generator.send, RUNNING)
        s.generator.next()
        return s.next

    @staticmethod
    def schedule_interval(func, interval, start=False):
        """
        Schedule a function to be called every `interval` seconds. Must call start() to activate.
        :param func: Scheduled Function
        :param start: start right away.
        :param interval: Time interval in seconds
        """
        s = ScheduledEvent(func, timeout=interval)
        s.generator = s._interval_generator(func)
        s.call_generator = partial(s.generator.send, RUNNING)
        s.generator.next()
        s.start() if start else s.stop()
        ScheduledEvent.objs[id(s)] = s
        return s

    def _interval_generator(self, f):
        interval = self.timeout
        scheduled_funcs = self.clock.scheduled_funcs
        add = scheduled_funcs.add
        append = self.clock.scheduled_events.append
        _next = self.next
        running = yield
        while running:
            t = time()
            dt = t - self.t0
            if dt > interval and self._active:
                # If we have past the timeout time, call the function, reset the reference time (t0)
                f()
                self.t0 = t
            # Add another call to this generator to the scheduled functions
            if _next not in scheduled_funcs:
                add(_next)
                append(_next)
            running = yield
        # When the loop breaks, we still have one scheduled call to the generator.
        yield

    def _timeout_generator(self, f):
        timeout = self.timeout
        scheduled_funcs = self.clock.scheduled_funcs
        add = scheduled_funcs.add
        append = self.clock.scheduled_events.append
        _next = self.next
        running = yield
        while running:
            dt = time() - self.t0
            if dt > timeout and self._active:
                # If we have pasted the timeout time, call the function
                f()
                running = yield
            else:
                # Add another call to this generator to the scheduled functions
                if _next not in scheduled_funcs:
                    add(_next)
                    append(_next)
                running = yield
        # When the loop breaks, we still have one scheduled call to the generator.
        yield

    def _trigger_generator(self, f):
        scheduled_funcs = self.clock.scheduled_funcs
        add = scheduled_funcs.add
        append = self.clock.scheduled_events.append
        running = yield
        while running:
            if f not in scheduled_funcs and self._active:
                add(f)
                append(f)
                running = yield
            else:
                running = yield


