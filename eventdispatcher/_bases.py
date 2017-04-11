__author__ = 'calvin'

import os

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
IS_COMPILED = os.path.exists(os.path.join(MODULE_DIR, 'cpp', 'eventdispatcher.so'))

if IS_COMPILED:
    print 'Compiled version of EventDispatcher found.'
    from cpp import eventdispatcher as cED
    EventDispatcherBase = cED.cEventDispatcher
    PropertyBase = cED.cProperty
    ListPropertyBase = cED.cListProperty
else:
    EventDispatcherBase = object
    PropertyBase = object
    ListPropertyBase = object
