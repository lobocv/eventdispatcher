__author__ = 'Calvin'

import logging
import pickle
import random
import unittest

# logging.getLogger().setLevel('INFO')
from eventdispatcher import BindError, Property


"""
All tests are assuming the event dispatcher instance is stored in self.dispatcher or self.dispatcher2
And all properties are named p1 or p2.
"""



class EventDispatcherTest(unittest.TestCase):
    def __init__(self, *args):
        super(EventDispatcherTest, self).__init__(*args)
        self.assert_callback_count = 0
        self.blocking_callback_count = 0

    def create_different_value(self, value):
        if isinstance(value, float):
            different_value = random.random()
        elif isinstance(value, int):
            different_value = random.randint(0, 1000)
        while different_value == value:
            return self.create_different_value(value)
        else:
            return different_value

    def setUp(self):
        self.assert_callback_count = 0
        self.blocking_callback_count = 0

    def tearDown(self):
        self.assert_callback_count = 0
        self.blocking_callback_count = 0

    def assert_callback(self, inst, value):
        self.assert_callback_count += 1
        logging.info('{testclass}: dispatching value {value}'.format(testclass=self.__class__.__name__,
                                                                     value=value))

    def blocking_callback(self, inst, value):
        self.blocking_callback_count += 1
        return True

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
        new_d1_p1 = self.create_different_value(d1_p1)
        while new_d1_p1 == d2_p1:                           # Make sure it is different from d2.p1
            new_d1_p1 = self.create_different_value(d1_p1)
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
            different_value = self.create_different_value(value)
            dc = self.assert_callback_count
            self.assertNotEqual(value, different_value)
            setattr(dispatcher, info['name'], different_value)
            info = dispatcher.event_dispatcher_properties[prop_name]  # May need to get the updated reference to info.
            self.assertEqual(dc + 1, self.assert_callback_count)
            if hasattr(info['value'], '__iter__'):
                self.assertItemsEqual(info['value'], different_value)
            else:
                self.assertEqual(info['value'], different_value)

    def test_block_dispatch_propagation(self):
        """
        Test that if a callback in the dispatch sequence returns True, the propagation stops.
        """
        dispatcher = self.dispatcher
        dispatcher.unbind_all('p1')
        self.assertEqual(self.assert_callback_count, 0)
        dispatcher.bind(p1=self.assert_callback)
        dispatcher.bind(p1=self.assert_callback)
        dispatcher.bind(p1=self.blocking_callback)
        dispatcher.bind(p1=self.assert_callback)

        dispatcher.p1 = self.create_different_value(dispatcher.p1)
        self.assertEqual(self.assert_callback_count, 2)

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
            self.dispatcher.p1 = self.create_different_value(self.dispatcher.p1)
            self.assertEqual(self.dispatcher.p1, self.dispatcher2.p1)
        self.assertEqual(self.assert_callback_count, expected_dispatches)
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

    def test_pickle(self):
        """
        Test that the property's value can be picked and unpickled. Note that unpickling a property does not
        restore the property, only it's value.
        :return:
        """
        self.dispatcher.p1 = value = self.create_different_value(self.dispatcher.p1)
        # Test pickling
        s = pickle.dumps(self.dispatcher.p1)
        assert isinstance(s, basestring)
        # Test un-pickling
        o = pickle.loads(s)
        self.assertEqual(o, value)