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

try:
    import simplejson as json
except ImportError:
    import json

import requests

from cloudv_ostf_adapter.common import exception


class Suites(object):

    _suite_route = ("http://%(host)s:%(port)d/%(api_version)s"
                    "/plugins/%(plugin)s/suites")
    _suite_test_route = ("http://%(host)s:%(port)d/%(api_version)s/"
                         "plugins/%(plugin)s/suites/%(suite)s/tests")
    _test_route = ("http://%(host)s:%(port)d/%(api_version)s/"
                   "plugins/%(plugin)s/suites/tests")

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def list_suites(self, plugin):
        self.kwargs.update({"plugin": plugin})
        suite_url = self._suite_route % self.kwargs
        response = requests.get(suite_url)
        if not response.ok:
            raise exception.exception_mapping.get(response.status_code)()
        return json.loads(response.content)['plugin']

    def list_tests_for_suites(self, plugin):
        self.kwargs.update({"plugin": plugin})
        suite_url = self._test_route % self.kwargs
        response = requests.get(suite_url)
        if not response.ok:
            raise exception.exception_mapping.get(response.status_code)()
        return json.loads(response.content)['plugin']

    def run_suites(self, plugin):
        self.kwargs.update({"plugin": plugin})
        suite_url = self._suite_route % self.kwargs
        response = requests.post(suite_url, {})
        if not response.ok:
            raise exception.exception_mapping.get(response.status_code)()
        return json.loads(response.content)['plugin']['report']

    def run_suite_tests(self, suite, plugin):
        self.kwargs.update({"suite": suite})
        self.kwargs.update({"plugin": plugin})
        url = self._suite_test_route % self.kwargs
        response = requests.post(url, {})
        if not response.ok:
            raise exception.exception_mapping.get(response.status_code)()
        return json.loads(response.content)['suite']
