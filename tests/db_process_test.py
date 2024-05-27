import pytest
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta

from cave_bot.const import CellType as ct, UserRole as ur, MapType as mt
from cave_bot.model import generate_models
from cave_bot.db_process import DbProcess
from cave_bot.db_init import Db
from cave_bot.utils import time_to_global_timezone
from cave_bot.config import Config

@pytest.fixture()
def db_process():
   config = Config()

   table_names = {
      'Role': str(uuid.uuid4()),
      'LastScan': str(uuid.uuid4()),
      'Cell': str(uuid.uuid4()),
      'UserRecord': str(uuid.uuid4()),
      'MapConfig': str(uuid.uuid4()),
      'UserConfig': str(uuid.uuid4()),
   }
   models = generate_models(table_names)
   db = Db(models, config.db_connection_str)
   db_process = DbProcess(db)

   yield db_process
   db.drop_tables()

def test_get_cell_type_counters(db_process):
   x, y, map_type, idle_reward_counter, demon_head_counter = 3, 4, mt.normal, 5, 2
   with db_process.db.Session() as s:
      cell = db_process.db.m.Cell(x = x, y = y, map_type = map_type, idle_reward = idle_reward_counter, demon_head = demon_head_counter)
      s.add(cell)
      s.commit()

   counters = db_process.get_cell_type_counters(x, y, map_type)

   expected_counters = [0] * len(ct)
   expected_counters[ct.idle_reward.value] = idle_reward_counter
   expected_counters[ct.demon_head.value] = demon_head_counter

   assert counters == expected_counters

@pytest.mark.parametrize("delta", [+1, -1])
def test_update_cell_if_not_set(db_process, delta):
   x, y, map_type = 3, 4, mt.normal

   db_process.update_cell(x, y, ct.demon_head, map_type, delta)

   with db_process.db.Session() as s:
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x   == x,
         db_process.db.m.Cell.y   == y,
         db_process.db.m.Cell.map_type == map_type
      ).one()
      assert cell.demon_head == max(delta, 0)

@pytest.mark.parametrize("delta", [+1, -1])
def test_update_cell_if_set(db_process, delta):
   x, y, map_type, counter = 3, 4, mt.normal, 5
   with db_process.db.Session() as s:
      cell = db_process.db.m.Cell(x = x, y = y, demon_head = counter, map_type = map_type)
      s.add(cell)
      s.commit()

   db_process.update_cell(x, y, ct.demon_head, map_type, delta)

   with db_process.db.Session() as s:
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x == x, 
         db_process.db.m.Cell.y == y,
         db_process.db.m.Cell.map_type == map_type
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
      db_process.set_last_scan(time)

      last_scan = db_process.get_last_scan()
      time = time_to_global_timezone(time)
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
         last_scan = time_to_global_timezone(last_scan)         
         time = time_to_global_timezone(time)
         # print(last_scan)
         # print(time)
         assert last_scan == time


def test_add_user_role_if_not_set(db_process):
   user_id, expected_role = 9871230948, ur.admin

   db_process.add_user_role(user_id, expected_role)

   with db_process.db.Session() as s:
      user_role = s.query(db_process.db.m.Role).filter(db_process.db.m.Role.id == user_id).one()
      assert user_role.role == expected_role

def test_add_user_role_if_set(db_process):
   user_id, set_role = 9871230948, ur.admin
   with db_process.db.Session() as s:
      user_role = db_process.db.m.Role(id = user_id, role = set_role)
      s.add(user_role)
      s.commit()

   expected_role = ur.banned
   db_process.add_user_role(user_id, expected_role)

   with db_process.db.Session() as s:
      user_role = s.query(db_process.db.m.Role).filter(db_process.db.m.Role.id == user_id).one()
      assert user_role.role == expected_role

def test_delete_user_role_if_not_set(db_process):
   user_id = 9871230948

   db_process.delete_user_role(user_id)

   with db_process.db.Session() as s:
      user_role = s.query(db_process.db.m.Role).filter(db_process.db.m.Role.id == user_id).first()
      assert user_role is None

