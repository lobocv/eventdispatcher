from eventdispatcher import EventDispatcher, Property, ListProperty


def my_callback(inst, value):
    print 'This is from my_callback'


class Dispatcher(EventDispatcher):
    name = Property('Bob')
    favourite_foods = ListProperty(['pizza', 'tacos'])


    def on_name(self, instance, value):
        print 'My name has changed to %s!' % value





if __name__ == '__main__':

    d = Dispatcher()
    d2 = Dispatcher()

    d.name = 'Bob'       # No event is dispatched, the value of name has not changed.
    d2.name = 'Calvin'   # Event is dispatched because name changed from Bob to Calvin

    d.bind(name=my_callback)
    d.name = 'Rick'                                 # on_name() and my_callback() will be called
    d.favourite_foods = ['hot dogs', 'burgers']     # Nothing will be called



    def print_callback(inst, value):
        print inst.name, value

    d.bind(favourite_foods=d2.setter('favourite_foods'))    # Bind d.favourite_foods to d2.favourite_foods
    d.bind(favourite_foods=print_callback)                  # Bind d.favourite_foods to print_callback
    d2.bind(favourite_foods=print_callback)                 # Bind d2.favourite_foods to print_callback

    d2.dispatch('favourite_foods', d, d.favourite_foods.list)       #  Rick ['hot dogs', 'burgers']
    d.favourite_foods = ['apples', 'bananas']                       #  Calvin ['apples', 'bananas']
                                                                    #  Rick ['apples', 'bananas']
    d2.favourite_foods = ['beef', 'chicken']                        #  Calvin ['beef', 'chicken']

    a=1