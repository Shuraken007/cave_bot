import pytest
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta

from cave_bot.const import CellType as ct, UserRole as ur
from cave_bot.model import generate_models
from cave_bot.db_process import DbProcess
from cave_bot.db_init import Db
from cave_bot.utils import time_to_local_timezone
from cave_bot.config import Config

@pytest.fixture()
def db_process():
   config = Config()

   table_names = {
      'Role': str(uuid.uuid4()),
      'LastScan': str(uuid.uuid4()),
      'Cell': str(uuid.uuid4()),
      'UserRecord': str(uuid.uuid4()),
   }
   models = generate_models(table_names)
   db = Db(models, config.db_connection_str)
   db_process = DbProcess(db)

   yield db_process
   db.drop_tables()

def test_get_cell_type_counters(db_process):
   x, y, map_size, idle_reward_counter, demon_head_counter = 3, 4, 20, 5, 2
   with db_process.db.Session() as s:
      cell = db_process.db.m.Cell(x = x, y = y, map_size = map_size, idle_reward = idle_reward_counter, demon_head = demon_head_counter)
      s.add(cell)
      s.commit()

   counters = db_process.get_cell_type_counters(x, y, map_size)

   expected_counters = [0] * len(ct)
   expected_counters[ct.idle_reward.value] = idle_reward_counter
   expected_counters[ct.demon_head.value] = demon_head_counter

   assert counters == tuple(expected_counters)

@pytest.mark.parametrize("delta", [+1, -1])
def test_update_cell_if_not_set(db_process, delta):
   x, y, map_size = 3, 4, 20

   db_process.update_cell(x, y, ct.demon_head, map_size, delta)

   with db_process.db.Session() as s:
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x   == x,
         db_process.db.m.Cell.y   == y,
         db_process.db.m.Cell.map_size == map_size
      ).one()
      assert cell.demon_head == max(delta, 0)

@pytest.mark.parametrize("delta", [+1, -1])
def test_update_cell_if_set(db_process, delta):
   x, y, map_size, counter = 3, 4, 20, 5
   with db_process.db.Session() as s:
      cell = db_process.db.m.Cell(x = x, y = y, demon_head = counter, map_size = map_size)
      s.add(cell)
      s.commit()

   db_process.update_cell(x, y, ct.demon_head, map_size, delta)

   with db_process.db.Session() as s:
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x == x, 
         db_process.db.m.Cell.y == y,
         db_process.db.m.Cell.map_size == map_size
      ).one()
      assert cell.demon_head == counter + delta

@pytest.fixture()
def local_time():
   offset = timedelta(hours=3)
   local_utc = timezone(offset)
   return datetime.now(tz=local_utc)

@pytest.fixture()
def global_time():
   global_utc = timezone.utc
   return datetime.now(tz=global_utc)

@pytest.fixture()
def anaware_time():
   return datetime.now()

def test_get_last_scan_if_not_set(db_process):
   last_scan = db_process.get_last_scan()
   assert last_scan is None


def test_get_last_scan(db_process, local_time, anaware_time):
   # global_time test have not sence, should be set via set_last_scan to have effect
   for time in [local_time, anaware_time]:
      with db_process.db.Session() as s:
         last_scan = db_process.db.m.LastScan(id=1, last_scan = time)
         s.merge(last_scan)
         s.commit()

      last_scan = db_process.get_last_scan()
      time = time_to_local_timezone(time)
      # print(last_scan)
      # print(time)
      assert last_scan == time

def test_set_last_scan(db_process, local_time, global_time, anaware_time):
   for time in [local_time, global_time, anaware_time]:
      db_process.set_last_scan(time)

      with db_process.db.Session() as s:
         last_scan_record = s.query(db_process.db.m.LastScan).one()
         last_scan = last_scan_record.last_scan

         # sqlite return anaware, while postgres - aware
         last_scan = time_to_local_timezone(last_scan)         
         time = time_to_local_timezone(time)
         # print(last_scan)
         # print(time)
         assert last_scan == time


def test_add_user_role_if_not_set(db_process):
   user_id, expected_role = 9871230948, ur.admin

   db_process.add_user_role(user_id, expected_role)

   with db_process.db.Session() as s:
      user_role = s.query(db_process.db.m.Role).filter(db_process.db.m.Role.id == user_id).one()
      assert user_role.role == expected_role.value

