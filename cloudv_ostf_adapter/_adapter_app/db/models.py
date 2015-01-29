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

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from cloudv_ostf_adapter._adapter_app import db
from cloudv_ostf_adapter._adapter_app.utils import generate_uuid


Base = declarative_base()


TESTRUN_FAILED = "FAILED"
TESTRUN_ERRORED = "ERRORED"
TESTRUN_IN_PROGRESS = "IN PROGRESS"
TESTRUN_SUCCEEDED = "SUCCEEDED"
TESTRUN_ABORTED = "ABORTED"
TESTRUN_NOT_STARTED = "NOT STARTED"


class TestRun(Base):
    __tablename__ = "testruns"

    id = Column(String, primary_key=True, default=generate_uuid)
    status = Column(String)
    result = Column(String, nullable=True)
    tests = relationship("Test", backref=backref("tests.id"))
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    pid = Column(Integer)


class TestSet(Base):
    __tablename__ = "testsets"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    description = Column(String)


class Test(Base):
    __tablename__ = "tests"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    description = Column(String)
    testsets = relationship("TestSet", backref=backref("tests"))


def get_all_tests():
    return db.Session.query(Test).all()


def get(id):
    return [id, id]


def get_all_testsets():
    return []


def get_all_testruns():
    s = db.Session

    return s.query(TestRun).all()
