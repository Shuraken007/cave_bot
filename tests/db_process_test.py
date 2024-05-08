import pytest

from const import CellType as ct, UserRole as ur
from model import Cell, LastScan, UserRecord, UserRole
from db_process import DbProcess
from db_init import Db
from pathlib import Path
from datetime import datetime, timezone, timedelta

@pytest.fixture()
def db_process(tmp_path):
   db = Db(tmp_path, const_db_name='const')
   db_process = DbProcess(db)
   yield db_process

def test_get_cell_type_counters(db_process):
   x, y, idle_reward_counter, demon_head_counter = 3, 4, 5, 2
   with db_process.db.Session() as s:
      cell = Cell(x = x, y = y, idle_reward = idle_reward_counter, demon_head = demon_head_counter)
      s.add(cell)
      s.commit()

   counters = db_process.get_cell_type_counters(x, y)

   expected_counters = [0] * len(ct)
   expected_counters[ct.idle_reward.value] = idle_reward_counter
   expected_counters[ct.demon_head.value] = demon_head_counter

   assert counters == tuple(expected_counters)

@pytest.mark.parametrize("delta", [+1, -1])
def test_update_cell_if_not_set(db_process, delta):
   x, y = 3, 4

   db_process.update_cell(x, y, ct.demon_head, delta)

   with db_process.db.Session() as s:
      cell = s.query(Cell).filter(Cell.x == x, Cell.y == y).one()
      assert cell.demon_head == max(delta, 0)

@pytest.mark.parametrize("delta", [+1, -1])
def test_update_cell_if_set(db_process, delta):
   x, y, counter = 3, 4, 5
   with db_process.db.Session() as s:
      cell = Cell(x = x, y = y, demon_head = counter)
      s.add(cell)
      s.commit()

   db_process.update_cell(x, y, ct.demon_head, delta)

   with db_process.db.Session() as s:
      cell = s.query(Cell).filter(Cell.x == x, Cell.y == y).one()
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

def is_time_anaware(dt):
   return not dt.strftime('%Z') == 'UTC'

def anaware_time_to_aware(dt):
   local_timezone = datetime.now().astimezone().tzinfo
   dt = dt.replace(tzinfo=local_timezone)
   return dt

def test_get_last_scan_if_not_set(db_process):
   last_scan = db_process.get_last_scan()
   assert last_scan is None

def test_get_last_scan(db_process, local_time, global_time, anaware_time):
   for time in [local_time, global_time, anaware_time]:
      with db_process.db.Session() as s:
         last_scan = LastScan(id=1, last_scan = time)
         s.merge(last_scan)
         s.commit()

      last_scan = db_process.get_last_scan()
      if is_time_anaware(time):
         time = anaware_time_to_aware(time)
      assert last_scan == time

def test_set_last_scan(db_process, local_time, global_time, anaware_time):
   for time in [local_time, global_time, anaware_time]:
      db_process.set_last_scan(time)

      with db_process.db.Session() as s:
         last_scan = s.query(LastScan).one()
         if is_time_anaware(time):
            time = anaware_time_to_aware(time)
         assert last_scan.last_scan == time


def test_add_user_role_if_not_set(db_process):
   user_id, expected_role = 9871230948, ur.admin

   db_process.add_user_role(user_id, expected_role)

   with db_process.db.Session() as s:
      user_role = s.query(UserRole).filter(UserRole.id == user_id).one()
      assert user_role.role == expected_role.value

def test_add_user_role_if_set(db_process):
   user_id, set_role = 9871230948, ur.admin
   with db_process.db.Session() as s:
      user_role = UserRole(id = user_id, role = set_role.value)
      s.add(user_role)
      s.commit()

   expected_role = ur.banned
   db_process.add_user_role(user_id, expected_role)

   with db_process.db.Session() as s:
      user_role = s.query(UserRole).filter(UserRole.id == user_id).one()
      assert user_role.role == expected_role.value

