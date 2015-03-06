#    Copyright 2015 Mirantis, Inc.
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

import datetime
import multiprocessing
import uuid

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from cloudv_ostf_adapter.storage import constants


BASE = declarative_base()


def run_proc(func, *args):
    proc = multiprocessing.Process(
        target=func,
        args=args)
    proc.daemon = True
    proc.start()
    return proc


class Task(BASE):

    __tablename__ = 'task'

    TEST_STATES = (
        constants.RUNNING,
        constants.FINISHED
    )

    TEST_RESULTS = (
        constants.FAILED,
        constants.SUCCEEDED
    )

    id = sa.Column(sa.String(128),
                   default=lambda: str(uuid.uuid4()), primary_key=True)
    status = sa.Column(sa.Enum(*TEST_STATES, name='task_states'),
                       nullable=False)
    result = sa.Column(sa.Enum(*TEST_RESULTS, name='tests_result'))
    started_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    ended_at = sa.Column(sa.DateTime)
    report = sa.Column(sa.Text)

    test_set_id = sa.Column(sa.String(128), nullable=False)

    @classmethod
    def update_status(cls, session, task_uuid, result,
                      status='wait_running'):
        res = constants.SUCCEEDED if result.success else constants.FAILED
        task = session.query(cls).filter(cls.id == task_uuid)
        task.update({'status': status,
                     'ended_at': datetime.datetime.utcnow(),
                     'result': res},
                    synchronize_session=False)

    @property
    def view(self):
        def format_date(date):
            if date is None:
                return date
            return date.strftime('%Y-%m-%d %H:%M')
        test_run_data = {
            'id': self.id,
            'test_set': self.test_set_id,
            'status': self.status,
            'started_at': format_date(self.started_at),
            'ended_at': format_date(self.ended_at),
            'result': self.result,
            'report': self.report,
        }
        return test_run_data

    @classmethod
    def start(cls, session, plugin, test_set):
            test_run = cls(test_set_id=test_set, status=constants.RUNNING)
            test_run.session = session
            session.add(test_run)

            # flush test_run data to db
            session.commit()

            run_proc(
                plugin.run_suite,
                test_set,
                test_run.id)

            return test_run.view
