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

from flask.ext.restful import reqparse
from flask.ext import restful
from flask.ext.restful import abort
from oslo_config import cfg

from cloudv_ostf_adapter.storage import engine
from cloudv_ostf_adapter.storage import models
from cloudv_ostf_adapter import validation_plugin


CONF = cfg.CONF


class BaseTests(object):
    def __init__(self, *args, **kwargs):
        self.session = engine.get_session(CONF.rest.dbpath)
        self.plugins = []
        for plugin in validation_plugin.VALIDATION_PLUGINS:
            _plugin = plugin(load_tests=True)
            self.plugins.append(_plugin)


class ShowTests(restful.Resource, BaseTests):

    def __init__(self, *args, **kwargs):
        super(ShowTests, self).__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('query',
                                 type=str,
                                 location='args',
                                 required=False)

    def get(self, **kwargs):
        if not self.plugins:
            abort(404, message="There are no plugins.")
        args = self.parser.parse_args()
        tests = []
        query = args.pop('query')
        test_set = kwargs.pop('test_set', None)
        for plugin in self.plugins:
            tests_plugin = plugin.tests
            if query is not None:
                filtered_tests = [t for t in tests_plugin if query in t]
            elif test_set is not None:
                filtered_tests = plugin.get_tests_by_suite(test_set)
            else:
                filtered_tests = tests_plugin
            tests.extend(filtered_tests)
        return {'query': query,
                'test_set': test_set,
                'tests': tests}


class RunTests(restful.Resource, BaseTests):

    def post(self, **kwargs):
        if not self.plugins:
            abort(404, message="There are no plugins.")

        test_set = kwargs.pop('test_set', None)
        result = {}
        for plugin in self.plugins:
            res = models.Task.start(
                self.session,
                plugin,
                test_set,
            )
            result[plugin.name] = res

        return result