def test_delete_user_role_if_not_set(db_process):
   user_id = 9871230948

   db_process.delete_user_role(user_id)

   with db_process.db.Session() as s:
      user_role = s.query(UserRole).filter(UserRole.id == user_id).first()
      assert user_role is None

def test_delete_user_role_if_set(db_process):
   user_id, set_role = 9871230948, ur.admin
   with db_process.db.Session() as s:
      user_role = UserRole(id = user_id, role = set_role.value)
      s.add(user_role)
      s.commit()

   db_process.delete_user_role(user_id)

   with db_process.db.Session() as s:
      user_role = s.query(UserRole).filter(UserRole.id == user_id).first()
      assert user_role is None

def test_get_user_role_if_not_set(db_process):
   user_id = 9871230948
   get_role = db_process.get_user_role(user_id)

   assert get_role is None

def test_get_user_role_if_set(db_process):
   user_id, expected_role = 9871230948, ur.admin
   with db_process.db.Session() as s:
      user_role = UserRole(id = user_id, role = expected_role.value)
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
         user_role = UserRole(id = id, role = set_role.value)
         s.add(user_role)
      s.commit()

   user_roles = db_process.get_user_roles()
   assert len(user_roles) == len(user_roles_config.keys())

   for user_role in user_roles:
      id = user_role.id
      role_val = user_role.role
      assert role_val == user_roles_config[id].value

def test_get_user_record_if_not_set(db_process):
   x, y, user_id = 3, 4, 2879234928

   cell_type = db_process.get_user_record(user_id, x, y)

   assert cell_type is None

def test_get_user_record_if_set(db_process):
   x, y, user_id, expected_cell_type = 3, 4, 2879234928, ct.demon_head
   with db_process.db.Session() as s:
      user_record = UserRecord(
         x = x, y = y, 
         user_id = user_id, cell_type = expected_cell_type.value)
      s.add(user_record)
      s.commit()

   cell_type = db_process.get_user_record(user_id, x, y)

   assert cell_type == expected_cell_type
   

def test_get_all_user_record_if_not_set(db_process):
   user_id =2879234928
   user_records = db_process.get_all_user_record(user_id)

   assert len(user_records) == 0

def test_get_all_user_record_if_set(db_process):
   set_user_id = 239485720
   user_records_config = [
      [3, 4, set_user_id, ct.demon_head],
      [3, 2, set_user_id, ct.demon_tail],
      [2, 2, set_user_id, ct.idle_reward],
      [1, 2, set_user_id, ct.empty],
      [1, 1, set_user_id + 10, ct.summon_stone],
   ]
   expected_user_records_config = [
      [1, 2, set_user_id, ct.empty],
      [2, 2, set_user_id, ct.idle_reward],
      [3, 2, set_user_id, ct.demon_tail],
      [3, 4, set_user_id, ct.demon_head],
   ]
   with db_process.db.Session() as s:
      for config in user_records_config:
         user_record = UserRecord(
            x = config[0],
            y = config[1],
            user_id = config[2],
            cell_type = config[3].value,

         )
         s.add(user_record)
      s.commit()

   user_records = db_process.get_all_user_record(set_user_id)
   assert len(user_records) == len(expected_user_records_config)

   counter = 0
   for user_record in user_records:
      config = expected_user_records_config[counter]

      assert user_record.x == config[0]
      assert user_record.y == config[1]
      assert user_record.user_id == config[2]
      assert user_record.cell_type == config[3].value

      counter += 1

def test_get_user_records_by_cell_type_if_not_set(db_process):
   user_id, cell_type = 2879234928, ct.demon_head
   user_records = db_process.get_user_records_by_cell_type(user_id, cell_type)

   assert len(user_records) == 0