def test_delete_user_role_if_set(db_process):
   user_id, set_role = 9871230948, ur.admin
   with db_process.db.Session() as s:
      user_role = db_process.db.m.Role(id = user_id, role = set_role)
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
      user_role = db_process.db.m.Role(id = user_id, role = expected_role)
      s.add(user_role)
      s.commit()

   get_role = db_process.get_user_role(user_id)

   assert get_role == expected_role

def test_get_user_roles_if_not_set(db_process):
   roles = db_process.get_user_roles()

   assert len(roles) == 0

def test_get_user_roles_if_set(db_process):
   user_roles_config = {82375293: ur.admin, 38745021: ur.banned}
   with db_process.db.Session() as s:
      for id, set_role in user_roles_config.items():
         user_role = db_process.db.m.Role(id = id, role = set_role)
         s.add(user_role)
      s.commit()

   user_roles = db_process.get_user_roles()
   assert len(user_roles) == len(user_roles_config.keys())

   for user_role in user_roles:
      id = user_role.id
      assert user_role.role == user_roles_config[id]

def test_get_user_record_if_not_set(db_process):
   x, y, user_id, map_type = 3, 4, 2879234928, mt.normal

   cell_type = db_process.get_user_record(user_id, x, y, map_type)

   assert cell_type is None

def test_get_user_record_if_set(db_process):
   x, y, user_id, expected_cell_type, map_type = 3, 4, 2879234928, ct.demon_head, mt.normal
   with db_process.db.Session() as s:
      user_record = db_process.db.m.UserRecord(
         x = x, y = y, 
         user_id = user_id, cell_type = expected_cell_type,
         map_type = map_type
      )
      s.add(user_record)
      s.commit()

   cell_type = db_process.get_user_record(user_id, x, y, map_type)

   assert cell_type == expected_cell_type
   

def test_get_all_user_record_if_not_set(db_process):
   user_id, map_type =2879234928, mt.normal
   user_records = db_process.get_all_user_record(user_id, map_type)

   assert len(user_records) == 0

def test_get_all_user_record_if_set(db_process):
   set_user_id = 239485720
   map_type = mt.normal
   user_records_config = [
      [3, 4, set_user_id, ct.demon_head, map_type],
      [3, 2, set_user_id, ct.demon_tail, map_type],
      [2, 2, set_user_id, ct.idle_reward, map_type],
      [1, 2, set_user_id, ct.empty, map_type],
      [1, 1, set_user_id + 10, ct.summon_stone, mt.hard],
   ]
   expected_user_records_config = [
      [1, 2, set_user_id, ct.empty, map_type],
      [2, 2, set_user_id, ct.idle_reward, map_type],
      [3, 2, set_user_id, ct.demon_tail, map_type],
      [3, 4, set_user_id, ct.demon_head, map_type],
   ]
   with db_process.db.Session() as s:
      for config in user_records_config:
         user_record = db_process.db.m.UserRecord(
            x = config[0],
            y = config[1],
            user_id = config[2],
            cell_type = config[3],
            map_type = config[4],
         )
         s.add(user_record)
      s.commit()

   user_records = db_process.get_all_user_record(set_user_id, map_type)
   assert len(user_records) == len(expected_user_records_config)

   counter = 0
   for user_record in user_records:
      config = expected_user_records_config[counter]

      assert user_record.x == config[0]
      assert user_record.y == config[1]
      assert user_record.user_id == config[2]
      assert user_record.cell_type == config[3]
      assert user_record.map_type == config[4]

      counter += 1

def test_get_user_records_by_cell_type_if_not_set(db_process):
   user_id, cell_type, map_type = 2879234928, ct.demon_head, mt.normal
   user_records = db_process.get_user_records_by_cell_type(user_id, cell_type, map_type)

   assert len(user_records) == 0

