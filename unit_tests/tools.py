__author__ = 'Owner'

from random import random, randint

force_dispatcher = {}


def create_different_value(self, value):
    different_value = {str(i): randint(0, 1000) for i in xrange(10)}
    while different_value == value:
        return self.create_different_value(value)
    else:
        return different_value
force_dispatcher['DictProperty'] = create_different_value


def create_different_value(self, value):
    if isinstance(value, float):
        different_value = random()
    elif isinstance(value, int):
        different_value = randint(MIN, MAX)
    while different_value == value:
        return self.create_different_value(value)
    else:
        return different_value
force_dispatcher['LimitProperty'] = create_different_value


def create_different_value(self, value):
    different_value = [randint(0, 1000) for i in xrange(10)]
    while different_value == value:
        return self.create_different_value(value)
    else:
        return different_value
force_dispatcher['ListProperty'] = create_different_value


def create_different_value(self, value):
    different_value = set([randint(0, 1000) for i in xrange(10)])
    while different_value == value:
        return self.create_different_value(value)
    else:
        return different_value
force_dispatcher['SetProperty'] = create_different_value


def create_different_value(self, value):
    different_value = 'new ' + str(value)
    return different_value
force_dispatcher['StringProperty'] = create_different_value




