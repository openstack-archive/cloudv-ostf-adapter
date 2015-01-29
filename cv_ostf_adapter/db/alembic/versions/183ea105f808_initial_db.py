"""Initial DB

Revision ID: 183ea105f808
Revises: 

"""

# revision identifiers, used by Alembic.
revision = '183ea105f808'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # TODO: Association tables!
    op.create_table(
        'tests',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('name', sa.String),
        sa.Column('description', sa.String)
        # TODO: association with testsets
    )
    op.create_table(
        'testsets',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('name', sa.String),
        sa.Column('description', sa.String)
        # TODO: association with tests
    )
    op.create_table(
        'testruns',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('status', sa.String),
        sa.Column('result', sa.String, nullable=True)
    )


def downgrade():
    op.drop_table('tests')
    op.drop_table('testsets')
    op.drop_table('testruns')