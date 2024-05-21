import pytest
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta

from cave_bot.const import CellType as ct, UserRole as ur
from cave_bot.model import generate_models
from cave_bot.db_process import DbProcess
from cave_bot.db_init import Db
from cave_bot.utils import get_mock_class_with_attr
from cave_bot.bot.bot_util import init_ctx
from cave_bot.config import Config
from cave_bot.controller import Controller

config = Config()

@pytest.fixture()
def role():

   table_names = {
      'Role': str(uuid.uuid4()),
      'LastScan': str(uuid.uuid4()),
      'Cell': str(uuid.uuid4()),
      'UserRecord': str(uuid.uuid4()),
      'UserConfig': str(uuid.uuid4()),
      'MapConfig': str(uuid.uuid4()),
   }
   models = generate_models(table_names)
   db = Db(models, config.db_connection_str, admin_id = config.admin_id)
   db_process = DbProcess(db)
   controller = Controller(db_process)
   yield controller.role
   db.drop_tables()

def get_bot(map_id_to_name):
   class MockBot:
      async def get_user_name_by_id(self, user_id):
         return map_id_to_name[user_id]
   return MockBot()

def get_user(user_id, name):
   return get_mock_class_with_attr({ 'id': int(user_id), 'name': name })

def get_ctx(user = None):
   if user is None:
      user = get_user(config.admin_id, 'I_am_super_admin')

   mock_ctx = get_mock_class_with_attr({
      'message': get_mock_class_with_attr({
         'author': user
      })
   })
   init_ctx(mock_ctx)

   return mock_ctx

def test_add_user_role(role):
   ctx = get_ctx()

   user = get_user(12654798, 'somebody')
   user_role = ur.admin

   role.add(user, user_role, ctx)
   assert role.db_process.get_user_role(user.id) == user_role