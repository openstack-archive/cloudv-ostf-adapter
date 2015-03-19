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

from flask.ext import restful
from flask.ext.restful import abort
from flask.ext.restful import reqparse
from oslo_config import cfg

from cloudv_ostf_adapter import validation_plugin


CONF = cfg.CONF


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
