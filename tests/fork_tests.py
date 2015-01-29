from StringIO import StringIO
from unittest import TextTestRunner
from fuel_health.tests.smoke.test_very_basic import TestUserTenantRole
import unittest2 as ut

result = None


class MyTestRunner(TextTestRunner):
    def __init__(self):
        s = StringIO()

        TextTestRunner.__init__(self, stream=s)

    def run(self, test):
        result = self._makeResult()
        test(result)
        return result

def test_fork():
    pass


def test_greenlets():
    from greenlet import greenlet

    def test1():
        print 'net request received'
        gr2.switch()
        print 'net request handled'

    def test2():
        print 'handling net request'
        gr1.switch()
        print 78

    gr1 = greenlet(test1)
    gr2 = greenlet(test2)
    gr2.switch()
    gr1.switch()


def test_test_runners():
    print "BEFORE"
    s = StringIO()

    runner = ut.TextTestRunner(stream=s)
    # runner = MyTestRunner()
    result = runner.run(ut.makeSuite(TestUserTenantRole))

    print 'stream = '
    print "AFTER"
    print runner
    print 'errors = ', result.errors
    print 'failures = ', result.failures

    for failing_test, traceback in result.failures:
        print 'failing test:', dir(failing_test)
        print 'traceback:', traceback
    print 'result = ', result


def f(x):
    return x*x


if __name__ == '__main__':
    # test_test_runners()
    # test_greenlets()
    from multiprocessing import pool

    p = pool.Pool(5)
    print(p.map(f, [1,2,3]))