def test_add_user_role_if_set(db_process):
   user_id, set_role = 9871230948, ur.admin
   with db_process.db.Session() as s:
      user_role = db_process.db.m.Role(id = user_id, role = set_role.value)
      s.add(user_role)
      s.commit()

   expected_role = ur.banned
   db_process.add_user_role(user_id, expected_role)

   with db_process.db.Session() as s:
      user_role = s.query(db_process.db.m.Role).filter(db_process.db.m.Role.id == user_id).one()
      assert user_role.role == expected_role.value

def test_delete_user_role_if_not_set(db_process):
   user_id = 9871230948

   db_process.delete_user_role(user_id)

   with db_process.db.Session() as s:
      user_role = s.query(db_process.db.m.Role).filter(db_process.db.m.Role.id == user_id).first()
      assert user_role is None

def test_delete_user_role_if_set(db_process):
   user_id, set_role = 9871230948, ur.admin
   with db_process.db.Session() as s:
      user_role = db_process.db.m.Role(id = user_id, role = set_role.value)
      s.add(user_role)
      s.commit()

   db_process.delete_user_role(user_id)

   with db_process.db.Session() as s:
      user_role = s.query(db_process.db.m.Role).filter(db_process.db.m.Role.id == user_id).first()
      assert user_role is None

def test_get_user_role_if_not_set(db_process):
   user_id = 9871230948
   get_role = db_process.get_user_role(user_id)

   assert get_role is None

def test_get_user_role_if_set(db_process):
   user_id, expected_role = 9871230948, ur.admin
   with db_process.db.Session() as s:
      user_role = db_process.db.m.Role(id = user_id, role = expected_role.value)
      s.add(user_role)
      s.commit()

   get_role = db_process.get_user_role(user_id)

   assert get_role == expected_role.value

def test_get_user_roles_if_not_set(db_process):
   roles = db_process.get_user_roles()

   assert len(roles) == 0

def test_get_user_roles_if_set(db_process):
   user_roles_config = {82375293: ur.admin, 38745021: ur.banned}
   with db_process.db.Session() as s:
      for id, set_role in user_roles_config.items():
         user_role = db_process.db.m.Role(id = id, role = set_role.value)
         s.add(user_role)
      s.commit()

   user_roles = db_process.get_user_roles()
   assert len(user_roles) == len(user_roles_config.keys())

   for user_role in user_roles:
      id = user_role.id
      role_val = user_role.role
      assert role_val == user_roles_config[id].value

def test_get_user_record_if_not_set(db_process):
   x, y, user_id, map_size = 3, 4, 2879234928, 20

   cell_type = db_process.get_user_record(user_id, x, y, map_size)

   assert cell_type is None

def test_get_user_record_if_set(db_process):
   x, y, user_id, expected_cell_type, map_size = 3, 4, 2879234928, ct.demon_head, 20
   with db_process.db.Session() as s:
      user_record = db_process.db.m.UserRecord(
         x = x, y = y, 
         user_id = user_id, cell_type = expected_cell_type.value,
         map_size = map_size
      )
      s.add(user_record)
      s.commit()

   cell_type = db_process.get_user_record(user_id, x, y, map_size)

   assert cell_type == expected_cell_type
   

def test_get_all_user_record_if_not_set(db_process):
   user_id, map_size =2879234928, 20
   user_records = db_process.get_all_user_record(user_id, map_size)

   assert len(user_records) == 0

def test_get_all_user_record_if_set(db_process):
   set_user_id = 239485720
   map_size = 20
   user_records_config = [
      [3, 4, set_user_id, ct.demon_head, map_size],
      [3, 2, set_user_id, ct.demon_tail, map_size],
      [2, 2, set_user_id, ct.idle_reward, map_size],
      [1, 2, set_user_id, ct.empty, map_size],
      [1, 1, set_user_id + 10, ct.summon_stone, map_size+5],
   ]
   expected_user_records_config = [
      [1, 2, set_user_id, ct.empty, map_size],
      [2, 2, set_user_id, ct.idle_reward, map_size],
      [3, 2, set_user_id, ct.demon_tail, map_size],
      [3, 4, set_user_id, ct.demon_head, map_size],
   ]
   with db_process.db.Session() as s:
      for config in user_records_config:
         user_record = db_process.db.m.UserRecord(
            x = config[0],
            y = config[1],
            user_id = config[2],
            cell_type = config[3].value,
            map_size = config[4],
         )
         s.add(user_record)
      s.commit()

   user_records = db_process.get_all_user_record(set_user_id, map_size)
   assert len(user_records) == len(expected_user_records_config)

   counter = 0
   for user_record in user_records:
      config = expected_user_records_config[counter]

      assert user_record.x == config[0]
      assert user_record.y == config[1]
      assert user_record.user_id == config[2]
      assert user_record.cell_type == config[3].value
      assert user_record.map_size == config[4]

      counter += 1

