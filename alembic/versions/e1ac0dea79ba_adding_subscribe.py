"""adding subscribe

Revision ID: e1ac0dea79ba
Revises: b99d7a3e2867
Create Date: 2024-05-31 17:23:13.169631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from cave_bot.const import SERVER_DEFAULT_USER_CONFIG

# revision identifiers, used by Alembic.
revision: str = 'e1ac0dea79ba'
down_revision: Union[str, None] = 'b99d7a3e2867'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    #color_scheme
    op.drop_constraint('color_scheme_pkey', 'color_scheme', type_='primary')
    # op.execute("ALTER TABLE color_scheme ADD COLUMN id SERIAL PRIMARY KEY;")
    op.add_column('color_scheme', sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, cycle=True), nullable=False))
    op.create_primary_key('color_scheme_pkey', 'color_scheme', ['id'])
    op.create_unique_constraint('uniq_1', 'color_scheme', ['user_id', 'name'])

    #user_config
    op.add_column('user_config', sa.Column('subscribe_id', sa.Integer(), nullable=True, server_default=SERVER_DEFAULT_USER_CONFIG['subscribe_id']))
    op.add_column('user_config', sa.Column('is_subscribed', sa.Boolean(), nullable=False, server_default=SERVER_DEFAULT_USER_CONFIG['is_subscribed']))
    op.create_foreign_key('subscribe_fk', 'user_config', 'color_scheme', ['subscribe_id'], ['id'], ondelete = 'SET NULL', onupdate = 'CASCADE')

def downgrade() -> None:
    #user_config
    op.drop_constraint('subscribe_fk', 'user_config', type_='foreignkey')
    op.drop_column('user_config', 'subscribe_id')
    op.drop_column('user_config', 'is_subscribed')

    #color_scheme
    op.drop_constraint('uniq_1', 'color_scheme', type_='unique')
    op.drop_constraint('color_scheme_pkey', 'color_scheme', type_='primary')
    op.drop_column('color_scheme', 'id')
    op.create_primary_key('color_scheme_pkey', 'color_scheme', ['user_id', 'name'])

