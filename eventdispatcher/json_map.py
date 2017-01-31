from eventdispatcher import DictProperty, ListProperty, Property, StringProperty, EventDispatcher
import json as JSON
from functools import partial

eventdispatcher_map = {dict: DictProperty,        list: ListProperty,     tuple: Property,
                       int: Property,             float: Property,        long: Property,
                       bool: Property,            None: Property,
                       unicode: StringProperty,   str: StringProperty}


class NoAttribute(object):
    pass


def dict_generator(indict, pre=None):
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_generator(value, [key] + pre):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in dict_generator(v, [key] + pre):
                        yield d
            else:
                yield pre + [key, value]
    else:
        yield indict


class JSON_Map(EventDispatcher):

    def __init__(self, json):
        self.raw = json
        # Check if this class has ever been initialized before, if not
        # perform the definition of event dispatcher properties to the class
        cls = self.__class__
        properties = JSON_Map.map_attributes(self, json)
        for prop_name, prop in properties.iteritems():
            if not hasattr(self, prop_name):
                setattr(cls, prop_name, prop)

        super(JSON_Map, self).__init__(json)

        with self.temp_unbind_all(*self.event_dispatcher_properties.iterkeys()):
            for key in properties.iterkeys():
                if key in json:
                    setattr(self, key, json[key])
        self.bind(**{p: partial(self._update_raw , p) for p in properties})

    def keys(self):
        return self.raw.keys()

    def values(self):
        return [v for v in self.itervalues()]

    def items(self):
        return [v for v in self.iteritems()]

    def get(self, *args):
        return getattr(self, *args)

    def iteritems(self):
        for key in self.event_dispatcher_properties:
            yield key, getattr(self, key)

    def iterkeys(self):
        return self.event_dispatcher_properties.iterkeys()

    def itervalues(self):
        for key in self.event_dispatcher_properties:
            yield getattr(self, key)

    def __reduce__(self):
        return dict, tuple(), None, None, self.raw.iteritems()

    def __contains__(self, item):
        return item in self.event_dispatcher_properties

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        else:
            raise KeyError(item)

    def __setitem__(self, key, value):
        if key in self.event_dispatcher_properties or isinstance(getattr(self.__class__, key, AttributeError), property):
            # The key maps to an event dispatcher property or python property
            setattr(self, key, value)
        else:
            raise TypeError('Cannot set %s using item assignment' % key)

    def update(self, E=None, **F):
        if E and self.raw != E:
            for k, v in E.items():
                self[k] = v
                if hasattr(self[k], 'update'):
                    self[k].update(v)
        elif F and self.raw != F:
            for k, v in F.items():
                self[k] = v
                if hasattr(self[k], 'update'):
                    self[k].update(v)

    def _update_raw(self, property_name, inst, value):
        """
        Callback to keep property values in sync with the underlying JSON object.
        """
        if property_name in self.raw:
            self.raw[property_name] = value
        else:
            raise AttributeError('Attribute %s is not found in the underlying JSON object.' % property_name)

    @staticmethod
    def map_attributes(obj, json):
        # Iterate through the JSON structure and create eventdispatcher properties for the attributes
        cls = obj.__class__
        attrs = {}
        for k, v in json.iteritems():
            obj_attr_exists = hasattr(obj, k)
            if obj_attr_exists:
                continue
            elif any([isinstance(getattr(c, k, NoAttribute), property) for c in cls.__mro__]):
                # Check if any class attributes are properties
                continue
            else:
                attrs[k] = eventdispatcher_map[type(v)](v)
        return attrs


if __name__ == '__main__':

    path = '/home/local/SENSOFT/clobo/projects/lmx/PygameLMX/resources/platforms/PulseEKKO.conf'
    with open(path, 'r') as f:
        js = JSON.load(f)
    obj = JSON_Map.map('PlatformConfig', js)
    sdfds=3

