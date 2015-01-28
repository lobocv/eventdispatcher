__author__ = 'Calvin'

import unittest
import logging
import random

# logging.getLogger().setLevel('INFO')
from eventdispatcher import BindError, Property, ListProperty
from eventdispatcher.listproperty import ObservableList
from eventdispatcher.dictproperty import ObservableDict

"""
All tests are assuming the event dispatcher instance is stored in self.dispatcher or self.dispatcher2
And all properties are named p1 or p2.
"""



def create_different_value(value):
    if isinstance(value, float):
        different_value = random.random()
    elif isinstance(value, int):
        different_value = random.randint(0, 1000)
    elif isinstance(value, list) or isinstance(value, ObservableList):
        different_value = [random.randint(0, 1000) for i in xrange(10)]
    elif isinstance(value, dict) or isinstance(value, ObservableDict):
        different_value = {str(i): random.randint(0, 1000) for i in xrange(10)}
    while different_value == value:
        return create_different_value(value)
    else:
        return different_value

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

    def test_property_individuality(self):
        """
        Check that if you change the value of a property in one instance of EventDispatcher, that it does not change
        across all instances of that class.
        """
        d1 = self.dispatcher
        d2 = self.dispatcher2
        d1_p1 = getattr(d1, 'p1')
        d2_p1 = getattr(d2, 'p1')
        # Create new values for each dispatcher.p1
        new_d1_p1 = create_different_value(d1_p1)
        while new_d1_p1 == d2_p1:                           # Make sure it is different from d2.p1
            new_d1_p1 = create_different_value(d1_p1)
        # Set d1.p1 to the new value and check that d2.p1 did not change
        setattr(d1, 'p1', new_d1_p1)
        self.assertNotEqual(d1.p1, d2.p1)

    def test_set_property_value(self):
        """
        Test setting the value of the property to a different value and ensure that the callback is called.
        """
        dispatcher = self.dispatcher
        for prop_name, info in dispatcher.event_dispatcher_properties.iteritems():
            value = info['value']
            different_value = create_different_value(value)
            dc = self.dispatch_count
            self.assertNotEqual(value, different_value)
            setattr(dispatcher, info['name'], different_value)
            info = dispatcher.event_dispatcher_properties[prop_name]  # May need to get the updated reference to info.
            self.assertEqual(dc + 1, self.dispatch_count)
            self.assertEqual(info['value'], different_value)

    def test_bind_none_existent_property(self):
        """
        Checks to make sure calling bind on a property that does not exist will raise a BindError
        """
        self.assertRaises(BindError, self.dispatcher.bind, some_property_that_doesnt_exist=self.assert_callback)

    def test_unbind_none_existent_property(self):
        """
        Checks to make sure calling unbind on a property that does not exist will raise a BindError
        """
        self.assertRaises(BindError, self.dispatcher.unbind, some_property_that_doesnt_exist=self.assert_callback)

    def test_unbind_all_none_existent_property(self):
        """
        Checks to make sure calling unbind_all on a property that does not exist will raise a BindError
        """
        self.assertRaises(BindError, self.dispatcher.unbind_all, 'some_property_that_doesnt_exist')

    def test_bind(self):
        """
        Bind and unbind and unbind_all functions to the properties in self.dispatcher.
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

    def test_binding_properties_together(self):
        """
        Test EventDispatcher.setter() ensuring that properties are bound together and therefore share the same value and
        also that the callback both properties are executed when the value changes.

        """
        expected_dispatches = 10
        self.dispatcher.bind(p1=self.dispatcher2.setter('p1'))
        if self.assert_callback not in self.dispatcher2.event_dispatcher_properties['p1']['callbacks']:
            self.dispatcher2.bind(p1=self.assert_callback)
        for i in xrange(expected_dispatches/2):
            self.dispatcher.p1 = create_different_value(self.dispatcher.p1)
            self.assertEqual(self.dispatcher.p1, self.dispatcher2.p1)
        self.assertEqual(self.dispatch_count, expected_dispatches)
        self.dispatcher2.unbind(p1=self.assert_callback)

    def test_get_property(self):
        """
        Test the ability to get the property instance for a particular instance of EventDispatcher.
        Check that the Property instance is the same for each instance of EventDispatcher for a particular property
        attribute.
        """
        d1_p = self.dispatcher.get_dispatcher_property('p1')
        self.assertTrue(isinstance(d1_p, Property))
        d1_p2 = self.dispatcher.get_dispatcher_property('p2')
        self.assertTrue(isinstance(d1_p2, Property))

        d2_p = self.dispatcher.get_dispatcher_property('p1')
        self.assertTrue(isinstance(d2_p, Property))
        d2_p2 = self.dispatcher.get_dispatcher_property('p2')
        self.assertTrue(isinstance(d2_p2, Property))

        self.assertIs(d1_p, d2_p)
        self.assertIs(d1_p2, d2_p2)
        self.assertIsNot(d1_p, d1_p2)
        self.assertIsNot(d2_p, d2_p2)
