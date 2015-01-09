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

    # def assertEqual(self, first, second, dispatch_count, msg=None):
    #     super(EventDispatcherTest, self).assertEqual(first, second, msg)
    #     super(EventDispatcherTest, self).assertEqual(self.dispatch_count, dispatch_count, msg)
