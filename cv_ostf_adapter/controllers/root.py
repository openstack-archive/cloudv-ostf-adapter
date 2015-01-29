from datetime import datetime
from io import StringIO
from multiprocessing import Process
from pecan import expose
from unittest import TextTestRunner, makeSuite

from cv_ostf_adapter.db import models

# from fuel_health.tests.smoke import test_create_flavor


def start_async(tests):
    s = StringIO()
    runner = TextTestRunner(stream=s)
    suite = makeSuite(tests)
    p = Process(target=runner.run, args=suite)
    p.start()

    testrun = models.TestRun(
        status=models.TESTRUN_IN_PROGRESS,
        result=None,
        tests=tests,
        started_at=datetime.utcnow(),
        pid=p.pid
    )

    return testrun


class Testruns(object):
    def __init__(self, id=None):
        self.id = id

    def abort(self):
        pass

    @expose('json')
    def run(self):
        return {'test': 'run'}

    @expose('json')
    def _lookup(self, key, *remainder):
        return {'testruns': 'lookup',
                'args': {'key': key,
                         'remainder': remainder}}, remainder
    @expose('json')
    def _default(self):
        return models.get_all_testsets()


def find_test(uid):
    return models.Test(id=uid)


class Tests(object):
    def run_test(self, uid):
        test = find_test(uid)
        testrun = start_async(test)

        return testrun

    def get_test(self, uid):
        return find_test(uid)

    @expose('json')
    def query(self, *args, **kwargs):
        return {'query': {'args': args, 'kwargs': kwargs}}

    @expose('json')
    def _lookup(self, uid, *remainder):
        if remainder and remainder[0] == 'run':
            return self.run_test(uid), remainder
        return self.get_test(uid), remainder

    @expose('json')
    def _default(self):
        return models.get_all_tests()


class Testsets(object):
    @expose('json')
    def _default(self):
        return models.get_all_testsets()


class RootController(object):
    tests = Tests()
    testsets = Testsets()
    testruns = Testruns()