import cv_ostf_adapter.db

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.testing.schema import Table
from pecan import conf

Base = declarative_base()


def association_table():
    return Table('association', cv_ostf_adapter.db.metadata,
                 sa.Column('xs', sa.Integer, sa.ForeignKey('x.value')),
                 sa.Column('ys', sa.Integer, sa.ForeignKey('y.value')))


class X(Base):
    __tablename__ = 'x'
    value = sa.Column(sa.Integer, primary_key=True)
    ys = relationship('Y', backref="xs")


class Y(Base):
    __tablename__ = 'y'
    value = sa.Column(sa.Integer, primary_key=True)
    xs = relationship('X', backref="ys")


def test_association(x, y):
    import pprint
    pprint.pprint(conf)
    print 'Init db'
    cv_ostf_adapter.db.init_model()
    print 'db start'
    cv_ostf_adapter.db.start()
    print 'metadata create_all'
    cv_ostf_adapter.db.metadata.create_all(cv_ostf_adapter.db.Session.bind)
    print 'db session()'
    s = cv_ostf_adapter.db.Session()
    print '-' * 100
    print 'SESSION:', s
    print '-' * 100

    s.add(X(value=1, ys=Y(value=101)))
    s.add(X(value=2, ys=Y(value=102)))
    s.add(X(value=3, ys=Y(value=103)))

    all_xs = s.query(X).all()
    all_ys = s.query(Y).all()
    all_associations = s.query(association_table).all()

    print '-' * 100
    print 'XS:', all_xs
    print '-' * 100
    print 'YS:', all_ys
    print '-' * 100
    print 'ASSOCIATIONS:', all_associations
    print '-' * 100
