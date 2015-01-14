__author__ = 'Calvin'

import unittest
import logging
import random

# logging.getLogger().setLevel('INFO')
from eventdispatcher.listproperty import ObservableList
from eventdispatcher.dictproperty import ObservableDict


class EventDispatcherTest(unittest.TestCase):
    def __init__(self, *args):
        super(EventDispatcherTest, self).__init__(*args)
        self.dispatch_count = 0


    def setUp(self):
        self.dispatch_count = 0

    def tearDown(self):
        self.dispatch_count = 0

    def assert_callback(self, inst, value):
        self.dispatch_count += 1
        logging.info('{testclass}: dispatching value {value}'.format(testclass=self.__class__.__name__,
                                                                     value=value))

    def _create_different_value(self, value):
        if isinstance(value, float):
            different_value = random.random()
        elif isinstance(value, int):
            different_value = random.randint(0, 1000)
        elif isinstance(value, list) or isinstance(value, ObservableList):
            different_value = [random.randint(0, 1000) for i in xrange(10)]
        elif isinstance(value, dict) or isinstance(value, ObservableDict):
            different_value = {str(i): random.randint(0, 1000) for i in xrange(10)}
        while different_value == value:
            return self._create_different_value(value)
        else:
            return different_value

    def test_set_property_value(self):
        dispatcher = self.dispatcher
        for prop_name, info in dispatcher.event_dispatcher_properties.iteritems():
            value = info['value']
            different_value = self._create_different_value(value)
            dc = self.dispatch_count
            self.assertNotEqual(value, different_value)
            setattr(dispatcher, info['name'], different_value)
            info = dispatcher.event_dispatcher_properties[prop_name]  # May need to get the updated reference to info.
            self.assertEqual(dc + 1, self.dispatch_count)
            self.assertEqual(info['value'], different_value)

    def test_bind(self):
        """
        Bind and unbind a function to the properties in self.dispatcher
        """
        self._some_function_call_count = 0

        def _some_function(*args):
            self._some_function_call_count += 1

        dispatcher = self.dispatcher
        for prop_name, info in dispatcher.event_dispatcher_properties.iteritems():
            # Bind
            dispatcher.bind(**{prop_name: _some_function})
            cc = self._some_function_call_count
            dispatcher.dispatch(prop_name, dispatcher, info['value'])
            self.assertEqual(cc + 1, self._some_function_call_count)
            # Unbind
            dispatcher.unbind(**{prop_name: _some_function})
            cc = self._some_function_call_count
            dispatcher.dispatch(prop_name, dispatcher, info['value'])
            self.assertEqual(cc, self._some_function_call_count)
            # Bind many
            bind_count = 3
            for i in xrange(bind_count):
                dispatcher.bind(**{prop_name: _some_function})
            cc = self._some_function_call_count
            dispatcher.dispatch(prop_name, dispatcher, info['value'])
            self.assertEqual(cc + bind_count, self._some_function_call_count)
            # Unbind all
            dispatcher.unbind_all(prop_name)
            cc = self._some_function_call_count
            dispatcher.dispatch(prop_name, dispatcher, info['value'])
            self.assertEqual(cc, self._some_function_call_count)



