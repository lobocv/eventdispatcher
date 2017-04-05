import eventdispatcher as ED

print 'Using compiled version' if ED.IS_COMPILED else 'Using python version'


class A(ED.EventDispatcher):

    age = ED.Property(10)


a = A()

def do_something(*args):
    print 'Doing something! %s' % str(args)

a.bind(age=do_something)
a.age = 20
a.age = 10
a.age = 10
a.age = 15
