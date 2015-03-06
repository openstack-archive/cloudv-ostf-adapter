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

import logging

from oslo.config import cfg
from pecan import abort
from pecan import expose
from pecan import request
from pecan import rest

from cloudv_ostf_adapter.storage import models
from cloudv_ostf_adapter.validation_plugin import VALIDATION_PLUGINS


LOG = logging.getLogger(__name__)


class BaseRestController(rest.RestController):
    def __init__(self, *args, **kwargs):
        super(BaseRestController, self).__init__(*args, **kwargs)
        self.plugins = []
        for plugin in VALIDATION_PLUGINS:
            _plugin = plugin(load_tests=True)
            self.plugins.append(_plugin)


class TestsController(BaseRestController):
    @expose('json')
    def get(self, *args, **kwargs):
        tests = []
        query = kwargs.pop('query', None)
        for plugin in self.plugins:
            tests_plugin = plugin.tests
            if query is not None:
                tests_plugin = [t for t in tests_plugin if query in t]
            tests.extend(tests_plugin)
        return tests

    @expose('json')
    def get_one(self, test_set):
        tests = []
        for plugin in self.plugins:
            tests_plugin = plugin.get_tests_by_suite(test_set)
            tests.extend(tests_plugin)
        return tests

    @expose('json')
    def post(self, *args):
        args_invalid = not args or len(list(args)) != 2 or not (
            args[0] in cfg.CONF.adapter.test_sets and args[1] == 'run')

        if args_invalid:
            abort(404)

        testset = args[0]
        for plugin in self.plugins:
            res = models.Task.start(
                request.session,
                plugin,
                testset,
            )

        return res
