[![Build Status](https://travis-ci.org/lobocv/eventdispatcher.svg?branch=master)](https://travis-ci.org/lobocv/eventdispatcher)

EventDispatcher
===============

An event dispatcher framework inspired by the [Kivy project](http://kivy.org/#home).
 
Property instances are monitored and dispatch events when their value changes. The event callback handler name defaults to `on_PROPERTY_NAME` and is
called with two arguments: the dispatcher instance and the value of the property.

Installation
==================

You can install eventdispatcher using pip package manager:

    pip install eventdispatcher

    
Learn by Example:
================

Creating a Dispatcher
---------------------

In our example, we have a settings file that needs to be constantly written to and updated whenever certain settings 
change. We have two settings that the file tracks, `last_login` and `favourite_color`. 

We can create a EventDispatcher class that can automatically update the file with the latest values whenever they are changed.

```python
    
    import json
    from eventdispatcher import EventDispatcher, Property
    
    class SettingsFile(EventDispatcher):
        last_login = Property(None)
        favourite_color = Property('red')
    
        def __init__(self, filepath):
            super(SettingsFile, self).__init__()
            self.filepath = filepath
            self.number_of_file_updates = 0
            # Bind the properties to the function that updates the file
            self.bind(last_login=self.update_settings_file,
                      favourite_color=self.update_settings_file)
    
        def on_last_login(self, inst, last_login):
            # Default handler for the last_login property
            print 'last login was %s' % last_login
    
        def on_color(self, inst, color):
            # Default handler for the color property
            print 'color has been set to %s' % color
    
        def update_settings_file(self, *args):
            # Update the file with the latest settings.
            print 'Updating settings file.'
            self.number_of_file_updates += 1
            with open(self.filepath, 'w') as _f:
                settings = {'last_login': self.last_login, 'favourite_color': self.favourite_color}
                json.dump(settings, _f)
                
```

Now, in the application, we no longer need to worry about updating the settings file, changing any of the settings will 
do that for us!

```python
    s = SettingsFile('./myfile.json')
    s.last_login = 'May 18 2015'             # Updates settings file
    # last login was May 18 2015
    # Updating settings file.
    s.favourite_color = 'blue'               # Updates settings file
    # color has been set to blue
    # Updating settings file.  
      
```

The bound functions are only called when the value of the properties change, so assigning the same date and color will do nothing.

```python
    s.last_login = 'May 18 2015'             # Does not update the settings file
    s.favourite_color = 'blue'               # Does not update the settings file  
```
    
Binding Events
--------------

You can bind functions to the event queue and call multiple functions when the event dispatches. The handler for the 
binding is called with the EventDispatcher instance and the property value as the arguments. 

In our example, SettingsFile has default handlers for both color and last_login properties that just print a notification.
In addition to these default handlers we bound both of those properties to the function that updates the settings file:

```python

    self.bind(last_login=self.update_settings_file,
              favourite_color=self.update_settings_file)
              
```
    
When an event is dispatched, the EventDispatcher calls each bound function in order, starting with the default handler.
You do not need to define a default handler, the EventDispatcher will not attempt to call it if it does not exist.
    
    
Manually Dispatching an Event
-----------------------------
You can also dispatch an event manually:

    d.dispatch('name', d, d.name)
    
    
Binding Properties to Properties
--------------------------------

You can bind an event to another so that when one changes, the other will reflect those changes.
        
    file1 = SettingsFile('./myfile1.json')
    file2 = SettingsFile('./myfile2.json')
       
    # Binds the color property from file1 to the color property of file2
    # Changing file1.color will automatically update the value of file2.color
    file1.bind(color=file2.setter('color'))     
    
    file1.color = 'green'
    # color has been set to green       
    # Updating settings file.
    # color has been set to green
    # Updating settings file.

    
    
    
