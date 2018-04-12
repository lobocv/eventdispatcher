__author__ = 'Calvin'

import unittest
import time

from eventdispatcher import EventDispatcher
from eventdispatcher import ScheduledEvent, Clock
from eventdispatcher.dictproperty import Property

MAX_TIME_S = 3


class App(Clock):

    def __init__(self):
        super(App, self).__init__()
        self.loop_counter = 0

    def _run_scheduled_events(self):
        super(App, self)._run_scheduled_events()
        if (time.time() - self.start_time) > MAX_TIME_S:
            self._running = False
        self.loop_counter += 1

    def run(self):
        self.start_time = time.time()
        super(App, self).run()


class Dispatcher(EventDispatcher):
    p1 = Property(0)
    p2 = Property(1)

    def __init__(self):
        super(Dispatcher, self).__init__()
        self.start_time = None
        self.last_increase_count_call = None
        self.counter = 0

    def increase_count(self):
        self.counter += 1
        self.last_increase_count_call = time.time()

    def reset_count(self):
        self.counter = 0


class EventTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(EventTest, self).__init__(*args, **kwargs)
        self.app = App()
        self.d = Dispatcher()

    def increase_count(self):
        self.d.counter += 1

    def tearDown(self):
        self.d.reset_count()

    def test_trigger(self):
        self.assertEqual(self.d.counter, 0)

        scheduler = ScheduledEvent.create_trigger(self.d.increase_count)
        trigger = scheduler.next
        self.assertFalse(scheduler.is_scheduled)
        trigger()
        self.assertTrue(scheduler.is_scheduled)
        for i in range(10):
            # These will not execute the callback since it's already been scheduled
            trigger()
        self.app.run()
        # Counter should still only increment by 1
        self.assertEqual(self.d.counter, 1)

    def test_schedule_once_delay(self):
        self.assertEqual(self.d.counter, 0)
        timeout_s = 2
        scheduler = ScheduledEvent.schedule_once(self.d.increase_count, timeout_s)
        self.assertTrue(scheduler.is_scheduled)
        self.app.run()
        # Counter should still only increment by 1
        self.assertEqual(self.d.counter, 1)
        self.assertAlmostEqual(self.d.last_increase_count_call - self.app.start_time, timeout_s, delta=0.2)

    def test_schedule_once_immediate(self):
        self.assertEqual(self.d.counter, 0)
        scheduler = ScheduledEvent.schedule_once(self.d.increase_count)
        self.assertTrue(scheduler.is_scheduled)
        self.app.run()
        # Counter should still only increment by 1
        self.assertEqual(self.d.counter, 1)

    def test_schedule_interval(self):
        self.assertEqual(self.d.counter, 0)
        timeout_s = 0.9
        counter_expected = int(MAX_TIME_S / 0.9)
        scheduler = ScheduledEvent.schedule_interval(self.d.increase_count, timeout_s)
        self.assertFalse(scheduler.is_scheduled)
        scheduler.start()
        self.assertTrue(scheduler.is_scheduled)
        self.app.run()
        # Counter should still only increment by 1
        self.assertEqual(self.d.counter, counter_expected)


if __name__ == '__main__':
    unittest.main()