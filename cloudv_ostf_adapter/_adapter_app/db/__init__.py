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

from pecan import conf
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

Session = scoped_session(sessionmaker())
metadata = MetaData()


def _engine_from_config(configuration):
    configuration = dict(configuration)
    url = configuration.pop('url')
    return create_engine(url, **configuration)


def init_model():
    conf.sqlalchemy.engine = _engine_from_config(conf.sqlalchemy)


def start():
    Session.bind = conf.sqlalchemy.engine
    metadata.bind = Session.bind


def start_read_only():
    start()


def commit():
    Session.commit()


def rollback():
    Session.rollback()


def clear():
    Session.remove()
