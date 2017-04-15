from eventdispatcher import EventDispatcher, Property, ListProperty

def pyprint(text):
    print "Python:       %s\n" % text

print "\n\n"
pyprint('Starting edtest.py\n')


class EventDispatcher(EventDispatcher):

    age = Property(27.5)
    shirts = ListProperty([])

    # def __init__(self):
    #
    #     super(EventDispatcher, self).__init__()
    #     for cls in reversed(self.__class__.__mro__):
    #         for prop_name, prop in cls.__dict__.iteritems():
    #             if isinstance(prop, cProperty):
    #                 pyprint('Registering EventDispatcher property %s' % prop_name)
    #                 prop.register(self, prop_name, prop.default_value)


def do_something(inst, value):
    print 'Doing something! %s, %s' % (inst, value)
    return True

def do_something_else(inst, value):
    print 'something ELSE! %s, %s' % (inst, value)



pyprint('Creating EventDispatcher object')
e = EventDispatcher()

pyprint('Getting event_dispatcher_properties:')
pyprint(e.event_dispatcher_properties)


#for k in dir(e):
#    print "%50s %50s" % (k, getattr(e, k))




#e.event_dispatcher_properties['age']['callbacks'].append(do_something)
pyprint('Binding')
asd = e.bind(age=do_something)
asd = e.bind(age=do_something_else)
pyprint('asd = %s' % asd)

pyprint(e.event_dispatcher_properties)

pyprint('Getting cProperty "age": %s' % e.age)

pyprint('Setting cProperty "age to 30": ')
e.age = 30.5
pyprint('Getting cProperty "age": %s' % e.age)


pyprint('Setting cProperty "age to 30": ')
e.age = 30


e.bind(shirts=do_something)
e.shirts = ['red', 'green']
e.shirts = ('red', 'green')
asd = e.shirts
# e.shirts = ('red', 'blue')
# print e.shirts
pyprint('Getting cListProperty "shirts": %s' % (e.shirts, ))
