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

from oslo_config import cfg
import pecan

from cloudv_ostf_adapter.storage import engine
from cloudv_ostf_adapter.wsgi import hooks

CONF = cfg.CONF


def setup_config(custom_pecan_config):
    """Updates defaults values for pecan server
    by those supplied via command line arguments
    when ostf-server is started
    """
    config_to_use = {
        'server': {
            'host': CONF.rest.server_host,
            'port': CONF.rest.server_port
        },
        'dbpath': CONF.rest.dbpath,
        'lock_dir': CONF.rest.lock_dir,
        'app': {
            'root': 'cloudv_ostf_adapter.wsgi.root.RootController',
            'modules': ['cloudv_ostf_adapter.wsgi']
        },
    }
    config_to_use.update(custom_pecan_config)
    pecan.conf.update(config_to_use)


def setup_app(config=None, session=None):
    setup_config(config or {})
    session = session or engine.get_session(pecan.conf.dbpath)
    app_hooks = [
        hooks.CustomTransactionalHook(session),
        hooks.AddTokenHook()
    ]
    app = pecan.make_app(
        pecan.conf.app.root,
        force_canonical=True,
        hooks=app_hooks,
    )
    return app
