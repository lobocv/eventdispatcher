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

    def test_bind(self):
        """
        Bind and unbind a function to the properties in self.dispatcher
        """
        self._some_function_call_count = 0

        def _some_function(*args):
            self._some_function_call_count += 1

        for prop_name, info in self.dispatcher.event_dispatcher_properties.iteritems():
            # Bind
            self.dispatcher.bind(**{prop_name: _some_function})
            cc = self._some_function_call_count
            self.dispatcher.dispatch(prop_name, self.dispatcher, info['value'])
            self.assertEqual(cc+1, self._some_function_call_count)
            # Unbind
            self.dispatcher.unbind(**{prop_name: _some_function})
            cc = self._some_function_call_count
            self.dispatcher.dispatch(prop_name, self.dispatcher, info['value'])
            self.assertEqual(cc, self._some_function_call_count)
            # Bind many
            bind_count = 3
            for i in xrange(bind_count):
                self.dispatcher.bind(**{prop_name: _some_function})
            cc = self._some_function_call_count
            self.dispatcher.dispatch(prop_name, self.dispatcher, info['value'])
            self.assertEqual(cc+bind_count, self._some_function_call_count)
            # Unbind all
            self.dispatcher.unbind_all(prop_name)
            cc = self._some_function_call_count
            self.dispatcher.dispatch(prop_name, self.dispatcher, info['value'])
            self.assertEqual(cc, self._some_function_call_count)



