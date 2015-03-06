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


import logging
import os
import signal
import sys

from gevent import pywsgi
from oslo_config import cfg

from cloudv_ostf_adapter import config as ostf_config
from cloudv_ostf_adapter import logger
from cloudv_ostf_adapter.wsgi import app


CONF = cfg.CONF


def main():
    ostf_config.init_config(sys.argv[1:])

    logger.setup(log_file=CONF.rest.log_file)

    log = logging.getLogger(__name__)
    log.info('Start app configuration')

    root = app.setup_app({})

    host, port = CONF.rest.server_host, CONF.rest.server_port
    srv = pywsgi.WSGIServer((host, port), root)

    log.info('Starting server in PID %s', os.getpid())
    log.info("serving on http://%s:%s", host, port)

    try:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
