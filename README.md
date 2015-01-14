EventDispatcher
===============

An event dispatcher framework inspired by the [Kivy project](http://kivy.org/#home).
 
Property instances are monitored and dispatch events when their value changes. The event callback handler name defaults to the `on_PROPERTY_NAME` and is
called with two arguments: the dispatcher instance and the <b>new</b> value of the property.

New in Version 1.5
==================

- Speed increase of 3 times for dispatching
- Speed increase of 4 times for setting property values
- Speed increase of 3 times for getting property values
- Property.get_property() has been replaced with Eventdispatcher.get_dispatcher_property()
- More comprehensive UnitTests
    
Learn by Example:
================

Creating a Dispatcher
---------------------
    from eventdispatcher import EventDispatcher, Property, ListProperty
    
    class Dispatcher(EventDispatcher):
        name = Property('Bob')          
        favourite_foods = ListProperty(['pizza', 'tacos'])
        
        def on_name(self, instance, value):
            print 'My name has changed to %s!' % value 
        
            
    d = Dispatcher()
    d2 = Dispatcher()
Changing A Property's Value
---------------------------

    d.name = 'Bob'      # No event is dispatched, the value of name has not changed.
    d.name = 'Calvin'   # Event is dispatched

Result:

    My name has changed to Calvin!
    
    
Binding Events
--------------

You can bind functions to the event queue and call multiple functions when the event dispatches.

    def my_callback(inst, value):
        print 'This is from my_callback'
        
    d.bind(name=my_callback)
    d.name = 'Rick'                                 # on_name() and my_callback() will be called 
    d.favourite_foods = ['hot dogs', 'burgers']     # Nothing will be called
    
When an event is dispatched, the EventDispatcher calls each bound function in order, starting with the default handler.
You do not need to define a default handler, the EventDispatcher will not attempt to call it if it does not exist.
    
Result:

    My name has changed to Rick!
    This is from my_callback
    
Manually Dispatching an Event
-----------------------------
You can also dispatch an event manually:

    d.dispatch('name', d, d.name)
    
    
Binding Properties to Properties
--------------------------------

You can bind an event to another so that when one changes, the other will reflect those changes.

    def print_callback(inst, value):
        print inst.name, value
        
    d = Dispatcher()
    d.name = 'Rick'      
    d.favourite_foods = ['hot dogs', 'burgers']
    
    d2 = Dispatcher()
    d2.name = 'Calvin'   

    d.bind(favourite_foods=d2.setter('favourite_foods'))    # Bind d.favourite_foods to d2.favourite_foods
    d.bind(favourite_foods=print_callback)                  # Bind d.favourite_foods to print_callback
    d2.bind(favourite_foods=print_callback)                 # Bind d2.favourite_foods to print_callback

    d2.dispatch('favourite_foods', d, d.favourite_foods.list)       #  Rick ['hot dogs', 'burgers']
    d.favourite_foods = ['apples', 'bananas']                       #  Calvin ['apples', 'bananas']
                                                                    #  Rick ['apples', 'bananas']
    d2.favourite_foods = ['beef', 'chicken']                        #  Calvin ['beef', 'chicken']
