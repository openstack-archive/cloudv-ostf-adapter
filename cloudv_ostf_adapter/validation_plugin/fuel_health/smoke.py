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

from cloudv_ostf_adapter.common import cfg
from cloudv_ostf_adapter.validation_plugin import base

GROUP = 'smoke'
CONF = cfg.CONF
TESTS = CONF.get(GROUP).enabled_tests


def get_tests():
    return base.SuiteDescriptor(GROUP, TESTS)
