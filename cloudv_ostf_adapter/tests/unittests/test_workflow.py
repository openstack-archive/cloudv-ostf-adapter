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

import testtools

from cloudv_ostf_adapter import validation_plugin
from cloudv_ostf_adapter.tests.unittests.fakes.fake_plugin import health_plugin


class TestWorkflow(testtools.TestCase):

    def setUp(self):
        self.plugin = health_plugin.FakeValidationPlugin()
        validation_plugin.VALIDATION_PLUGINS.append(self.plugin.__class__)
        super(TestWorkflow, self).setUp()

    def tearDown(self):
        validation_plugin.VALIDATION_PLUGINS.pop(
            validation_plugin.VALIDATION_PLUGINS.index(
                self.plugin.__class__))
        super(TestWorkflow, self).tearDown()

    def test_verify_plugins(self):
        self.assertEqual(2, len(validation_plugin.VALIDATION_PLUGINS))
        self.assertIn(self.plugin.__class__,
                      validation_plugin.VALIDATION_PLUGINS)

    def test_verify_fake_plugin(self):
        test_patsh = self.plugin._collect_test(self.plugin.tests)
        self.assertEqual(2, len(test_patsh))
        self.assertEqual(2, len(self.plugin.tests))
