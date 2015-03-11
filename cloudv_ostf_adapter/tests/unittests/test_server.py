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

from mock import patch
import testtools

from cloudv_ostf_adapter import server
from cloudv_ostf_adapter.tests.unittests.fakes.fake_plugin import health_plugin


class TestServer(testtools.TestCase):

    def setUp(self):
        self.plugin = health_plugin.FakeValidationPlugin()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        super(TestServer, self).setUp()

    def test_urlmap(self):
        links = []
        check_list = [
            '/v1/plugins',
            '/v1/plugins/<plugin>/suites/<suite>/tests',
            '/v1/plugins/<plugin>/suites',
            '/static/<path:filename>']
        for rule in server.app.url_map.iter_rules():
            links.append(str(rule))
        self.assertEqual(check_list, links)

    @patch('cloudv_ostf_adapter.wsgi.validation_plugin')
    def test_plugins_no_load_tests(self, mock_plugins):
        mock_plugins.VALIDATION_PLUGINS = [self.plugin.__class__]
        rv = self.app.get('/v1/plugins').data
        check = {
            'plugins': [{'name': self.plugin.name,
                         'suites': self.plugin.suites,
                         'tests': []}]
        }
        self.assertEqual(self._resp_to_dict(rv), check)

    @patch('cloudv_ostf_adapter.wsgi.validation_plugin')
    def test_plugins_load_tests(self, mock_plugins):
        mock_plugins.VALIDATION_PLUGINS = [self.plugin.__class__]
        rv = self.app.get('/v1/plugins?load_tests=True').data
        check = {
            'plugins': [{'name': self.plugin.name,
                         'suites': self.plugin.suites,
                         'tests': self.plugin.tests}]
        }
        self.assertEqual(self._resp_to_dict(rv), check)

    @patch('cloudv_ostf_adapter.wsgi.validation_plugin')
    def test_plugin_not_found(self, mock_plugins):
        mock_plugins.VALIDATION_PLUGINS = [self.plugin.__class__]
        rv = self.app.get('/v1/plugins/fake2/suites').data
        check = {"message": "Unsupported plugin fake2."}
        self.assertEqual(self._resp_to_dict(rv), check)

    @patch('cloudv_ostf_adapter.wsgi.validation_plugin')
    def test_plugin_suites(self, mock_plugins):
        mock_plugins.VALIDATION_PLUGINS = [self.plugin.__class__]
        rv = self.app.get('/v1/plugins/fake/suites').data
        check = {"plugin": {"name": self.plugin.name,
                            "suites": self.plugin.suites}}
        self.assertEqual(self._resp_to_dict(rv), check)

    @patch('cloudv_ostf_adapter.wsgi.validation_plugin')
    def test_suite_plugin_not_found(self, mock_plugins):
        mock_plugins.VALIDATION_PLUGINS = [self.plugin.__class__]
        rv = self.app.get(
            '/v1/plugins/fake2/suites/fake/tests').data
        check = {u'message': u'Unsupported plugin fake2.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    @patch('cloudv_ostf_adapter.wsgi.validation_plugin')
    def est_suite_tests(self, mock_plugins):
        mock_plugins.VALIDATION_PLUGINS = [self.plugin.__class__]
        suite = self. plugin.suites[0]
        url = '/v1/plugins/fake/suites/%s/tests' % suite
        rv = self.app.get(url).data
        tests = self.plugin.get_tests_by_suite(suite)
        check = {
            "plugin": {"name": self.plugin.name,
                       "suite": suite,
                       "tests": tests}}
        self.assertEqual(self._resp_to_dict(rv), check)

    @patch('cloudv_ostf_adapter.wsgi.validation_plugin')
    def test_suite_not_found(self, mock_plugins):
        mock_plugins.VALIDATION_PLUGINS = [self.plugin.__class__]
        rv = self.app.get(
            '/v1/plugins/fake/suites/fake/tests').data
        check = {u'message': u'Unknown suite fake.'}
        self.assertEqual(self._resp_to_dict(rv), check)

    def _resp_to_dict(self, data):
        if type(data) == bytes:
            data = data.decode('utf-8')
        return json.loads(data)
