from .const import CellType
from .utils import time_to_local_timezone

def decorator(f):
   def session_wrap(self, *args, **kwargs):
      if self.is_session_invoked_outer:
         return f(self, *args, **kwargs)
      
      self._start_session()
      result = f(self, *args, **kwargs)
      self._end_session()
   
      return result
   
   return session_wrap

def for_all_methods(decorator, include_with_partial, exclude):
   def decorate(cls):
      for attr in cls.__dict__: # there's propably a better way to do this
         if attr in exclude:
            continue

         is_attr_suit = False
         for part in include_with_partial:
            if part in attr:
               is_attr_suit = True
               break
         
         if is_attr_suit and callable(getattr(cls, attr)):
            setattr(cls, attr, decorator(getattr(cls, attr)))
      return cls
   return decorate

@for_all_methods(decorator, ['cell', 'last_scan', 'user', 'map'], ['get_array_of_cell_orm_cell_type_fields'])
class DbProcess:
   def __init__(self, db):
      self.db = db
      self.cell_query_fields = self.get_array_of_cell_orm_cell_type_fields()

      self.is_session_invoked_outer = False
      self.s = None

   def get_array_of_cell_orm_cell_type_fields(self):
      arr = []
      for ct in CellType:
         arr.append(getattr(self.db.m.Cell, ct.name))
      return arr

   def _start_session(self):
      self.s = self.db.Session()

   def _end_session(self):
      if self.s.new or self.s.dirty or self.s.deleted:
         print('commit')
         self.s.commit()
      self.s.close()

   def start_session(self):
      self._start_session()
      self.is_session_invoked_outer = True

   def end_session(self):
      self._end_session()
      self.is_session_invoked_outer = False

   def get_all_cells(self, map_type):
      return self.s.query(self.db.m.Cell).filter(
         self.db.m.Cell.map_type == map_type
      ).order_by(self.db.m.Cell.x, self.db.m.Cell.y).all()

   def get_cell_type_counters(self, x, y, map_type):
      cell = self.s.query(*self.cell_query_fields).filter(
         self.db.m.Cell.x   == x,
         self.db.m.Cell.y   == y,
         self.db.m.Cell.map_type == map_type
      ).first()
      if cell is not None:
         return cell

   def update_cell(self, x, y, cell_type, map_type, delta):
      cell = self.s.query(self.db.m.Cell).filter(
         self.db.m.Cell.x   == x,
         self.db.m.Cell.y   == y,
         self.db.m.Cell.map_type == map_type,
      ).first()
      if cell is None:
         cell = self.db.m.Cell(x = x, y = y, map_type = map_type)
         setattr(cell, cell_type.name, 0)

      val = getattr(cell, cell_type.name)
      if (val + delta) >= 0:
         val += delta
         setattr(cell, cell_type.name, val)

      self.s.add(cell)

   def get_last_scan(self):
      last_scan_record = self.s.query(self.db.m.LastScan).first()

      if last_scan_record is not None:
         last_scan = last_scan_record.last_scan

         # sqlite database don't works with utc correctly, while postgress works
         # depends on engine dialect+driver
         last_scan = time_to_local_timezone(last_scan)
         return last_scan
      return None

   def set_last_scan(self, last_scan):
      # sqlite database don't works with utc correctly, while postgress works
      # depends on engine dialect+driver
      last_scan = time_to_local_timezone(last_scan)

      record = self.db.m.LastScan(id = 1, last_scan = last_scan)
      self.s.merge(record)

   def add_user_role(self, user_id, role):
      user_role = self.db.m.Role(id = user_id, role = role)
      self.s.merge(user_role)

   def delete_user_role(self, user_id):
      role = self.s.query(self.db.m.Role).filter(
         self.db.m.Role.id == user_id
      ).first()

      if role is not None:
         self.s.delete(role)

   def get_user_role(self, user_id):
      user_role = self.s.query(
         self.db.m.Role
      ).filter(
         self.db.m.Role.id == user_id
      ).first()
      
      if user_role is None:
         return None
      
      return user_role.role

   def get_user_roles(self):
      return self.s.query(self.db.m.Role).all()

   def get_user_record(self, user_id, x, y, map_type):
      cell_type = self.s.query(self.db.m.UserRecord.cell_type).filter(
         self.db.m.UserRecord.x == x, 
         self.db.m.UserRecord.y == y, 
         self.db.m.UserRecord.user_id == user_id,
         self.db.m.UserRecord.map_type == map_type
      ).first()
      
      if cell_type is not None:
         cell_type = cell_type[0]
      
      return cell_type

   def get_all_user_record(self, user_id, map_type):
      return self.s.query(self.db.m.UserRecord).filter(
         self.db.m.UserRecord.user_id == user_id,
         self.db.m.UserRecord.map_type == map_type,
      ).order_by(self.db.m.UserRecord.x, self.db.m.UserRecord.y).all()

   def get_user_records_by_cell_type(self, user_id, cell_type, map_type):
      return self.s.query(self.db.m.UserRecord).filter(
         self.db.m.UserRecord.user_id == user_id,
         self.db.m.UserRecord.cell_type == cell_type,
         self.db.m.UserRecord.map_type == map_type
      ).order_by(self.db.m.UserRecord.x, self.db.m.UserRecord.y).all()

   def get_users_and_types_by_coords(self, x, y, map_type):
      return self.s.query(self.db.m.UserRecord.cell_type, self.db.m.UserRecord.user_id).filter(
         self.db.m.UserRecord.x == x,
         self.db.m.UserRecord.y == y,
         self.db.m.UserRecord.map_type == map_type,
      ).order_by(self.db.m.UserRecord.cell_type).all()

   def update_user_record(self, user_id, x, y, cell_type, map_type):
      user_record = self.db.m.UserRecord(
         user_id = user_id, x = x, y = y, cell_type = cell_type, map_type = map_type)
      self.s.merge(user_record)

   def delete_user_record(self, user_id, x, y, map_type):
      user_record = self.s.query(self.db.m.UserRecord).filter(
         self.db.m.UserRecord.user_id == user_id, 
         self.db.m.UserRecord.x == x, 
         self.db.m.UserRecord.y == y,
         self.db.m.UserRecord.map_type == map_type
      ).first()

      if user_record is not None:
         self.s.delete(user_record)

   def update_user_record_and_cell(self, user_id, coords, cell_type, map_type):
      self.update_user_record(user_id, *coords, cell_type, map_type)
      self.update_cell(*coords, cell_type, map_type, +1)

   def delete_user_record_and_update_cell(self, user_id, coords, cell_type, map_type):
      self.delete_user_record(user_id, *coords, map_type)
      self.update_cell(*coords, cell_type, map_type, -1)

   def get_user_map_types_unique(self, user_id):
      result = self.s.query(
         self.db.m.UserRecord.map_type
      ).filter(
         self.db.m.UserRecord.user_id == user_id, 
      ).group_by(
         self.db.m.UserRecord.map_type
      ).all()

      result = [x[0] for x in result]
      
      return result
         
   def get_user_config(self, user_id):
      return self.s.query(
         self.db.m.UserConfig
      ).filter(
         self.db.m.UserConfig.id == user_id, 
      ).first()
      
   def set_user_config(self, user_id, user_config_dict):
      user_config = self.s.query(
         self.db.m.UserConfig
      ).filter(
         self.db.m.UserConfig.id == user_id
      ).first()
      if user_config is None:
         user_config = self.db.m.UserConfig(id = user_id)
      
      for field, value in user_config_dict.items():
         setattr(user_config, field, value)

      self.s.add(user_config)

   def delete_user_config(self, user_id):
      config = self.s.query(
         self.db.m.UserConfig
      ).filter(
         self.db.m.UserConfig.id == user_id
      ).first()

      if config is not None:
         self.s.delete(config)

   def get_map_max_amount(self, map_type, cell_name):
      amount = self.s.query(
         getattr(self.db.m.MapConfig, cell_name)
      ).filter(
         self.db.m.MapConfig.map_type == map_type
      ).first()

      if amount:
         return amount[0]
      return None
      
   def get_map_max_amount(self, map_type, cell_name):
      amount = self.s.query(
         getattr(self.db.m.MapConfig, cell_name)
      ).filter(
         self.db.m.MapConfig.map_type == map_type
      ).first()

      if amount:
         return amount[0]
      return None
      
   def set_map_max_amount(self, map_type, cell_name, value):
      map_config = self.s.query(self.db.m.MapConfig).filter(
         self.db.m.MapConfig.map_type == map_type,
      ).first()
      if map_config is None:
         map_config = self.db.m.MapConfig(
            map_type = map_type
         )

      setattr(map_config, cell_name, value)   
      self.s.add(map_config)