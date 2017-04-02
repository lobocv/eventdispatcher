from eventdispatcher.cpp import eventdispatcher as ED

def pyprint(text):
    print "Python:       %s" % text

print "\n\n"
pyprint('Starting edtest.py\n')


class EventDispatcher(ED.cEventDispatcher):

    age = ED.cProperty(27)

    def __init__(self):

        super(EventDispatcher, self).__init__()
        for cls in reversed(self.__class__.__mro__):
            for prop_name, prop in cls.__dict__.iteritems():
                if isinstance(prop, ED.cProperty):
                    pyprint('Registering EventDispatcher property %s' % prop_name)
                    prop.register_(self, prop_name, prop.default_value)




pyprint('Creating EventDispatcher object')
e = EventDispatcher()

pyprint('Getting event_dispatcher_properties:')
pyprint(e.event_dispatcher_properties)


#for k in dir(e):
#    print "%50s %50s" % (k, getattr(e, k))




pyprint('Getting cProperty "age": %s' % e.age)
pyprint('Setting cProperty "age to 30": ')
e.age = 30
