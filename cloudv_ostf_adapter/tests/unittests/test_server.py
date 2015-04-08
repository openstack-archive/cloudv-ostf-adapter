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
import os
import shutil
import uuid

import mock
from oslo_config import cfg
import testtools

from cloudv_ostf_adapter.cmd import server
from cloudv_ostf_adapter.tests.unittests.fakes.fake_plugin import health_plugin
from cloudv_ostf_adapter import wsgi


CONF = cfg.CONF


class TestServer(testtools.TestCase):

    def setUp(self):
        self.jobs_dir = '/tmp/ostf_tests_%s' % uuid.uuid1()
        CONF.rest.jobs_dir = self.jobs_dir
        if not os.path.exists(self.jobs_dir):
            os.mkdir(self.jobs_dir)
        self.plugin = health_plugin.FakeValidationPlugin()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        self.actual_plugins = wsgi.validation_plugin.VALIDATION_PLUGINS
        wsgi.validation_plugin.VALIDATION_PLUGINS = [self.plugin.__class__]

        data = {'job': {'name': 'fake',
                        'tests': self.plugin.tests,
                        'description': 'description'}}
        rv = self.app.post(
            '/v1/jobs/create', content_type='application/json',
            data=json.dumps(data)).data
        self.job_id = self._resp_to_dict(rv)['job']['id']
        rv2 = self.app.post(
            '/v1/jobs/create', content_type='application/json',
            data=json.dumps(data)).data
        self.job_id2 = self._resp_to_dict(rv2)['job']['id']

        p = mock.patch('cloudv_ostf_adapter.wsgi.uuid.uuid4')
        self.addCleanup(p.stop)
        m = p.start()
        m.return_value = 'fake_uuid'
        execute = mock.patch('cloudv_ostf_adapter.wsgi.Execute._execute_job')
        self.addCleanup(execute.stop)
        execute.start()
        super(TestServer, self).setUp()

    def tearDown(self):
        wsgi.validation_plugin.VALIDATION_PLUGINS = self.actual_plugins
        shutil.rmtree(self.jobs_dir)
        super(TestServer, self).tearDown()

    def test_urlmap(self):
        links = []
        check_list = [
            '/v1/plugins',
            '/v1/plugins/<plugin>/suites/tests/<test>',
            '/v1/plugins/<plugin>/suites/<suite>/tests',
            '/v1/plugins/<plugin>/suites/tests',
            '/v1/plugins/<plugin>/suites/<suite>',
            '/v1/plugins/<plugin>/suites',
            '/v1/plugins/<plugin>/suites/tests/<test>',
            '/v1/jobs/create',
            '/v1/jobs',
            '/v1/jobs/execute/<job_id>',
            '/v1/jobs/<job_id>'
        ]
        for rule in server.app.url_map.iter_rules():
            links.append(str(rule))
        self.assertEqual(set(check_list) & set(links), set(check_list))

    def _resp_to_dict(self, data):
        if type(data) == bytes:
            data = data.decode('utf-8')
        return json.loads(data)

    def test_plugins_no_load_tests(self):
        rv = self.app.get('/v1/plugins').data
        check = {
            'plugins': [{'name': self.plugin.name,
                         'suites': self.plugin.suites,
                         'tests': []}]
        }
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_plugins_load_tests(self):
        rv = self.app.get('/v1/plugins?load_tests=True').data
        check = {
            'plugins': [{'name': self.plugin.name,
                         'suites': self.plugin.suites,
                         'tests': self.plugin.tests}]
        }
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_plugin_not_found(self):
        rv = self.app.get('/v1/plugins/fake2/suites').data
        check = {"message": "Unsupported plugin fake2."}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_plugin_suites(self):
        rv = self.app.get('/v1/plugins/fake/suites').data
        check = {"plugin": {"name": self.plugin.name,
                            "suites": self.plugin.suites}}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_suite_plugin_not_found(self):
        rv = self.app.get(
            '/v1/plugins/fake2/suites/fake/tests').data
        check = {u'message': u'Unsupported plugin fake2.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_suite_tests(self):
        suite = self.plugin.suites[0]
        url = '/v1/plugins/fake/suites/%s/tests' % suite
        rv = self.app.get(url).data
        tests = self.plugin.get_tests_by_suite(suite)
        check = {
            "plugin": {"name": self.plugin.name,
                       "suite": {"name": suite,
                                 "tests": tests}}}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_suite_not_found(self):
        rv = self.app.get(
            '/v1/plugins/fake/suites/fake/tests').data
        check = {u'message': u'Unknown suite fake.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_plugin_tests_not_found(self):
        rv = self.app.get(
            '/v1/plugins/fake2/suites/tests').data
        check = {u'message': u'Unsupported plugin fake2.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_plugin_tests(self):
        rv = self.app.get(
            '/v1/plugins/fake/suites/tests').data
        check = {"plugin": {"name": self.plugin.name,
                            "tests": self.plugin.tests}}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_run_suites(self):
        rv = self.app.post(
            '/v1/plugins/fake/suites').data
        check = {
            u'plugin': {u'name': self.plugin.name,
                        u'report': [self.plugin.test.description]}}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_run_suites_plugin_not_found(self):
        rv = self.app.post(
            '/v1/plugins/fake2/suites').data
        check = {u'message': u'Unsupported plugin fake2.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_run_suite(self):
        suite = self.plugin.suites[0]
        rv = self.app.post(
            '/v1/plugins/fake/suites/%s' % suite).data
        check = {
            u'suite': {u'name': suite,
                       u'report': [self.plugin.test.description]}}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_run_suite_plugin_not_found(self):
        rv = self.app.post(
            '/v1/plugins/fake2/suites/fake_suite').data
        check = {u'message': u'Unsupported plugin fake2.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_run_suite_suite_not_found(self):
        rv = self.app.post(
            '/v1/plugins/fake/suites/fake_suite').data
        check = {u'message': u'Unknown suite fake_suite.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_run_test(self):
        test = self.plugin.tests[0]
        rv = self.app.post(
            '/v1/plugins/fake/suites/tests/%s' % test).data
        self.plugin.test.description['test'] = test
        check = {
            u'plugin': {u'name': self.plugin.name,
                        u'test': test,
                        u'report': [self.plugin.test.description]}}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_run_test_plugin_not_found(self):
        rv = self.app.post(
            '/v1/plugins/fake2/suites/tests/fake_test').data
        check = {u'message': u'Unsupported plugin fake2.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_run_test_not_found(self):
        rv = self.app.post(
            '/v1/plugins/fake/suites/tests/fake_test').data
        check = {u'message': u'Test fake_test not found.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_job_create_json_not_found(self):
        rv = self.app.post(
            '/v1/jobs/create').data
        check = {u'message': u'JSON is missing.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_job_create_job_key_found(self):
        data = {'fake': {}}
        rv = self.app.post(
            '/v1/jobs/create', content_type='application/json',
            data=json.dumps(data)).data
        check = {u'message': u"JSON doesn't have `job` key."}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_job_create_fields_not_found(self):
        data = {'job': {'name': 'fake'}}
        rv = self.app.post(
            '/v1/jobs/create', content_type='application/json',
            data=json.dumps(data)).data
        check = {u'message': u'Fields description,tests are not specified.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_job_create_tests_not_found(self):
        data = {'job': {'name': 'fake',
                        'tests': ['a', 'b'],
                        'description': 'description'}}
        rv = self.app.post(
            '/v1/jobs/create', content_type='application/json',
            data=json.dumps(data)).data
        check = {u'message': u'Tests not found (a,b).'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_job_create(self):
        data = {'job': {'name': 'fake',
                        'tests': self.plugin.tests,
                        'description': 'description'}}
        rv = self.app.post(
            '/v1/jobs/create', content_type='application/json',
            data=json.dumps(data)).data
        check = {u'job': {u'description': u'description',
                 u'id': u'fake_uuid',
                 u'name': u'fake',
                 u'status': u'CREATED',
                 u'tests': self.plugin.tests}}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_execute_job_not_found(self):
        rv = self.app.post('/v1/jobs/execute/fake').data
        check = {u'message': u'Job not found.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_execute_job(self):
        rv = self.app.post('/v1/jobs/execute/%s' % self.job_id).data
        check = {u'job': {u'description': u'description',
                          u'id': self.job_id,
                          u'name': u'fake',
                          u'report': [],
                          u'status': u'IN PROGRESS',
                          u'tests': self.plugin.tests}}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_get_list_jobs(self):
        rv = self.app.get('/v1/jobs').data
        resp_dict = self._resp_to_dict(rv)['jobs']
        check = [
            {u'description': u'description',
             u'id': self.job_id,
             u'name': u'fake',
             u'status': u'CREATED',
             u'tests': self.plugin.tests},
            {u'description': u'description',
             u'id': self.job_id2,
             u'name': u'fake',
             u'status': u'CREATED',
             u'tests': self.plugin.tests}]
        for job in resp_dict:
            self.assertIn(job, check)

    def test_get_job_not_found(self):
        rv = self.app.get('/v1/jobs/fake').data
        check = {u'message': u'Job not found.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_get_job(self):
        rv = self.app.get('/v1/jobs/%s' % self.job_id).data
        check = {'job': {u'description': u'description',
                         u'id': self.job_id,
                         u'name': u'fake',
                         u'status': u'CREATED',
                         u'tests': self.plugin.tests}}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_delete_job_not_found(self):
        rv = self.app.delete('/v1/jobs/fake').data
        check = {u'message': u'Job not found.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def test_delete_job(self):
        before = self._resp_to_dict(
            self.app.get('/v1/jobs').data)
        jobs_id_before = [j['id'] for j in before['jobs']]
        self.assertEqual(len(jobs_id_before), 2)
        self.app.delete('/v1/jobs/%s' % self.job_id)
        after = self._resp_to_dict(
            self.app.get('/v1/jobs').data)
        jobs_id_after = [j['id'] for j in after['jobs']]
        self.assertEqual(len(jobs_id_after), 1)
