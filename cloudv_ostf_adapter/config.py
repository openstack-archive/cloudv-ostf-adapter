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

from oslo_config import cfg


LOG = logging.getLogger(__name__)

adapter_group = cfg.OptGroup(name='rest',
                             title='Cloudvalidation ReST API service options')

adapter_opts = [
    cfg.StrOpt('server_host',
               default='127.0.0.1',
               help="adapter host"),
    cfg.IntOpt('server_port',
               default=8777,
               help="Port number"),
    cfg.StrOpt('dbpath',
               default='mysql://ostf:ostf@localhost/ostf',
               help=""),
    cfg.StrOpt('log_file',
               default='/var/log/ostf.log',
               help=""),
    cfg.StrOpt('lock_dir',
               default='/var/lock',
               help=""),
]


cfg.CONF.register_opts(adapter_opts, group='rest')


DEFAULT_CONFIG_DIR = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), '/etc')

DEFAULT_CONFIG_FILE = "cloudv_ostf_adapter.conf"


def init_config(args=[]):

    config_files = []

    failsafe_path = "/etc/cloudv_ostf_adapter/" + DEFAULT_CONFIG_FILE

    # Environment variables override defaults...
    conf_dir = os.environ.get('CLOUD_VALIDATION_CONFIG_DIR',
                              DEFAULT_CONFIG_DIR)
    conf_file = os.environ.get('CLOUD_VALIDATION_CONFIG', DEFAULT_CONFIG_FILE)

    path = os.path.join(conf_dir, conf_file)

    if not (os.path.isfile(path)
            or 'CLOUD_VALIDATION_CONFIG_DIR' in os.environ
            or 'CLOUD_VALIDATION_CONFIG' in os.environ):
        path = failsafe_path

    if not os.path.exists(path):
        msg = "Config file {0} not found".format(path)
        LOG.warning(msg)
        # No need to fail here! If config doesnot exist defaults are used
    else:
        config_files.append(path)

    cfg.CONF(args,
             project='cloudvalidation',
             default_config_files=config_files)