def test_get_user_records_by_cell_type_if_not_set(db_process):
   user_id, cell_type, map_size = 2879234928, ct.demon_head, 20
   user_records = db_process.get_user_records_by_cell_type(user_id, cell_type, map_size)

   assert len(user_records) == 0

def test_get_user_records_by_cell_type_if_set(db_process):
   request_user_id, request_cell_type, map_size = 239485720, ct.summon_stone, 20
   user_records_config = [
      [3, 4, request_user_id, ct.demon_head, map_size],
      [3, 2, request_user_id, request_cell_type, map_size],
      [2, 2, request_user_id, request_cell_type, map_size],
      [1, 2, request_user_id, request_cell_type, map_size],
      [1, 1, request_user_id + 10, ct.summon_stone, map_size],
   ]
   expected_user_records_config = [
      [1, 2, request_user_id, request_cell_type, map_size],
      [2, 2, request_user_id, request_cell_type, map_size],
      [3, 2, request_user_id, request_cell_type, map_size],
   ]
   with db_process.db.Session() as s:
      for config in user_records_config:
         user_record = db_process.db.m.UserRecord(
            x = config[0],
            y = config[1],
            user_id = config[2],
            cell_type = config[3].value,
            map_size = config[4],
         )
         s.add(user_record)
      s.commit()

   user_records = db_process.get_user_records_by_cell_type(request_user_id, request_cell_type, map_size)
   assert len(user_records) == len(expected_user_records_config)

   counter = 0
   for user_record in user_records:
      config = expected_user_records_config[counter]

      assert user_record.x == config[0]
      assert user_record.y == config[1]
      assert user_record.user_id == config[2]
      assert user_record.cell_type == config[3].value
      assert user_record.map_size == config[4]

      counter += 1

def test_get_users_and_types_by_coords_if_not_set(db_process):
   x, y, map_size = 2, 3, 20
   user_records = db_process.get_users_and_types_by_coords(x, y, map_size)
   assert len(user_records) == 0

def test_get_users_and_types_by_coords_if_set(db_process):
   user1, user2, user3 = 3495873489, 817238172, 83745834
   x, y, map_size = 4, 5, 20
   user_records_config = [
      [x, y, user1, ct.demon_head, map_size],
      [x, y, user2, ct.empty, map_size],
      [x, y, user3, ct.idle_reward, map_size],
      [x+1, y, user1, ct.summon_stone, map_size],
      [x, y+1, user2, ct.summon_stone, map_size],
   ]
   expected_user_records_config = [
      [ct.empty, user2],
      [ct.demon_head, user1],
      [ct.idle_reward, user3],
   ]
   with db_process.db.Session() as s:
      for config in user_records_config:
         user_record = db_process.db.m.UserRecord(
            x         = config[0],
            y         = config[1],
            user_id   = config[2],
            cell_type = config[3].value,
            map_size       = config[4],
         )
         s.add(user_record)
      s.commit()

   user_records = db_process.get_users_and_types_by_coords(x, y, map_size)
   assert len(user_records) == len(expected_user_records_config)

   counter = 0
   for cell_type, user_id in user_records:
      config = expected_user_records_config[counter]

      assert cell_type == config[0].value
      assert user_id == config[1]

      counter += 1

def test_update_user_record_if_not_set(db_process):
   x, y, user_id, expected_cell_type, map_size = 3, 4, 2879234928, ct.demon_head, 20
   db_process.update_user_record(user_id, x, y, expected_cell_type, map_size)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id,
         db_process.db.m.UserRecord.map_size == map_size,
      ).one()
      assert user_record.cell_type == expected_cell_type.value

def test_update_user_record_if_set(db_process):
   x, y, user_id, set_cell_type, map_size = 3, 4, 2879234928, ct.demon_head, 56
   expected_cell_type = ct.empty
   with db_process.db.Session() as s:
      user_record = db_process.db.m.UserRecord(
         x = x, y = y, 
         user_id = user_id, 
         cell_type = set_cell_type.value,
         map_size = map_size,
      )
      s.add(user_record)
      s.commit()

   db_process.update_user_record(user_id, x, y, expected_cell_type, map_size)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id,
         db_process.db.m.UserRecord.map_size == map_size
      ).one()
      assert user_record.cell_type == expected_cell_type.value

