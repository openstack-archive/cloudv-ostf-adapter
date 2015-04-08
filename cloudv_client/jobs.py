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


class Jobs(object):

    _jobs_create_route = ("http://%(host)s:%(port)d/%(api_version)s"
                          "/jobs/create")
    _jobs_route = ("http://%(host)s:%(port)d/%(api_version)s/jobs")
    _jobs_execute_route = ("http://%(host)s:%(port)d/%(api_version)s"
                           "/jobs/execute/%(job_id)s")

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def list(self):
        jobs_url = self._jobs_route % self.kwargs
        response = requests.get(jobs_url)
        if not response.ok:
            raise exception.exception_mapping.get(response.status_code)()
        return json.loads(response.content)['jobs']

    def create(self, name, description, tests):
        data = {'job': {'name': name,
                        'description': description,
                        'tests': tests}}
        jobs_url = self._jobs_create_route % self.kwargs
        headers = {'Content-Type': 'application/json'}
        response = requests.post(jobs_url,
                                 headers=headers,
                                 data=json.dumps(data))
        if not response.ok:
            raise exception.exception_mapping.get(response.status_code)()
        return json.loads(response.content)['job']

    def get(self, job_id):
        jobs_url = self._jobs_route % self.kwargs
        jobs_url += '/%s' % job_id
        response = requests.get(jobs_url)
        if not response.ok:
            raise exception.exception_mapping.get(response.status_code)()
        return json.loads(response.content)['job']

    def delete(self, job_id):
        jobs_url = self._jobs_route % self.kwargs
        jobs_url += '/%s' % job_id
        response = requests.delete(jobs_url)
        if not response.ok:
            raise exception.exception_mapping.get(response.status_code)()

    def execute(self, job_id):
        self.kwargs.update({'job_id': job_id})
        jobs_url = self._jobs_execute_route % self.kwargs
        response = requests.post(jobs_url)
        if not response.ok:
            raise exception.exception_mapping.get(response.status_code)()
        return json.loads(response.content)['job']
