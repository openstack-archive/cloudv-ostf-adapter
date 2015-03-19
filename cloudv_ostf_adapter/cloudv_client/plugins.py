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


class Plugins(object):

    route = "http://%(host)s:%(port)d/%(api_version)s/plugins"

    def __init__(self, **kwargs):
        self.url = self.route % kwargs

    def list(self, load_tests=True):
        params = {'load_tests': load_tests}
        response = requests.get(self.url, params=params)
        if not response.ok:
            raise exception.exception_mapping.get(response.status_code)()
        resp = json.loads(response.content)
        return resp['plugins']
