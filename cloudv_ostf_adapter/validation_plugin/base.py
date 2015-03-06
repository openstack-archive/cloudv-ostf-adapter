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
import sys

from oslo_utils import importutils

from cloudv_ostf_adapter.common import utils
from cloudv_ostf_adapter.nose_plugin import discovery
from cloudv_ostf_adapter.storage import engine
from cloudv_ostf_adapter.storage import models


class SuiteDescriptor(object):

    suite_attrs = ['test_group', 'tests']
    test_attrs = ['tests']

    def __init__(self, test_group_definition, tests):
        """
        Describes test specific test group
        @param test_group_definition: Test group definition
                                      (i.e. sanity, smoke, HA, platform)
        @type test_group_definition: basestring
        @param tests: list of tests per test group
        @type tests: list
        """
        self.test_group = test_group_definition
        self.tests = tests

    def print_tests_description(self):
        utils.print_list(self, self.test_attrs)

    def print_description(self):
        utils.print_dict(self)


class ValidationPlugin(object):

    test_executor = "%(test_module_path)s:%(class)s.%(test)s"

    def __init__(self, name, suites, load_tests=True):
        __suites = []
        for suite in suites:
            __suites.extend(suite.TESTS)

        self.name = name
        self.suites = __suites
        self._suites = suites
        self.tests = (self._get_tests()
                      if load_tests else [])

    def _get_tests(self):
        """
        Test collector
        """
        tests = []
        for suite in self._suites:
            _tests = discovery.do_test_discovery(
                suite.TESTS)
            tests.extend(_tests)
        return tests

    def _collect_test(self, tests):
        test_suites_paths = []
        for test in tests:
            classpath, test_method = test.split(":")
            classname = classpath.split(".")[-1]
            module = importutils.import_class(
                classpath).__module__
            test_module_path = os.path.abspath(
                sys.modules[module].__file__)
            if test_module_path.endswith("pyc"):
                test_module_path = test_module_path[:-1]
            test_suites_paths.append(
                self.test_executor %
                {
                    'test_module_path': test_module_path,
                    'class': classname,
                    'test': test_method
                })
        return test_suites_paths

    def get_tests_by_suite(self, suite):
        tests = []
        for test in self.tests:
            if suite in test:
                tests.append(test)
        return tests

    def descriptor(self):
        """
        Returns Plugin descriptor that contains:
         - plugin name
         - plugin suites
         - plugin tests
        """
        return {
            "name": self.name,
            "suites": self.suites,
            "tests": self.tests,
        }

    def run_suites(self):
        """
        Runs all tests from all suites
        """
        raise Exception("Plugin doesn't support suites execution.")

    def _run_suite(self, suite):
        """
        Runs specific suite
        """
        raise Exception("Plugin doesn't support suite execution.")

    def run_suite(self, suite, db_test=None, dbpath=None):
        result = self._run_suite(suite)
        if db_test is not None:
            self.store_result_to_db(db_test, dbpath, result)

    def store_result_to_db(self, db_test, dbpath, result):
        with engine.contexted_session(dbpath) as session:
            models.Task.update_status(session, db_test, result, 'finished')

    def run_test(self, test):
        """
        Runs specific test
        """
        raise Exception("Plugin doesn't support test execution.")
