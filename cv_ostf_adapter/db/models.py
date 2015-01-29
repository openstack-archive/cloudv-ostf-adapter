import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from cv_ostf_adapter import db
from cv_ostf_adapter.utils import generate_uuid


Base = declarative_base()


TESTRUN_FAILED = "FAILED"
TESTRUN_ERRORED = "ERRORED"
TESTRUN_IN_PROGRESS = "IN PROGRESS"
TESTRUN_SUCCEEDED = "SUCCEEDED"
TESTRUN_ABORTED = "ABORTED"
TESTRUN_NOT_STARTED = "NOT STARTED"


class TestRun(Base):
    __tablename__ = "testruns"

    id = sa.Column(sa.String, primary_key=True, default=generate_uuid)
    status = sa.Column(sa.String)
    result = sa.Column(sa.String, nullable=True)
    tests = relationship("tests", backref="tests.id")
    started_at = sa.Column(sa.DateTime, nullable=True)
    finished_at = sa.Column(sa.DateTime, nullable=True)
    pid = sa.Column(sa.Integer)


class TestSet(Base):
    __tablename__ = "testsets"

    id = sa.Column(sa.String, primary_key=True, default=generate_uuid)
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)


class Test(Base):
    __tablename__ = "tests"

    id = sa.Column(sa.String, primary_key=True, default=generate_uuid)
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)
    testsets = relationship("TestSet", backref="tests")


def get_all_tests():
    return db.Session.query(Test).all()


def get(id):
    return [id, id]


def get_all_testsets():
    return []


def get_all_testruns():
    s = db.Session

    return s.query(TestRun).all()