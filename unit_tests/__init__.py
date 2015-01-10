__author__ = 'Calvin'

import unittest
import logging


# logging.getLogger().setLevel('INFO')


class EventDispatcherTest(unittest.TestCase):

    def setUp(self):
        self.dispatch_count = 0

    def tearDown(self):
        self.dispatch_count = 0

    def assert_callback(self, inst, value):
        self.dispatch_count += 1
        logging.info('{testclass}: dispatching value {value}'.format(testclass=self.__class__.__name__,
                                                                     value=value))

    def set_property(self, ed, prop_name, values):
        if not isinstance(values, list):
            values = [values]
        for value in values:
            dc = self.dispatch_count
            before_value = getattr(ed, prop_name)
            expected_dc = dc + int(before_value != value)
            setattr(ed, prop_name, value)
            after_value = getattr(ed, prop_name)
            self.assertEqual(after_value, value)
            self.assertEqual(self.dispatch_count, expected_dc)

