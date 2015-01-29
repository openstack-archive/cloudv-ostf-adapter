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

from cloudv_ostf_adapter import _adapter_app

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.testing.schema import Table
from pecan import conf

Base = declarative_base()


def association_table():
    return Table('association', _adapter_app.db.metadata,
                 Column('xs', Integer, ForeignKey('x.value')),
                 Column('ys', Integer, ForeignKey('y.value')))


class X(Base):
    __tablename__ = 'x'
    value = Column(Integer, primary_key=True)
    ys = relationship('Y', backref="xs")


class Y(Base):
    __tablename__ = 'y'
    value = Column(Integer, primary_key=True)
    xs = relationship('X', backref="ys")


def test_association(x, y):
    import pprint
    pprint.pprint(conf)
    print('Init db')
    _adapter_app.db.init_model()
    print('db start')
    _adapter_app.db.start()
    print('metadata create_all')
    _adapter_app.db.metadata.create_all(_adapter_app.db.Session.bind)
    print('db session()')
    s = _adapter_app.db.Session()
    print('-' * 100)
    print('SESSION:', s)
    print('-' * 100)

    s.add(X(value=1, ys=Y(value=101)))
    s.add(X(value=2, ys=Y(value=102)))
    s.add(X(value=3, ys=Y(value=103)))

    all_xs = s.query(X).all()
    all_ys = s.query(Y).all()
    all_associations = s.query(association_table).all()

    print('-' * 100)
    print('XS:', all_xs)
    print('-' * 100)
    print('YS:', all_ys)
    print('-' * 100)
    print('ASSOCIATIONS:', all_associations)
    print('-' * 100)
