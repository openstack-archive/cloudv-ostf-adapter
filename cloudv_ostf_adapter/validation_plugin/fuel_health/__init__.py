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

import os

from nose import core

from oslo_utils import importutils

from cloudv_ostf_adapter.common import cfg
from cloudv_ostf_adapter.validation_plugin import base
from cloudv_ostf_adapter.validation_plugin.fuel_health import sanity
from cloudv_ostf_adapter.validation_plugin.fuel_health import smoke
from cloudv_ostf_adapter.validation_plugin.fuel_health import high_availability
from cloudv_ostf_adapter.validation_plugin.fuel_health import platform


CONF = cfg.CONF

SUITES = [
    sanity,
    smoke,
    high_availability,
    platform,
]


class FuelHealthPlugin(base.ValidationPlugin):

    def setup_fuel_health_on_need(self):
        FUEL_HEALTH_CONF = importutils.import_module("fuel_health.config")

        @FUEL_HEALTH_CONF.process_singleton
        class MonkeyPatchFuelHealthConf(object):

            def __init__(self):
                self.register_opts()
                self.compute = cfg.CONF.compute
                self.identity = cfg.CONF.identity
                self.network = cfg.CONF.network
                self.volume = cfg.CONF.volume
                self.murano = cfg.CONF.murano
                self.heat = cfg.CONF.heat
                self.sahara = cfg.CONF.sahara

            def register_opts(self):
                FUEL_HEALTH_CONF.register_compute_opts(CONF)
                FUEL_HEALTH_CONF.register_identity_opts(CONF)
                FUEL_HEALTH_CONF.register_network_opts(CONF)
                FUEL_HEALTH_CONF.register_volume_opts(CONF)
                FUEL_HEALTH_CONF.register_murano_opts(CONF)
                FUEL_HEALTH_CONF.register_heat_opts(CONF)
                FUEL_HEALTH_CONF.register_sahara_opts(CONF)

        FUEL_HEALTH_CONF.FileConfig = MonkeyPatchFuelHealthConf

        MonkeyPatchFuelHealthConf()

    def __init__(self, load_tests=True):
        self.setup_fuel_health_on_need()
        super(FuelHealthPlugin, self).__init__(
            'fuel_health', SUITES, load_tests=load_tests)

    def _get_tests(self):
        try:
            return super(FuelHealthPlugin, self)._get_tests()
        except Exception:
            print("fuel_health is not installed.")

    def run_suites(self):
        test_suites_paths = self.setup_execution(self.tests)
        print(core.TestProgram(
            argv=test_suites_paths).success)

    def setup_execution(self, tests):
        test_suites_paths = self._collect_test(tests)
        test_suites_paths.append(CONF.nose_verbosity)
        os.environ.update(
            {"CUSTOM_FUEL_CONFIG": CONF.health_check_config_path})
        CONF.reload_config_files()
        return test_suites_paths

    def _run_suite(self, suite):
        if ":" in suite:
            raise Exception(
                "%s is a test case, but not test suite." % suite)
        else:
            tests = self.get_tests_by_suite(suite)
            print("Running test suite: %s ..." % suite)
            result = core.TestProgram(
                argv=self.setup_execution(tests), exit=False)
            print(result.success)
        return result