def test_get_user_records_by_cell_type_if_set(db_process):
   request_user_id, request_cell_type = 239485720, ct.summon_stone
   user_records_config = [
      [3, 4, request_user_id, ct.demon_head],
      [3, 2, request_user_id, request_cell_type],
      [2, 2, request_user_id, request_cell_type],
      [1, 2, request_user_id, request_cell_type],
      [1, 1, request_user_id + 10, ct.summon_stone],
   ]
   expected_user_records_config = [
      [1, 2, request_user_id, request_cell_type],
      [2, 2, request_user_id, request_cell_type],
      [3, 2, request_user_id, request_cell_type],
   ]
   with db_process.db.Session() as s:
      for config in user_records_config:
         user_record = UserRecord(
            x = config[0],
            y = config[1],
            user_id = config[2],
            cell_type = config[3].value,
         )
         s.add(user_record)
      s.commit()

   user_records = db_process.get_user_records_by_cell_type(request_user_id, request_cell_type)
   assert len(user_records) == len(expected_user_records_config)

   counter = 0
   for user_record in user_records:
      config = expected_user_records_config[counter]

      assert user_record.x == config[0]
      assert user_record.y == config[1]
      assert user_record.user_id == config[2]
      assert user_record.cell_type == config[3].value

      counter += 1

def test_get_users_and_types_by_coords_if_not_set(db_process):
   x, y = 2,3
   user_records = db_process.get_users_and_types_by_coords(x, y)
   assert len(user_records) == 0

def test_get_users_and_types_by_coords_if_set(db_process):
   user1, user2, user3 = 3495873489, 817238172, 83745834
   x, y = 4, 5
   user_records_config = [
      [x, y, user1, ct.demon_head],
      [x, y, user2, ct.empty],
      [x, y, user3, ct.idle_reward],
      [x+1, y, user1, ct.summon_stone],
      [x, y+1, user2, ct.summon_stone],
   ]
   expected_user_records_config = [
      [ct.empty, user2],
      [ct.demon_head, user1],
      [ct.idle_reward, user3],
   ]
   with db_process.db.Session() as s:
      for config in user_records_config:
         user_record = UserRecord(
            x = config[0],
            y = config[1],
            user_id = config[2],
            cell_type = config[3].value,
         )
         s.add(user_record)
      s.commit()

   user_records = db_process.get_users_and_types_by_coords(x, y)
   assert len(user_records) == len(expected_user_records_config)

   counter = 0
   for cell_type, user_id in user_records:
      config = expected_user_records_config[counter]

      assert cell_type == config[0].value
      assert user_id == config[1]

      counter += 1

def test_update_user_record_if_not_set(db_process):
   x, y, user_id, expected_cell_type = 3, 4, 2879234928, ct.demon_head
   db_process.update_user_record(user_id, x, y, expected_cell_type)

   with db_process.db.Session() as s:
      user_record = s.query(UserRecord).filter(
         UserRecord.x == x, UserRecord.y == y, 
         UserRecord.user_id == user_id).one()
      assert user_record.cell_type == expected_cell_type.value

def test_update_user_record_if_set(db_process):
   x, y, user_id, set_cell_type = 3, 4, 2879234928, ct.demon_head
   expected_cell_type = ct.empty
   with db_process.db.Session() as s:
      user_record = UserRecord(
         x = x, y = y, 
         user_id = user_id, cell_type = set_cell_type.value)
      s.add(user_record)
      s.commit()

   db_process.update_user_record(user_id, x, y, expected_cell_type)

   with db_process.db.Session() as s:
      user_record = s.query(UserRecord).filter(
         UserRecord.x == x, UserRecord.y == y, 
         UserRecord.user_id == user_id).one()
      assert user_record.cell_type == expected_cell_type.value

def test_delete_user_record_if_not_set(db_process):
   x, y, user_id = 3, 4, 2879234928
   db_process.delete_user_record(user_id, x, y)

   with db_process.db.Session() as s:
      user_record = s.query(UserRecord).filter(
         UserRecord.x == x, UserRecord.y == y, 
         UserRecord.user_id == user_id).first()
      assert user_record is None

