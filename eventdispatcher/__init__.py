import json

from .eventdispatcher import EventDispatcher
from .property import Property
from .dictproperty import DictProperty, ObservableDict
from .limitproperty import LimitProperty
from .listproperty import ListProperty, ObservableList
from .optionproperty import OptionProperty
from .setproperty import SetProperty, ObservableSet
from .stringproperty import StringProperty, _
from .unitproperty import UnitProperty
from .weakrefproperty import WeakRefProperty
from .scheduledevent import ScheduledEvent
from .clock import Clock
from .json_map import JSON_Map
from .exceptions import *
from .version import __version__


class PropertyEncoder(json.JSONEncoder):
    """
    Encoder that helps with the JSON serializing of properties. In particular, ObservableDict and ObservableList
    """

    def default(self, o):
        try:
            r = super(PropertyEncoder, self).default(o)
        except TypeError as e:
            if isinstance(o, ObservableList):
                return o.list
            elif isinstance(o, ObservableDict):
                return o.dictionary
            elif isinstance(o, JSON_Map):
                return o.raw
            else:
                raise e

        return r