def test_delete_user_record_if_not_set(db_process):
   x, y, user_id, map_size = 3, 4, 2879234928, 20
   db_process.delete_user_record(user_id, x, y, map_size)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id,
         db_process.db.m.UserRecord.map_size == map_size,
      ).first()
      assert user_record is None

def test_delete_user_record_if_set(db_process):
   x, y, user_id, set_cell_type, map_size = 3, 4, 2879234928, ct.demon_head, 20
   with db_process.db.Session() as s:
      user_record = db_process.db.m.UserRecord(
         x = x, y = y, 
         user_id = user_id, cell_type = set_cell_type.value,
         map_size = map_size
      )
      s.add(user_record)
      s.commit()

   db_process.delete_user_record(user_id, x, y, map_size)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id,
         db_process.db.m.UserRecord.map_size == map_size,
      ).first()
      assert user_record is None

def test_update_user_record_and_cell_if_not_set(db_process):
   x, y, user_id, map_size = 3, 4, 2879234928, 30
   user_cell_type_now = ct.empty
   cell_type_now_counter_expected = 1

   db_process.update_user_record_and_cell(user_id, [x, y], user_cell_type_now, map_size)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id, 
         db_process.db.m.UserRecord.map_size == map_size,
      ).one()
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x == x, 
         db_process.db.m.Cell.y == y,
         map_size == map_size
      ).one()
      assert user_record.cell_type == user_cell_type_now.value
      assert cell.empty == cell_type_now_counter_expected
      assert cell.map_size == map_size

def test_update_user_record_and_cell_if_set(db_process):
   x, y, user_id, map_size = 3, 4, 2879234928, 55
   user_cell_type_was = ct.demon_head
   user_cell_type_now = ct.empty
   cell_type_was_counter = 3
   cell_type_was_counter_expected = 3
   cell_type_now_counter_expected = 1

   with db_process.db.Session() as s:
      user_record = db_process.db.m.UserRecord(
         x = x, y = y,
         user_id = user_id, cell_type = user_cell_type_was.value,
         map_size = map_size
      )
      cell = db_process.db.m.Cell(x = x, y = y, map_size = map_size)
      cell.demon_head = cell_type_was_counter
      s.add(cell)
      s.add(user_record)
      s.commit()

   db_process.update_user_record_and_cell(user_id, [x, y], user_cell_type_now, map_size)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id, map_size == map_size
      ).one()
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x == x, db_process.db.m.Cell.y == y, map_size == map_size
      ).one()
      assert user_record.cell_type == user_cell_type_now.value
      assert cell.demon_head == cell_type_was_counter_expected
      assert cell.empty == cell_type_now_counter_expected

def test_delete_user_record_and_update_cell_if_not_set(db_process):
   x, y, user_id, map_size = 3, 4, 2879234928, 42

   db_process.delete_user_record_and_update_cell(user_id, [x, y], ct.empty, map_size)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, 
         db_process.db.m.UserRecord.y == y,
         db_process.db.m.UserRecord.user_id == user_id,
         db_process.db.m.UserRecord.map_size == map_size
      ).first()
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x == x, 
         db_process.db.m.Cell.y == y, 
         db_process.db.m.Cell.map_size == map_size
      ).one()
      assert user_record is None
      assert cell.x == x
      assert cell.y == y
      assert cell.empty == 0
      assert cell.map_size == map_size

def test_delete_user_record_and_update_cell_if_set(db_process):
   x, y, user_id, map_size = 3, 4, 2879234928, 47
   user_cell_type_was = ct.demon_head
   cell_type_was_counter = 3
   cell_type_was_counter_expected = 2

   with db_process.db.Session() as s:
      user_record = db_process.db.m.UserRecord(
         x = x, y = y,
         user_id = user_id, cell_type = user_cell_type_was.value,
         map_size = map_size
      )
      cell = db_process.db.m.Cell(x = x, y = y, map_size = map_size)
      cell.demon_head = cell_type_was_counter
      s.add(cell)
      s.add(user_record)
      s.commit()

   db_process.delete_user_record_and_update_cell(user_id, [x, y], user_cell_type_was, map_size)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, 
         db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id, 
         map_size == map_size,
      ).first()
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x   == x,
         db_process.db.m.Cell.y   == y,
         db_process.db.m.Cell.map_size == map_size
      ).one()
      assert user_record is None
      assert cell.demon_head == cell_type_was_counter_expected