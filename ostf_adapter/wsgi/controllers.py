#    Copyright 2015 Mirantis, Inc
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import logging

from oslo.config import cfg
from pecan import abort
from pecan import expose
from pecan import request
from pecan import rest
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from ostf_adapter import mixins
from ostf_adapter.storage import models


LOG = logging.getLogger(__name__)


class BaseRestController(rest.RestController):
    pass


class TestsetsController(BaseRestController):
    @expose('json')
    def get(self):
        mixins.discovery_check(request.session, request.token)

        test_sets = request.session.query(models.TestSet)\
            .filter(models.TestSet.id.in_(cfg.CONF.adapter.test_sets))\
            .order_by(models.TestSet.test_runs_ordering_priority)\
            .all()

        if test_sets:
            return [item.frontend for item in test_sets]
        return {}


class TestsController(BaseRestController):
    @expose('json')
    def get(self):
        mixins.discovery_check(request.session, request.token)
        query = request.session.query(models.Test)
        test_set = models.Test.test_set_id
        needed_tests_list = query.filter(test_set.in_(
            cfg.CONF.adapter.test_sets))

        return needed_tests_list.all()

    @expose('json')
    def post(self, *args):
        args_invalid = not args or len(list(args)) != 2 or not (
            args[0] in cfg.CONF.adapter.test_sets and args[1] == 'run')

        if args_invalid:
            abort(404)

        testset = args[0]
        metadata = {}
        tests = []

        q = request.session.query(models.TestSet)
        testset = q.filter(models.TestSet.id == testset).first()

        res = models.TestRun.start(
            request.session,
            testset,
            metadata,
            tests,
            cfg.CONF.adapter.dbpath,
            token=request.token
        )

        return res


class TestrunsController(BaseRestController):

    _custom_actions = {
        'last': ['GET'],
    }

    @expose('json')
    def get_all(self):
        test_runs = request.session.query(models.TestRun).all()

        return [item.frontend for item in test_runs]

    @expose('json')
    def get_one(self, test_run_id):
        test_run = request.session.query(models.TestRun)\
            .filter_by(id=test_run_id).first()
        if test_run and isinstance(test_run, models.TestRun):
            return test_run.frontend
        return {}

    @expose('json')
    def get_last(self):
        test_run_ids = request.session.query(func.max(models.TestRun.id)) \
            .group_by(models.TestRun.test_set_id).all()

        test_runs = request.session.query(models.TestRun)\
            .options(joinedload('tests'))\
            .filter(models.TestRun.id.in_(test_run_ids))

        return [item.frontend for item in test_runs]

    @expose('json')
    def post(self):
        test_runs = json.loads(request.body)
        if 'objects' in test_runs:
            test_runs = test_runs['objects']

        # Discover tests for all clusters in request
        nedded_testsets = set()
        for test_run in test_runs:
            mixins.discovery_check(request.session, request.token)
            nedded_testsets.add(test_run['testset'])
        # Validate testsets from request
        test_sets = set([testset.id for testset in request.
                        session.query(models.TestSet).all()])
        if nedded_testsets - test_sets:
            abort(400)

        res = []
        for test_run in test_runs:
            test_set = test_run['testset']
            metadata = test_run['metadata']
            tests = test_run.get('tests', [])

            test_set = models.TestSet.get_test_set(
                request.session,
                test_set
            )

            test_run = models.TestRun.start(
                request.session,
                test_set,
                metadata,
                tests,
                cfg.CONF.adapter.dbpath,
                token=request.token
            )

            res.append(test_run)

        return res

    @expose('json')
    def put(self):
        test_runs = json.loads(request.body)
        if 'objects' in test_runs:
            test_runs = test_runs['objects']

        data = []
        with request.session.begin(subtransactions=True):
            for test_run in test_runs:
                status = test_run.get('status')
                tests = test_run.get('tests', [])
                ostf_os_access_creds = test_run.get('ostf_os_access_creds')

                test_run = models.TestRun.get_test_run(request.session,
                                                       test_run['id'])
                if status == 'stopped':
                    data.append(test_run.stop(request.session))
                elif status == 'restarted':
                    data.append(test_run.restart(request.session,
                                                 cfg.CONF.adapter.dbpath,
                                                 ostf_os_access_creds,
                                                 tests=tests,
                                                 token=request.token))
        return data
