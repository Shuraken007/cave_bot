from .const import CellType
from .utils import time_to_local_timezone
import sqlalchemy as sa

class DbProcess:
   def __init__(self, db):
      self.db = db
      self.cell_query_fields = self.get_array_of_cell_orm_cell_type_fields()

   def get_array_of_cell_orm_cell_type_fields(self):
      arr = []
      for ct in CellType:
         arr.append(getattr(self.db.m.Cell, ct.name))
      return arr

   def get_cell_type_counters(self, x, y, map_type):
      with self.db.Session() as s:
         cell = s.query(*self.cell_query_fields).filter(
            self.db.m.Cell.x   == x,
            self.db.m.Cell.y   == y,
            self.db.m.Cell.map_type == map_type
         ).first()
         if cell is not None:
            return cell

   def update_cell(self, x, y, cell_type, map_type, delta, session = None):
      s = session
      if session is None:
         s = self.db.Session()

      cell = s.query(self.db.m.Cell).filter(
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
         
      s.add(cell)

      if session is None:
         s.commit()
         s.close()

   def get_last_scan(self):
      with self.db.Session() as s:
         last_scan_record = s.query(self.db.m.LastScan).first()

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

      with self.db.Session() as s:
         record = self.db.m.LastScan(id = 1, last_scan = last_scan)
         s.merge(record)
         s.commit()

   def add_user_role(self, user_id, role):
      with self.db.Session() as s:
         user_role = self.db.m.Role(id = user_id, role = role)
         s.merge(user_role)
         s.commit()

   def delete_user_role(self, user_id):
      with self.db.Session() as s:
         s.query(self.db.m.Role).filter(
            self.db.m.Role.id == user_id).delete()
         s.commit()

   def get_user_role(self, user_id):
      with self.db.Session() as s:
         user_role = s.query(self.db.m.Role).filter(
            self.db.m.Role.id == user_id).first()
         if user_role is None:
            return None
         return user_role.role

   def get_user_roles(self):
      with self.db.Session() as s:
         return s.query(self.db.m.Role).all()

   def get_user_record(self, user_id, x, y, map_type):
      with self.db.Session() as s:
         cell_type = s.query(self.db.m.UserRecord.cell_type).filter(
            self.db.m.UserRecord.x == x, 
            self.db.m.UserRecord.y == y, 
            self.db.m.UserRecord.user_id == user_id,
            self.db.m.UserRecord.map_type == map_type
         ).first()
         
         if cell_type is not None:
            cell_type = cell_type[0]
         
         return cell_type

   def get_all_user_record(self, user_id, map_type):
      with self.db.Session() as s:
         return s.query(self.db.m.UserRecord).filter(
            self.db.m.UserRecord.user_id == user_id,
            self.db.m.UserRecord.map_type == map_type,
         ).order_by(self.db.m.UserRecord.x, self.db.m.UserRecord.y).all()

   def get_user_records_by_cell_type(self, user_id, cell_type, map_type):
      with self.db.Session() as s:
         return s.query(self.db.m.UserRecord).filter(
            self.db.m.UserRecord.user_id == user_id,
            self.db.m.UserRecord.cell_type == cell_type,
            self.db.m.UserRecord.map_type == map_type
         ).order_by(self.db.m.UserRecord.x, self.db.m.UserRecord.y).all()

   def get_users_and_types_by_coords(self, x, y, map_type):
      with self.db.Session() as s:
         return s.query(self.db.m.UserRecord.cell_type, self.db.m.UserRecord.user_id).filter(
            self.db.m.UserRecord.x == x,
            self.db.m.UserRecord.y == y,
            self.db.m.UserRecord.map_type == map_type,
         ).order_by(self.db.m.UserRecord.cell_type).all()

   def update_user_record(self, user_id, x, y, cell_type, map_type, session = None):
      s = session
      if s is None:
         s = self.db.Session()

      user_record = self.db.m.UserRecord(
         user_id = user_id, x = x, y = y, cell_type = cell_type, map_type = map_type)
      s.merge(user_record)

      if session is None:
         s.commit()
         s.close()

   def delete_user_record(self, user_id, x, y, map_type, session = None):
      s = session
      if s is None:
         s = self.db.Session()

      user_record = s.query(self.db.m.UserRecord).filter(
         self.db.m.UserRecord.user_id == user_id, 
         self.db.m.UserRecord.x == x, 
         self.db.m.UserRecord.y == y,
         self.db.m.UserRecord.map_type == map_type
      ).first()

      if user_record is not None:
         s.delete(user_record)

      if session is None:
         s.commit()
         s.close()

   def update_user_record_and_cell(self, user_id, coords, cell_type, map_type):
      with self.db.Session() as s:
         self.update_user_record(user_id, *coords, cell_type, map_type, session=s)
         self.update_cell(*coords, cell_type, map_type, +1, session=s)
         s.commit()

   def delete_user_record_and_update_cell(self, user_id, coords, cell_type, map_type):
      with self.db.Session() as s:
         self.delete_user_record(user_id, *coords, map_type, session=s)
         self.update_cell(*coords, cell_type, map_type, -1, session=s)
         s.commit()

   def get_user_map_types_unique(self, user_id):
      with self.db.Session() as s:
         result = s.query(
            self.db.m.UserRecord.map_type
         ).filter(
            self.db.m.UserRecord.user_id == user_id, 
         ).group_by(
            self.db.m.UserRecord.map_type
         ).all()

         result = [x[0] for x in result]
         if len(result) == 0:
            result = None
         
         return result
         
   def get_user_config(self, user_id):
      with self.db.Session() as s:
         return s.query(
            self.db.m.UserConfig
         ).filter(
            self.db.m.UserConfig.id == user_id, 
         ).first()
      
   def set_user_config(self, user_config_dict):
      with self.db.Session() as s:
         user_config = self.db.m.UserConfig(**user_config_dict)
         s.merge(user_config)
         s.commit()

   def delete_user_config(self, user_id):
      with self.db.Session() as s:
         s.query(
            self.db.m.UserConfig
         ).filter(
            self.db.m.UserConfig.id == user_id
         ).delete()
         s.commit()