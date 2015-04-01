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
import signal
import sys

import flask

from flask.ext import restful
from oslo_config import cfg

from cloudv_ostf_adapter.common import cfg as config
from cloudv_ostf_adapter import wsgi


CONF = cfg.CONF


app = flask.Flask('cloudv_ostf_adapter')
api = restful.Api(app)

api.add_resource(wsgi.Plugins, '/v1/plugins')
api.add_resource(wsgi.PluginSuite,
                 '/v1/plugins/<plugin>/suites')
api.add_resource(wsgi.PluginTests,
                 '/v1/plugins/<plugin>/suites/tests')
api.add_resource(wsgi.Suites,
                 '/v1/plugins/<plugin>/suites/<suite>',
                 '/v1/plugins/<plugin>/suites/<suite>/tests')
api.add_resource(wsgi.Tests,
                 '/v1/plugins/<plugin>/suites/tests/<test>')

api.add_resource(wsgi.Job,
                 '/v1/jobs/<job_id>')


def main():
    config.parse_args(sys.argv)
    jobs_dir = CONF.rest.jobs_dir
    if not os.path.exists(jobs_dir):
        os.mkdir(jobs_dir)

    host, port = CONF.rest.server_host, CONF.rest.server_port
    try:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        app.run(host=host, port=port,
                debug=CONF.rest.debug,
                use_reloader=True,
                processes=100)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