def test_get_user_records_by_cell_type_if_set(db_process):
   request_user_id, request_cell_type, map_type = 239485720, ct.summon_stone, mt.normal
   user_records_config = [
      [3, 4, request_user_id, ct.demon_head, map_type],
      [3, 2, request_user_id, request_cell_type, map_type],
      [2, 2, request_user_id, request_cell_type, map_type],
      [1, 2, request_user_id, request_cell_type, map_type],
      [1, 1, request_user_id + 10, ct.summon_stone, map_type],
   ]
   expected_user_records_config = [
      [1, 2, request_user_id, request_cell_type, map_type],
      [2, 2, request_user_id, request_cell_type, map_type],
      [3, 2, request_user_id, request_cell_type, map_type],
   ]
   with db_process.db.Session() as s:
      for config in user_records_config:
         user_record = db_process.db.m.UserRecord(
            x = config[0],
            y = config[1],
            user_id = config[2],
            cell_type = config[3],
            map_type = config[4],
         )
         s.add(user_record)
      s.commit()

   user_records = db_process.get_user_records_by_cell_type(request_user_id, request_cell_type, map_type)
   assert len(user_records) == len(expected_user_records_config)

   counter = 0
   for user_record in user_records:
      config = expected_user_records_config[counter]

      assert user_record.x == config[0]
      assert user_record.y == config[1]
      assert user_record.user_id == config[2]
      assert user_record.cell_type == config[3]
      assert user_record.map_type == config[4]

      counter += 1

def test_get_users_and_types_by_coords_if_not_set(db_process):
   x, y, map_type = 2, 3, mt.normal
   user_records = db_process.get_users_and_types_by_coords(x, y, map_type)
   assert len(user_records) == 0

def test_get_users_and_types_by_coords_if_set(db_process):
   user1, user2, user3 = 3495873489, 817238172, 83745834
   x, y, map_type = 4, 5, mt.normal
   user_records_config = [
      [x, y, user1, ct.demon_head, map_type],
      [x, y, user2, ct.empty, map_type],
      [x, y, user3, ct.idle_reward, map_type],
      [x+1, y, user1, ct.summon_stone, map_type],
      [x, y+1, user2, ct.summon_stone, map_type],
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
            cell_type = config[3],
            map_type       = config[4],
         )
         s.add(user_record)
      s.commit()

   user_records = db_process.get_users_and_types_by_coords(x, y, map_type)
   assert len(user_records) == len(expected_user_records_config)

   counter = 0
   for cell_type, user_id in user_records:
      config = expected_user_records_config[counter]

      assert cell_type == config[0]
      assert user_id == config[1]

      counter += 1

def test_update_user_record_if_not_set(db_process):
   x, y, user_id, expected_cell_type, map_type = 3, 4, 2879234928, ct.demon_head, mt.normal
   db_process.update_user_record(user_id, x, y, expected_cell_type, map_type, datetime.now())

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id,
         db_process.db.m.UserRecord.map_type == map_type,
      ).one()
      assert user_record.cell_type == expected_cell_type

def test_update_user_record_if_set(db_process):
   x, y, user_id, set_cell_type, map_type = 3, 4, 2879234928, ct.demon_head, mt.hard
   expected_cell_type = ct.empty
   with db_process.db.Session() as s:
      user_record = db_process.db.m.UserRecord(
         x = x, y = y, 
         user_id = user_id, 
         cell_type = set_cell_type,
         map_type = map_type,
      )
      s.add(user_record)
      s.commit()

   db_process.update_user_record(user_id, x, y, expected_cell_type, map_type, datetime.now())

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id,
         db_process.db.m.UserRecord.map_type == map_type
      ).one()
      assert user_record.cell_type == expected_cell_type

def test_delete_user_record_if_not_set(db_process):
   x, y, user_id, map_type = 3, 4, 2879234928, mt.normal
   db_process.delete_user_record(user_id, x, y, map_type)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id,
         db_process.db.m.UserRecord.map_type == map_type,
      ).first()
      assert user_record is None

def test_delete_user_record_if_set(db_process):
   x, y, user_id, set_cell_type, map_type = 3, 4, 2879234928, ct.demon_head, mt.normal
   with db_process.db.Session() as s:
      user_record = db_process.db.m.UserRecord(
         x = x, y = y, 
         user_id = user_id, cell_type = set_cell_type,
         map_type = map_type
      )
      s.add(user_record)
      s.commit()

   db_process.delete_user_record(user_id, x, y, map_type)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id,
         db_process.db.m.UserRecord.map_type == map_type,
      ).first()
      assert user_record is None

