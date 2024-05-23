"""add time to user_record

Revision ID: 86080e29d660
Revises: a8f899de8563
Create Date: 2024-05-22 17:30:02.132386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision: str = '86080e29d660'
down_revision: Union[str, None] = 'a8f899de8563'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    timestamp = str(datetime.now())
    # timestamp = sa.func.current_timestamp()
    op.add_column('user_record_20_05_2024', sa.Column('time', sa.DateTime(timezone=True), server_default=timestamp))
    # op.alter_column('user_record_20_05_2024', 'time', )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_record_20_05_2024', 'time')
    # ### end Alembic commands ###