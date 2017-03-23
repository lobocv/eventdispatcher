import json
from .dictproperty import ObservableDict
from .listproperty import ObservableList



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
            else:
                raise e
        return r
