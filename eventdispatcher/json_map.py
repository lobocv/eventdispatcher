from eventdispatcher import DictProperty, ListProperty, Property, StringProperty, EventDispatcher
import json as JSON
import types

eventdispatcher_map = {dict: DictProperty,        list: ListProperty,     tuple: Property,
                       int: Property,             float: Property,        long: Property,
                       bool: Property,            None: Property,
                       unicode: StringProperty,   str: StringProperty}


class NoAttribute(object):
    pass


class JSON_Map(EventDispatcher):

    _mapped_classes = {}

    def __init__(self, json):

        # Check if this class has ever been initialized before, if not
        # perform the definition of event dispatcher properties to the class
        cls = self.__class__
        class_name = cls.__name__
        properties = {}
        if class_name not in JSON_Map._mapped_classes:
            properties = JSON_Map.map_attributes(self, json)
            for prop_name, prop in properties.iteritems():
                if not hasattr(self, prop_name):
                    setattr(cls, prop_name, prop)
            JSON_Map._mapped_classes[class_name] = self

        super(JSON_Map, self).__init__(json)

        with self.temp_unbind_all(*self.event_dispatcher_properties.iterkeys()):
            for key in properties.iterkeys():
                setattr(self, key, json[key])

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

