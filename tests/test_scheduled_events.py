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
        self.start_time = 0
        self.loop_counter = 0
        self.loop_hooks = []

    def _run_scheduled_events(self):

        # Execute any hooks we add at certain points in the main loop
        for hook_config in self.loop_hooks[:]:
            if 'exec_index' in hook_config and self.loop_counter == hook_config['exec_index']:
                hook_config['hook'](*hook_config.get('args', []))
                self.loop_hooks.remove(hook_config)
            elif 'timeout_s' in hook_config and (time.time()-self.start_time) > hook_config['timeout_s']:
                hook_config['hook'](*hook_config.get('args', []))
                self.loop_hooks.remove(hook_config)

        super(App, self)._run_scheduled_events()
        if (time.time() - self.start_time) > MAX_TIME_S:
            self._running = False
        self.loop_counter += 1

    def run(self):
        self.start_time = time.time()
        super(App, self).run()


class Dispatcher(EventDispatcher):
    p1 = Property(0)

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

        def check(self, counter_expected):
            self.assertEqual(self.d.counter, counter_expected)

        # Check after the first loop that it incremented only once
        self.app.loop_hooks.append({'hook': check, 'exec_index': 1, 'args': [self, 1]})
        # Trigger multiple times before the next loop
        self.app.loop_hooks.append({'hook': trigger, 'exec_index': 2, 'args': [self]})
        self.app.loop_hooks.append({'hook': trigger, 'exec_index': 2, 'args': [self]})
        self.app.loop_hooks.append({'hook': trigger, 'exec_index': 2, 'args': [self]})
        # Check that it still only incremented by 1 even though it was triggered multiple times.
        self.app.loop_hooks.append({'hook': check, 'exec_index': 3, 'args': [self, 2]})
        # Trigger it once again
        self.app.loop_hooks.append({'hook': trigger, 'exec_index': 2, 'args': [self]})
        # Reset the trigger
        self.app.loop_hooks.append({'hook': scheduler.reset_trigger, 'exec_index': 2, 'args': [self]})
        # Check that the counter didn't change because we reset the trigger
        self.app.loop_hooks.append({'hook': check, 'exec_index': 3, 'args': [self, 2]})
        # Kill the scheduler
        self.app.loop_hooks.append({'hook': scheduler.kill, 'timeout_s': 0.5, 'args': []})

        self.app.run()

        # The underlying generator should have exited since we killed the scheduler
        with self.assertRaises(StopIteration):
            scheduler.generator.send(ScheduledEvent.RUNNING)
    #
    def test_schedule_once_delay(self):
        self.assertEqual(self.d.counter, 0)
        timeout_s = MAX_TIME_S-1
        scheduler = ScheduledEvent.schedule_once(self.d.increase_count, timeout_s)
        self.assertTrue(scheduler.is_scheduled)

        def check(self, timeout_s):
            # Counter should still only increment by 1
            self.assertEqual(self.d.counter, 1)
            self.assertAlmostEqual(self.d.last_increase_count_call - self.app.start_time, timeout_s, delta=0.1)

        # Check after the timeout that the counter has gone up
        self.app.loop_hooks.append({'hook': check, 'timeout_s': timeout_s+0.5, 'args': [self, timeout_s]})
        self.app.run()

    def test_schedule_once_immediate(self):
        self.assertEqual(self.d.counter, 0)
        scheduler = ScheduledEvent.schedule_once(self.d.increase_count)
        self.assertTrue(scheduler.is_scheduled)

        def check(self):
            # Counter should still only increment by 1
            self.assertEqual(self.d.counter, 1)

        # Check after the first loop that the counter has gone up
        self.app.loop_hooks.append({'hook': check, 'exec_index': 1, 'args': [self]})
        self.app.run()

    def test_schedule_interval(self):
        self.assertEqual(self.d.counter, 0)
        timeout_s = MAX_TIME_S / 10.
        n_dispatches = int(MAX_TIME_S / timeout_s)
        self.assertGreaterEqual(n_dispatches, 3)
        scheduler = ScheduledEvent.schedule_interval(self.d.increase_count, timeout_s)
        self.assertFalse(scheduler.is_scheduled)
        scheduler.start()
        self.assertTrue(scheduler.is_scheduled)

        def check(self, counter_expected):
            self.assertEqual(self.d.counter, counter_expected)

        N_stop = n_dispatches - 5  # Stop after this many dispatches
        self.assertGreater(N_stop, 0)
        # Schedule checks to happen just after the call is expected to execute
        for ii in range(1, N_stop):
            self.app.loop_hooks.append({'hook': check, 'timeout_s': ii*timeout_s+0.1, 'args': [self, ii]})

        # At this point, we should have N_stop-1 dispatches and expected counter = N_stop-1
        # Stop the scheduler and check that it's still at N_stop-1
        self.app.loop_hooks.append({'hook': scheduler.stop, 'timeout_s': (N_stop-1)*timeout_s+0.1, 'args': []})
        self.app.loop_hooks.append({'hook': check, 'timeout_s': N_stop*timeout_s+0.1, 'args': [self, N_stop-1]})

        # Kill the scheduler
        self.app.loop_hooks.append({'hook': scheduler.kill, 'timeout_s': N_stop*timeout_s+0.1, 'args': []})

        self.app.run()

        # The underlying generator should have exited since we killed the scheduler
        with self.assertRaises(StopIteration):
            next(scheduler.generator)


if __name__ == '__main__':
    unittest.main()