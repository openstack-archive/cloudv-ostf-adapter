#    Copyright 2015 Mirantis, Inc
#
#    Licensed under the Apache License, Version 3.0 (the "License"); you may
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

import mock
from oslo_config import cfg
import testtools

from cloudv_ostf_adapter.cmd import server
from cloudv_ostf_adapter.tests.unittests.fakes.fake_plugin import health_plugin
from cloudv_ostf_adapter import wsgi


CONF = cfg.CONF


class TestServer(testtools.TestCase):

    def setUp(self):
        self.plugin = health_plugin.FakeValidationPlugin()
        CONF.rest.jobs_dir = '/var/log/tmp_ostf'
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        self.actual_plugins = wsgi.validation_plugin.VALIDATION_PLUGINS
        wsgi.validation_plugin.VALIDATION_PLUGINS = [self.plugin.__class__]
        p = mock.patch('cloudv_ostf_adapter.wsgi.BaseTests.run_tests')
        self.addCleanup(p.stop)
        m = p.start()
        m.return_value = 'fake_job'
        super(TestServer, self).setUp()

    def tearDown(self):
        wsgi.validation_plugin.VALIDATION_PLUGINS = self.actual_plugins
        super(TestServer, self).tearDown()

    def test_urlmap(self):
        links = []
        check_list = [
            '/v1/plugins',
            '/v1/plugins/<plugin>/suites/tests/<test>',
            '/v1/plugins/<plugin>/suites/<suite>/tests',
            '/v1/plugins/<plugin>/suites/tests',
            '/v1/plugins/<plugin>/suites/<suite>',
            '/v1/plugins/<plugin>/suites'
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
                        u'job_id': u'fake_job'}}
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
                       u'job_id': u'fake_job'}}
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
                        u'job_id': u'fake_job'}}
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