def test_delete_user_record_if_set(db_process):
   x, y, user_id, set_cell_type = 3, 4, 2879234928, ct.demon_head
   expected_cell_type = ct.empty
   with db_process.db.Session() as s:
      user_record = UserRecord(
         x = x, y = y, 
         user_id = user_id, cell_type = set_cell_type.value)
      s.add(user_record)
      s.commit()

   db_process.delete_user_record(user_id, x, y)

   with db_process.db.Session() as s:
      user_record = s.query(UserRecord).filter(
         UserRecord.x == x, UserRecord.y == y, 
         UserRecord.user_id == user_id).first()
      assert user_record is None

def test_update_user_record_and_cell_if_not_set(db_process):
   x, y, user_id = 3, 4, 2879234928
   user_cell_type_now = ct.empty
   cell_type_now_counter_expected = 1

   db_process.update_user_record_and_cell(user_id, [x, y], user_cell_type_now)

   with db_process.db.Session() as s:
      user_record = s.query(UserRecord).filter(
         UserRecord.x == x, UserRecord.y == y, 
         UserRecord.user_id == user_id).one()
      cell = s.query(Cell).filter(
         Cell.x == x, Cell.y == y).one()
      assert user_record.cell_type == user_cell_type_now.value
      assert cell.empty == cell_type_now_counter_expected

def test_update_user_record_and_cell_if_set(db_process):
   x, y, user_id = 3, 4, 2879234928
   user_cell_type_was = ct.demon_head
   user_cell_type_now = ct.empty
   cell_type_was_counter = 3
   cell_type_was_counter_expected = 3
   cell_type_now_counter_expected = 1

   with db_process.db.Session() as s:
      user_record = UserRecord(
         x = x, y = y,
         user_id = user_id, cell_type = user_cell_type_was.value)
      cell = Cell(x = x, y = y)
      cell.demon_head = cell_type_was_counter
      s.add(cell)
      s.add(user_record)
      s.commit()

   db_process.update_user_record_and_cell(user_id, [x, y], user_cell_type_now)

   with db_process.db.Session() as s:
      user_record = s.query(UserRecord).filter(
         UserRecord.x == x, UserRecord.y == y, 
         UserRecord.user_id == user_id).one()
      cell = s.query(Cell).filter(
         Cell.x == x, Cell.y == y).one()
      assert user_record.cell_type == user_cell_type_now.value
      assert cell.demon_head == cell_type_was_counter_expected
      assert cell.empty == cell_type_now_counter_expected

def test_delete_user_record_and_update_cell_if_not_set(db_process):
   x, y, user_id = 3, 4, 2879234928

   db_process.delete_user_record_and_update_cell(user_id, [x, y], ct.empty)

   with db_process.db.Session() as s:
      user_record = s.query(UserRecord).filter(
         UserRecord.x == x, UserRecord.y == y, 
         UserRecord.user_id == user_id).first()
      cell = s.query(Cell).filter(
         Cell.x == x, Cell.y == y).one()
      assert user_record is None
      assert cell.x == x
      assert cell.y == y
      assert cell.empty == 0

def test_delete_user_record_and_update_cell_if_set(db_process):
   x, y, user_id = 3, 4, 2879234928
   user_cell_type_was = ct.demon_head
   cell_type_was_counter = 3
   cell_type_was_counter_expected = 2

   with db_process.db.Session() as s:
      user_record = UserRecord(
         x = x, y = y,
         user_id = user_id, cell_type = user_cell_type_was.value)
      cell = Cell(x = x, y = y)
      cell.demon_head = cell_type_was_counter
      s.add(cell)
      s.add(user_record)
      s.commit()

   db_process.delete_user_record_and_update_cell(user_id, [x, y], user_cell_type_was)

   with db_process.db.Session() as s:
      user_record = s.query(UserRecord).filter(
         UserRecord.x == x, UserRecord.y == y, 
         UserRecord.user_id == user_id).first()
      cell = s.query(Cell).filter(
         Cell.x == x, Cell.y == y).one()
      assert user_record is None
      assert cell.demon_head == cell_type_was_counter_expected