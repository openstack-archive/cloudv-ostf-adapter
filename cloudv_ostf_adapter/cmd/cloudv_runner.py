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
from cloudv_ostf_adapter.common import utils
from cloudv_ostf_adapter.cmd import _common as cmd

from cloudv_ostf_adapter import validation_plugin

CONF = cfg.CONF


class OSTF(object):
    """
    Represents CLI view for OSTF tests commands:
    - list validation plugins
    - list per-plugin test suites
    """

    def list_plugins(self):
        for plugin in validation_plugin.VALIDATION_PLUGINS:
            _plugin = plugin(load_tests=False)
            descriptor = _plugin.descriptor()
            del descriptor['tests']
            descriptor.update({'suites': "\n".join(descriptor['suites'])})
            utils.print_dict(descriptor)

    @cmd.args("--validation-plugin-name", dest="validation_plugin_name")
    def list_plugin_suites(self, validation_plugin_name):
        for plugin in validation_plugin.VALIDATION_PLUGINS:
            _plugin = plugin(load_tests=False)
            descriptor = _plugin.descriptor()
            if descriptor['name'] == validation_plugin_name:
                utils.print_dict({'suites': "\n".join(descriptor['suites'])})

    @cmd.args("--validation-plugin-name", dest="validation_plugin_name")
    def list_plugin_tests(self, validation_plugin_name):
        for plugin in validation_plugin.VALIDATION_PLUGINS:
            _plugin = plugin(load_tests=False)
            descriptor = _plugin.descriptor()
            if descriptor['name'] == validation_plugin_name:
                utils.print_dict({
                    'tests': "\n".join(plugin().descriptor()['tests'])})

    @cmd.args("--validation-plugin-name", dest="validation_plugin_name")
    def run_suites(self, validation_plugin_name):
        for plugin in validation_plugin.VALIDATION_PLUGINS:
            _plugin = plugin(load_tests=False)
            descriptor = _plugin.descriptor()
            if descriptor['name'] == validation_plugin_name:
                plugin().run_suites()

    @cmd.args("--suite", dest="suite")
    @cmd.args("--validation-plugin-name", dest="validation_plugin_name")
    def run_suite(self, validation_plugin_name, suite):
        for plugin in validation_plugin.VALIDATION_PLUGINS:
            _plugin = plugin(load_tests=False)
            descriptor = _plugin.descriptor()
            if descriptor['name'] == validation_plugin_name:
                plugin().run_suite(suite)

    @cmd.args("--validation-plugin-name", dest="validation_plugin_name")
    @cmd.args("--test", dest="test")
    def run_test(self, validation_plugin_name, test):
        for plugin in validation_plugin.VALIDATION_PLUGINS:
            _plugin = plugin(load_tests=False)
            descriptor = _plugin.descriptor()
            if descriptor['name'] == validation_plugin_name:
                plugin().run_test(test)


CATS = {
    'cloud-health-check': OSTF
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