def test_update_user_record_and_cell_if_not_set(db_process):
   x, y, user_id, map_type = 3, 4, 2879234928, mt.nightmare
   user_cell_type_now = ct.empty
   cell_type_now_counter_expected = 1

   db_process.update_user_record_and_cell(user_id, [x, y], user_cell_type_now, map_type, datetime.now())

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id, 
         db_process.db.m.UserRecord.map_type == map_type,
      ).one()
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x == x, 
         db_process.db.m.Cell.y == y,
         map_type == map_type
      ).one()
      assert user_record.cell_type == user_cell_type_now
      assert cell.empty == cell_type_now_counter_expected
      assert cell.map_type == map_type

def test_update_user_record_and_cell_if_set(db_process):
   x, y, user_id, map_type = 3, 4, 2879234928, mt.hard
   user_cell_type_was = ct.demon_head
   user_cell_type_now = ct.empty
   cell_type_was_counter = 3
   cell_type_was_counter_expected = 3
   cell_type_now_counter_expected = 1

   with db_process.db.Session() as s:
      user_record = db_process.db.m.UserRecord(
         x = x, y = y,
         user_id = user_id, cell_type = user_cell_type_was,
         map_type = map_type
      )
      cell = db_process.db.m.Cell(x = x, y = y, map_type = map_type)
      cell.demon_head = cell_type_was_counter
      s.add(cell)
      s.add(user_record)
      s.commit()

   db_process.update_user_record_and_cell(user_id, [x, y], user_cell_type_now, map_type, datetime.now())

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id, map_type == map_type
      ).one()
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x == x, db_process.db.m.Cell.y == y, map_type == map_type
      ).one()
      assert user_record.cell_type == user_cell_type_now
      assert cell.demon_head == cell_type_was_counter_expected
      assert cell.empty == cell_type_now_counter_expected

def test_delete_user_record_and_update_cell_if_not_set(db_process):
   x, y, user_id, map_type = 3, 4, 2879234928, mt.nightmare

   db_process.delete_user_record_and_update_cell(user_id, [x, y], ct.empty, map_type)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, 
         db_process.db.m.UserRecord.y == y,
         db_process.db.m.UserRecord.user_id == user_id,
         db_process.db.m.UserRecord.map_type == map_type
      ).first()
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x == x, 
         db_process.db.m.Cell.y == y, 
         db_process.db.m.Cell.map_type == map_type
      ).one()
      assert user_record is None
      assert cell.x == x
      assert cell.y == y
      assert cell.empty == 0
      assert cell.map_type == map_type

def test_delete_user_record_and_update_cell_if_set(db_process):
   x, y, user_id, map_type = 3, 4, 2879234928, mt.hard
   user_cell_type_was = ct.demon_head
   cell_type_was_counter = 3
   cell_type_was_counter_expected = 2

   with db_process.db.Session() as s:
      user_record = db_process.db.m.UserRecord(
         x = x, y = y,
         user_id = user_id, cell_type = user_cell_type_was,
         map_type = map_type
      )
      cell = db_process.db.m.Cell(x = x, y = y, map_type = map_type)
      cell.demon_head = cell_type_was_counter
      s.add(cell)
      s.add(user_record)
      s.commit()

   db_process.delete_user_record_and_update_cell(user_id, [x, y], user_cell_type_was, map_type)

   with db_process.db.Session() as s:
      user_record = s.query(db_process.db.m.UserRecord).filter(
         db_process.db.m.UserRecord.x == x, 
         db_process.db.m.UserRecord.y == y, 
         db_process.db.m.UserRecord.user_id == user_id, 
         map_type == map_type,
      ).first()
      cell = s.query(db_process.db.m.Cell).filter(
         db_process.db.m.Cell.x   == x,
         db_process.db.m.Cell.y   == y,
         db_process.db.m.Cell.map_type == map_type
      ).one()
      assert user_record is None
      assert cell.demon_head == cell_type_was_counter_expected

