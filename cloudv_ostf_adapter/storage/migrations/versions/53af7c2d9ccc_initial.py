# -*- coding: utf-8 -*-

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

"""initial

Revision ID: 53af7c2d9ccc
Revises: None
Create Date: 2013-12-04 13:32:29.109891

"""

# revision identifiers, used by Alembic.
revision = '53af7c2d9ccc'
down_revision = None

from alembic import op
import sqlalchemy as sa

from cloudv_ostf_adapter.storage import constants


def upgrade():
    op.create_table(
        'task',
        sa.Column('uuid', sa.String(36), nullable=False),
        sa.Column('status',
                  sa.Enum(constants.RUNNING,
                          constants.FINISHED, name='task_states'),
                  nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('test_set_id', sa.String(length=128), nullable=True),
        sa.Column('report', sa.Text(), nullable=True),
        sa.Column('result',
                  sa.Enum(constants.FAILED,
                          constants.SUCCEEDED, name='tests_result'),
                  nullable=True),
        sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():
    op.drop_table('task')
