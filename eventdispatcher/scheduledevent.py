__author__ = 'calvin'

__author__ = 'calvin'

from time import time
import threading
import weakref
from clock import Clock


class ScheduledEvent(object):
    """ Creates a trigger to the scheduler generator that is thread-safe."""
    objs = weakref.WeakValueDictionary({})
    RUNNING = 1
    KILL = 0

    def __init__(self, func, timeout=0):
        self.func = func
        self.t0 = time()
        self.timeout = timeout
        self.lock = threading.Lock()
        self._active = 1
        ScheduledEvent.clock = Clock.get_running_clock()

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
            self.clock.scheduled_funcs[self.next] += 1
            self.clock.queue.append(self.next)

    def kill(self):
        """
        Send a kill signal to the generator, kicking it out of it's while loop and closing the generator.
        We must catch the StopIteration exception so that the main loop does not fail.
        """

        def _kill():
            try:
                self.generator.send(ScheduledEvent.KILL)
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
        if not self.clock.scheduled_funcs[self.next]:
            self.clock.scheduled_funcs[self.next] += 1
            self.clock.queue.append(self.next)

    def reset_trigger(self, reschedule=False):
        if self.clock.scheduled_funcs[self.func]:
            self.clock.scheduled_funcs[self.func] -= 1
            self.clock.queue.remove(self.func)
        if reschedule:
            self.next()

    @property
    def is_scheduled(self):
        return bool(self.clock.scheduled_funcs[self.func])

    def __repr__(self):
        return "ScheduledEvent for {}{}".format(self.func, ' (scheduled)' if self.is_scheduled else '')

    def next(self, *args):
        try:
            with self.lock:
                self.generator.send(ScheduledEvent.RUNNING)
        except StopIteration:
            pass

    @staticmethod
    def unschedule_event(func):
        """
        Unschedule an event in the queue. Fails safely if the scheduled function is not in the queue.
        Be sure to use the same reference object if the scheduled function was a lambda or partial.
        :param func: scheduled function in the queue
        :return: True if the function was removed from the queue
        """
        clock = ScheduledEvent.clock
        if clock.scheduled_funcs[func]:
            clock.scheduled_funcs[func] -= 1
            clock.queue.remove(func)
            return True
        else:
            return False

    @staticmethod
    def schedule_once(func, timeout=0, start=True):
        """
        Schedule a function to be called `interval` seconds later.
        :param func: Scheduled Function
        :param interval: Time interval in seconds
        """
        if timeout:
            s = ScheduledEvent(func, timeout)
            s.generator = s._timeout_generator(func)
            s.generator.next()
            s.start() if start else s.stop()
            return s
        else:
            ScheduledEvent.clock.scheduled_funcs[func] += 1
            ScheduledEvent.clock.queue.append(func)

    @staticmethod
    def create_trigger(func):
        """
        Create a trigger that schedules a function to be called on the next cycle of the main loop.
        Calling the trigger more than once will not schedule the function multiple times.
        :param func: Scheduled Function
        """
        s = ScheduledEvent(func, timeout=0)
        s.generator = s._trigger_generator(func)
        s.generator.next()
        return s

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
        s.generator.next()
        s.start() if start else s.stop()
        ScheduledEvent.objs[id(s)] = s
        return s

    """
    Generators for the different types of ScheduledEvents
    """

    def _interval_generator(self, f):
        """
        Generator. The function f is called every `timeout` number of seconds.
        """
        interval = self.timeout
        scheduled_funcs = self.clock.scheduled_funcs
        append = self.clock.queue.append
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
            if not scheduled_funcs[_next]:
                scheduled_funcs[_next] += 1
                append(_next)
            running = yield
        # When the loop breaks, we still have one scheduled call to the generator.
        yield

    def _timeout_generator(self, f):
        """
        Generator. The function f is called after `timeout` number of seconds
        """
        timeout = self.timeout
        scheduled_funcs = self.clock.scheduled_funcs
        append = self.clock.queue.append
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
                if not scheduled_funcs[_next]:
                    scheduled_funcs[_next] += 1
                    append(_next)
                running = yield
        # When the loop breaks, we still have one scheduled call to the generator.
        yield

    def _trigger_generator(self, f):
        """
        Generator. The function f is called on the next Clock cycle. A function can be scheduled at most once per
        clock cycle.
        """
        scheduled_funcs = self.clock.scheduled_funcs
        append = self.clock.queue.append
        running = yield
        while running:
            if not scheduled_funcs[f] and self._active:
                scheduled_funcs[f] += 1
                append(f)
                running = yield
            else:
                running = yield