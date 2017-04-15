__author__ = 'calvin'

import os
import collections

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
IS_COMPILED = os.path.exists(os.path.join(MODULE_DIR, 'cpp', 'eventdispatcher.so'))

if IS_COMPILED:
    print 'Compiled version of EventDispatcher found.'
    from cpp import eventdispatcher as cED
    EventDispatcherBase = cED.cEventDispatcher
    PropertyBase = cED.cProperty
else:
    EventDispatcherBase = object
    PropertyBase = object
    # Bases for the following have not been defined until the Property class is defined.
    # Initialize the bases to None and call _update_bases() to fix the references after the Property
    # class is defined.
    ListPropertyBase = None


def _update_bases(property_base):
    """
    This function is called once the Property class is defined.
    It sets the MRO for all other properties which inherit from Property.
    """
    global PropertyBase, ListPropertyBase, ObservableListBase
    PropertyBase = property_base

    if IS_COMPILED:
        # Redefine the base classes
        class ListPropertyBase(PropertyBase, cED.cListProperty):
            pass

        class ObservableListBase(cED.cObservableList):
            pass

    else:
        ListPropertyBase = PropertyBase
        ObservableListBase = collections.MutableSequence


def _get_base(class_name):
    """
    Lookup function for returning the base class used for event dispatcher property classes.
    This is required because we only define the Property class (which is used as the base for all other properties)
    after this file has been imported. Therefore property subclasses need to call this function in order to
    get an up to date reference of the base class.
    :param class_name: Name of the class we need to look up a base for
    :return: Base class
    """
    return {'Property': PropertyBase,
            'ListProperty': ListPropertyBase,
            'ObservableList': ObservableListBase}[class_name]