def test_get_user_map_types_unique_if_set(db_process):
   set_user_id = 239485720
   map_type1 = mt.normal
   map_type2 = mt.hard
   user_records_config = [
      [3, 4, set_user_id, ct.demon_head, map_type1],
      [3, 2, set_user_id, ct.demon_tail, map_type1],
      [2, 2, set_user_id, ct.idle_reward, map_type2],
      [1, 2, set_user_id, ct.empty, map_type2],
      [5, 1, set_user_id, ct.empty, map_type2],
      [1, 1, set_user_id + 10, ct.summon_stone, mt.nightmare],
   ]

   expected_map_types = [map_type1, map_type2]

   with db_process.db.Session() as s:
      for config in user_records_config:
         user_record = db_process.db.m.UserRecord(
            x = config[0],
            y = config[1],
            user_id = config[2],
            cell_type = config[3],
            map_type = config[4],
         )
         s.add(user_record)
      s.commit()

   map_types = db_process.get_user_map_types_unique(set_user_id)

   assert len(map_types) == len(expected_map_types)

   counter = 0
   for map_type in map_types:
      assert expected_map_types[counter] == map_type
      counter += 1

def test_get_user_map_types_unique_if_not_set(db_process):
   set_user_id = 239485720
   user_records_config = [
      [1, 1, set_user_id + 10, ct.summon_stone, mt.hard],
   ]

   with db_process.db.Session() as s:
      for config in user_records_config:
         user_record = db_process.db.m.UserRecord(
            x = config[0],
            y = config[1],
            user_id = config[2],
            cell_type = config[3],
            map_type = config[4],
         )
         s.add(user_record)
      s.commit()   

   map_types = db_process.get_user_map_types_unique(set_user_id)
   assert len(map_types) == 0


def test_get_user_config_if_not_set(db_process):
   user_id = 239485720
   user_config = db_process.get_user_config(user_id)
   assert user_config is None

def test_get_user_config_if_set(db_process):
   user_id = 239485720
   map_type = mt.nightmare

   with db_process.db.Session() as s:
      obj = db_process.db.m.UserConfig(id = user_id, map_type = map_type)
      s.add(obj)
      s.commit()
      
   user_config = db_process.get_user_config(user_id)

   assert user_config.id == user_id
   assert user_config.map_type == map_type

def test_set_user_config_if_not_set(db_process):
   user_id = 239485720
   map_type = mt.nightmare
   db_process.set_user_config(user_id, {'map_type': map_type})

   get_user_config = db_process.get_user_config(user_id)

   assert get_user_config.id == user_id
   assert get_user_config.map_type == map_type

def test_set_user_config_if_set(db_process):
   user_id = 239485720
   map_type_was = mt.nightmare
   map_type_new = mt.hard
   db_process.set_user_config(user_id, {'map_type': map_type_was})
   db_process.set_user_config(user_id, {'map_type': map_type_new})

   get_user_config = db_process.get_user_config(user_id)

   assert get_user_config.id == user_id
   assert get_user_config.map_type == map_type_new

def test_delete_user_config_if_not_set(db_process):
   user_id = 4859132
   db_process.delete_user_config(user_id)

   assert db_process.get_user_config(user_id) is None

def test_delete_user_config_if_set(db_process):
   user_id = 239485720
   map_type = mt.nightmare

   db_process.set_user_config(user_id, {'map_type': map_type})
   db_process.delete_user_config(user_id)

   assert db_process.get_user_config(user_id) is None

def test_get_map_max_amount_if_not_set(db_process):
   map_type = mt.normal
   cell_type = ct.idle_reward
   amount = db_process.get_map_max_amount(map_type, cell_type.name)
   assert amount is None

def test_get_map_max_amount_if_set(db_process):
   map_type = mt.normal
   cell_type = ct.idle_reward
   value = 130

   db_process.set_map_max_amount(map_type, cell_type.name, value)
   amount = db_process.get_map_max_amount(map_type, cell_type.name)
   assert amount == value

def test_set_map_max_amount_if_not_set(db_process):
   map_type = mt.normal
   cell_type = ct.idle_reward
   value = 130

   db_process.set_map_max_amount(map_type, cell_type.name, value)
   amount = db_process.get_map_max_amount(map_type, cell_type.name)
   assert amount == value

def test_set_map_max_amount_if_set(db_process):
   map_type = mt.normal
   cell_type = ct.idle_reward
   value = 130
   delta = 10

   db_process.set_map_max_amount(map_type, cell_type.name, value)
   db_process.set_map_max_amount(map_type, cell_type.name, value+delta)
   amount = db_process.get_map_max_amount(map_type, cell_type.name)
   assert amount == value+delta