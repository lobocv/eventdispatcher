__author__ = 'Calvin'

import unittest
from StringIO import StringIO
from pprint import pprint

from unit_tests.listproperty import ListPropertyTest
from unit_tests.property import PropertyTest
from unit_tests.unitproperty import UnitPropertyTest
from unit_tests.dictproperty import DictPropertyTest
RUN_TESTS = [PropertyTest, UnitPropertyTest, ListPropertyTest, DictPropertyTest]

for test in RUN_TESTS:
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream)
    result = runner.run(unittest.makeSuite(test))
    print 'Running {}, Tests run {}'.format(test.__name__, result.testsRun)
    if result.errors:
        print 'Errors: ', result.errors
    if result.failures:
        pprint(result.failures)
    stream.seek(0)
    print 'Test output:\n', stream.read()