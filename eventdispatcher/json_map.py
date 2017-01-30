from eventdispatcher import DictProperty, ListProperty, Property, StringProperty, EventDispatcher
import json as JSON
from functools import partial

eventdispatcher_map = {dict: DictProperty,        list: ListProperty,     tuple: Property,
                       int: Property,             float: Property,        long: Property,
                       bool: Property,            None: Property,
                       unicode: StringProperty,   str: StringProperty}


class NoAttribute(object):
    pass


class JSON_Map(EventDispatcher):

    _mapped_classes = {}

    def __init__(self, json):
        self.raw = json
        # Check if this class has ever been initialized before, if not
        # perform the definition of event dispatcher properties to the class
        cls = self.__class__
        class_name = cls.__name__
        properties = JSON_Map._mapped_classes.get(class_name, None)
        if properties is None:
            properties = JSON_Map.map_attributes(self, json)
            for prop_name, prop in properties.iteritems():
                if not hasattr(self, prop_name):
                    setattr(cls, prop_name, prop)
            JSON_Map._mapped_classes[class_name] = properties

        super(JSON_Map, self).__init__(json)

        with self.temp_unbind_all(*self.event_dispatcher_properties.iterkeys()):
            for key in properties.iterkeys():
                if key in json:
                    setattr(self, key, json[key])
        self.bind(**{p: partial(self._update_raw , p) for p in properties})

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

