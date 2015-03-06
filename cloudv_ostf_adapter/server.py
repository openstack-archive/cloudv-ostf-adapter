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


import signal
import sys

import flask
from flask.ext import restful
from oslo_config import cfg

from cloudv_ostf_adapter.common import cfg as config
from cloudv_ostf_adapter.wsgi import ShowTests
from cloudv_ostf_adapter.wsgi import RunTests


CONF = cfg.CONF


def main():
    config.parse_args(sys.argv)

    host, port = CONF.rest.server_host, CONF.rest.server_port
    app = flask.Flask('cloudvalidation-server')
    api = restful.Api(app)
    api.add_resource(ShowTests,
                     '/v1/tests',
                     '/v1/tests/<test_set>')
    api.add_resource(RunTests,
                     '/v1/tests/<test_set>/run')

    try:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        app.run(host=host, port=port, debug=CONF.rest.debug)
    except KeyboardInterrupt:
        pass
