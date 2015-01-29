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

import mock

from cloudv_ostf_adapter._adapter_app.db import models

from cloudv_ostf_adapter.tests._base import BaseTestCase


class TestRootController(BaseTestCase):

    def test_tests_get_succeeds(self):
        response = self.app.get("/tests")
        self.assertEqual(response.status_int, 200)

    def test_testsets_get_succeeds(self):
        response = self.app.get("/testsets")
        self.assertEqual(response.status_int, 200)

    def test_testruns_get_succeeds(self):
        response = self.app.get("/testruns")
        self.assertEqual(response.status_int, 200)

    def test_get(self):
        response = self.app.get("/", expect_errors=True)
        self.assertEqual(response.status_int, 404)

    def test_run(self):
        response = self.app.post("/tests/123/run")
        self.assertEqual(response.status_int, 202)

    def test_get_by_id(self):
        response = self.app.get("/tests/123")
        self.assertEqual(response.status_int, 200)

    def test_query(self):
        response = self.app.get("/tests/query?name=somename&group=somegroup")
        self.assertIsNotNone(response)


class TestModels(BaseTestCase):

    def test_get_all_testsets_returns_list(self):
        self.assertIsInstance(models.get_all_tests(), list)

    def test_get_returns_list(self):
        id = mock.Mock()
        assert isinstance(models.get(id), list)
