# Copyright 2015 Mirantis Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from datetime import datetime
from multiprocessing import Process
from pecan import expose
from unittest import TextTestRunner
from unittest import makeSuite

from cloudv_ostf_adapter._adapter_app.db import models as db_models


def _run_test_suit(runner, suite):
    for test in suite._tests:
        runner.run(test)


def start_async(tests):
    runner = TextTestRunner(verbosity=3, failfast=True)
    suite = makeSuite(tests)
    p = Process(target=_run_test_suit, args=(runner, suite))
    test_set_mapper_class = db_models.TestSet(
        name=str(suite),
        description="TestSet for %s" % str(suite)
    )

    tests_mapper_class = db_models.Test(
        name="Test execution for %s" % str(suite),
        description="Test execution for %s" % str(suite),
        testset=test_set_mapper_class
    )

    testrun = db_models.TestRun(
        status=db_models.TESTRUN_IN_PROGRESS,
        result=None,
        tests=tests_mapper_class,
        started_at=datetime.utcnow(),
        pid=p.pid
    )

    p.start()

    while not p.is_alive():
        p.terminate()
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
        return db_models.get_all_testsets()


def find_test(uid):
    return db_models.Test(id=uid)


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
        return db_models.get_all_tests()


class Testsets(object):
    @expose('json')
    def _default(self):
        return db_models.get_all_testsets()


class RootController(object):
    tests = Tests()
    testsets = Testsets()
    testruns = Testruns()
