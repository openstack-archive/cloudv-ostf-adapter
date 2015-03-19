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

import sys

from oslo_config import cfg

from cloudv_ostf_adapter.common import cfg as config
from cloudv_ostf_adapter.cloudv_client import client
from cloudv_ostf_adapter.common import utils
from cloudv_ostf_adapter.cmd import _common as cmd

CONF = cfg.CONF


class ClientV1Shell(object):
    """
    Represents set of capabilities to interact with Cloudvalidation API
    """

    _client = client.Client(CONF.host, CONF.port, CONF.api_version)

    def list_plugins(self):
        """
        List plugins
        """
        resp = self._client.plugins.list(load_tests=False)
        for plugin in resp:
            suites = plugin['suites']
            plugin['suites'] = "\n".join(suites)
            del plugin['tests']
            utils.print_dict(plugin)

    @cmd.args("--validation-plugin-name", dest="validation_plugin_name")
    def list_plugin_suites(self, validation_plugin_name):
        """
        List plugin suites
        Required options:
          --validation-plugin
        """
        resp = self._client.suites.list_suites(validation_plugin_name)
        suites = resp['suites']
        resp['suites'] = "\n".join(suites)
        del resp['name']
        utils.print_dict(resp)

    @cmd.args("--validation-plugin-name", dest="validation_plugin_name")
    def list_plugin_tests(self, validation_plugin_name):
        """
        List plugin tests
        Required options:
          --validation-plugin
        """
        resp = self._client.suites.list_tests_for_suites(
            validation_plugin_name)
        tests = resp['tests']
        resp['tests'] = "\n".join(tests)
        del resp['name']
        utils.print_dict(resp)

    @cmd.args("--validation-plugin-name", dest="validation_plugin_name")
    def run_suites(self, validation_plugin_name):
        """
        Run plugin suites
        Required options:
          --validation-plugin
        """
        resp = self._client.suites.run_suites(validation_plugin_name)
        utils.print_list(resp,
                         ['test', 'duration', 'result', 'report'],
                         obj_is_dict=True)

    @cmd.args("--suite", dest="suite")
    @cmd.args("--validation-plugin-name", dest="validation_plugin_name")
    def run_suite(self, validation_plugin_name, suite):
        """
        Run plugin suite
        Required options:
          --validation-plugin
          --suite
        """
        resp = self._client.suites.run_suite_tests(
            suite, validation_plugin_name)
        suite_test_reports = resp['report']
        utils.print_list(suite_test_reports,
                         ['test', 'duration', 'result', 'report'],
                         obj_is_dict=True)

    @cmd.args("--validation-plugin-name", dest="validation_plugin_name")
    @cmd.args("--test", dest="test")
    def run_test(self, validation_plugin_name, test):
        """
        Run plugin test
        Required options:
          --validation-plugin
          --test
        """
        resp = self._client.tests.run(test, validation_plugin_name)
        utils.print_list(resp,
                         ['test', 'duration', 'result', 'report'],
                         obj_is_dict=True)


CATS = {
    'cloud-health-check': ClientV1Shell
}

category_opt = cfg.SubCommandOpt('category',
                                 title='Command categories',
                                 help='Available categories',
                                 handler=cmd.add_command_parsers(CATS))


def main():
    """Parse options and call the appropriate class/method."""
    cmd._main(CONF, config, category_opt, sys.argv)

if __name__ == "__main__":
    main()
