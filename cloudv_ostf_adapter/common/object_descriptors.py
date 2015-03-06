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

from oslo_utils import importutils


class Test(object):

    def safe_import(self):
        """
        Performs safe import on demand of test class
        """
        try:
            importutils.import_class(self._test_class)
        except ImportError:
            print("Can't import test's class: %s. "
                  "It is not installed." % self._test_class)

    def __init__(self, test_class):
        """
        This class represents seginificant information about test case
        @param test_class: unit test case
        @type test_class: basestring
        """
        self._test_class = test_class
        self._nose_test_name = None
        self._description = {}
        self._suite = None
        self._aproximate_duration = None
        self._actual_duration = None

    @property
    def description(self):
        """
        Extracts docstrings from test
        :rtype: dict
        """
        return {}

    @property
    def suite(self):
        """
        Describes test suite
        :rtype: basestring
        """
        return self._suite

    @property
    def aproximate_duration(self):
        """
        Aproximate test execution duration
        :rtype: basestring
        """
        return self._aproximate_duration

    @property
    def actual_duration(self):
        """
        Actual test execution duration
        """
        raise self._actual_duration

    @actual_duration.setter
    def actual_duration(self, duration):
        self._actual_duration = duration

    @property
    def name(self):
        """
        Returns nose test name
        """
        return self._nose_test_name

    @name.setter
    def name(self, name):
        self._nose_test_name = name


class Suite(object):

    def __init__(self, suite):
        """
        Represents test suite
        @param suite: test suite
        @type suite: basestring
        """
        self.suite = suite
        self._tests = []
        self._description = {}

    @property
    def tests(self):
        """
        Returns all test cases from suite
        :rtype: list of Test
        """
        return self._tests

    @property
    def description(self):
        """
        Returns suite description
        :rtype: dict
        """
        return self._description
