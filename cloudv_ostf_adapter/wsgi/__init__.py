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
import multiprocessing
import os
import os.path
import uuid

from flask.ext import restful
from flask.ext.restful import abort
from flask.ext.restful import reqparse
from flask import request
from oslo_config import cfg

from cloudv_ostf_adapter import validation_plugin


CONF = cfg.CONF
CREATED = 'CREATED'
IN_PROGRESS = 'IN PROGRESS'
COMPLETED = 'COMPLETED'


class BaseTests(restful.Resource):
    def __init__(self, *args, **kwargs):
        super(BaseTests, self).__init__(*args, **kwargs)
        self.plugins = {}
        for plugin in validation_plugin.VALIDATION_PLUGINS:
            _plugin = plugin(load_tests=False)
            self.plugins[_plugin.name] = _plugin

    def load_tests(self):
        for plugin in self.plugins.values():
                plugin.tests = plugin.get_tests()

    def get_plugin(self, **kwargs):
        plugin = kwargs.pop('plugin', None)
        if plugin is None or plugin not in self.plugins:
            abort(404,
                  message='Unsupported plugin %s.' % plugin)
        return self.plugins[plugin]

    def get_suite(self, plugin, suite=None):
        if suite not in plugin.suites:
            abort(404,
                  message='Unknown suite %s.' % suite)
        return suite

    def path_from_job_name(self, job_id):
        return '/'.join((CONF.rest.jobs_dir, job_id))

    def get_job(self, **kwargs):
        job_id = kwargs.pop('job_id', None)
        if job_id is None:
            abort(400,
                  message="Job id is missing.")
        file_name = self.path_from_job_name(job_id)
        if not os.path.exists(file_name):
            abort(404,
                  message="Job not found.")
        return (job_id, file_name)


class Plugins(BaseTests):

    def __init__(self, *args, **kwargs):
        super(Plugins, self).__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('load_tests',
                                 type=str,
                                 location='args',
                                 required=False)

    def get(self, **kwargs):
        args = self.parser.parse_args()
        load_tests = args.pop('load_tests', False)
        if load_tests in ['True', 'true', '1']:
            self.load_tests()
        plugins = [
            {'name': p.name,
             'suites': p.suites,
             'tests': p.tests}
            for p in self.plugins.values()
        ]
        return {'plugins': plugins}


class PluginSuite(BaseTests):

    def get(self, **kwargs):
        plugin = self.get_plugin(**kwargs)
        return {'plugin': {'name': plugin.name,
                           'suites': plugin.suites}}

    def post(self, **kwargs):
        plugin = self.get_plugin(**kwargs)
        self.load_tests()
        reports = plugin.run_suites()
        report = [r.description for r in reports]
        return {"plugin": {"name": plugin.name,
                           "report": report}}


class PluginTests(BaseTests):

    def get(self, **kwargs):
        plugin = self.get_plugin(**kwargs)
        self.load_tests()
        return {'plugin': {'name': plugin.name,
                           'tests': plugin.tests}}


class Suites(BaseTests):

    def get(self, **kwargs):
        plugin = self.get_plugin(**kwargs)
        _suite = kwargs.pop('suite', None)
        suite = self.get_suite(plugin, suite=_suite)
        self.load_tests()
        tests = plugin.get_tests_by_suite(suite)
        return {'plugin': {'name': plugin.name,
                           'suite': {'name': suite,
                                     'tests': tests}}}

    def post(self, **kwargs):
        plugin = self.get_plugin(**kwargs)
        _suite = kwargs.pop('suite', None)
        suite = self.get_suite(plugin, suite=_suite)
        self.load_tests()
        reports = plugin.run_suite(suite)
        report = [r.description for r in reports]
        return {"suite": {"name": suite,
                          "report": report}}


class Tests(BaseTests):

    def post(self, **kwargs):
        plugin = self.get_plugin(**kwargs)
        self.load_tests()
        test = kwargs.pop('test', None)
        if test is None or test not in plugin.tests:
            abort(404,
                  message="Test %s not found." % test)
        reports = plugin.run_test(test)
        report = [r.description for r in reports]
        report[0]['test'] = test
        return {"plugin": {"name": plugin.name,
                           "test": test,
                           "report": report}}


class JobsCreation(BaseTests):

    def post(self, **kwargs):
        try:
            data = request.json
        except Exception:
            abort(400,
                  message="JSON is missing.")
        if data is None:
            abort(400,
                  message="JSON is missing.")
        job = data.get('job', None)
        if job is None:
            abort(400,
                  message="JSON doesn't have `job` key.")
        mandatory = ['name',
                     'tests',
                     'description']
        missing = set(mandatory) - set(job.keys())
        missing = list(missing)
        missing.sort()
        if missing:
            abort(400,
                  message="Fields %s are not specified." % ','.join(missing))
        self.load_tests()
        filtered_tests = []
        for p in self.plugins.values():
            tests_in_plugin = set(p.tests) & set(job['tests'])
            filtered_tests.extend(tests_in_plugin)
        not_found = set(job['tests']) - set(filtered_tests)
        not_found = list(not_found)
        not_found.sort()
        if not_found:
            abort(400,
                  message="Tests not found (%s)." % ','.join(not_found))
        job_uuid = str(uuid.uuid4())
        file_name = self.path_from_job_name(job_uuid)
        job['status'] = CREATED
        with open(file_name, 'w') as f:
            f.write(json.dumps(job))
        job['id'] = job_uuid
        return {'job': job}


class Execute(BaseTests):

    def post(self, **kwargs):
        job_id, file_name = self.get_job(**kwargs)
        data = {}
        with open(file_name, 'r') as f:
            data = json.loads(f.read())
        with open(file_name, 'w') as f:
            data['status'] = IN_PROGRESS
            data['report'] = []
            f.write(json.dumps(data))
        p = multiprocessing.Process(target=self._execute_job,
                                    args=(data, job_id))
        p.start()
        job = data.copy()
        job['id'] = job_id
        return {'job': job}

    def _execute_job(self, data, job_id):
        tests = data['tests']
        self.load_tests()
        reports = []
        for name, plugin in self.plugins.iteritems():
            tests_in_plugin = set(plugin.tests) & set(tests)
            for test in tests_in_plugin:
                results = plugin.run_test(test)
                report = [r.description for r in results].pop()
                report['test'] = test
                reports.append(report)
        data['status'] = COMPLETED
        data['report'] = reports
        file_name = self.path_from_job_name(job_id)
        with open(file_name, 'w') as f:
            f.write(json.dumps(data))


class Job(BaseTests):

    def get(self, **kwargs):
        job_id, file_name = self.get_job(**kwargs)
        data = {}
        with open(file_name, 'r') as f:
            data = json.loads(f.read())
        job = data.copy()
        job['id'] = job_id
        return {'job': job}

    def delete(self, **kwargs):
        job_id, file_name = self.get_job(**kwargs)
        os.remove(file_name)
        return {}


class Jobs(BaseTests):

    def get(self):
        res = []
        jobs = [f for (dp, dn, f) in os.walk(CONF.rest.jobs_dir)][0]
        for job in jobs:
            file_name = self.path_from_job_name(job)
            with open(file_name, 'r') as f:
                data = json.loads(f.read())
            data['id'] = job
            res.append(data)
        return {'jobs': res}
