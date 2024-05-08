from datetime import timezone
from const import CellType, MAP_SIZE, UserRole as ur
from model import Cell, UserRecord, LastScan, UserRole

def get_array_of_cell_orm_cell_type_fields():
   arr = []
   for ct in CellType:
      arr.append(getattr(Cell, ct.name))
   return arr

class DbProcess:
   def __init__(self, db):
      self.db = db
      self.cell_query_fields = get_array_of_cell_orm_cell_type_fields()

   def get_cell_type_counters(self, x, y):
      with self.db.Session() as s:
         cell = s.query(*self.cell_query_fields).filter(
            Cell.x == x, Cell.y == y).first()
         if cell is not None:
            return cell

   def update_cell(self, x, y, cell_type, delta, session = None):
      s = session
      if session is None:
         s = self.db.Session()

      cell = s.query(Cell).filter(Cell.x == x, Cell.y == y).first()
      if cell is None:
         cell = Cell(x = x, y = y)
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
         last_scan = s.query(LastScan.last_scan).first()

         if last_scan is not None:
            return last_scan[0]
         return None

   def set_last_scan(self, last_scan):
      with self.db.Session() as s:
         record = LastScan(id = 1, last_scan = last_scan)
         s.merge(record)
         s.commit()

   def add_user_role(self, user_id, role):
      with self.db.Session() as s:
         user_role = UserRole(id = user_id, role = role)
         s.merge(user_role)
         s.commit()

   def delete_user_role(self, user_id):
      with self.db.Session() as s:
         s.query(UserRole).filter(
            UserRole.id == user_id).delete()
         s.commit()

   def get_user_role(self, user_id):
      with self.db.Session() as s:
         user_role = s.query(UserRole).filter(
            UserRole.id == user_id).first()
         if user_role is None:
            return None
         return user_role.role

   def get_user_roles(self):
      with self.db.Session() as s:
         return s.query(UserRole).all()

   def get_user_record(self, user_id, x, y):
      with self.db.Session() as s:
         cell_type = s.query(UserRecord.cell_type).filter(
            UserRecord.x == x, 
            UserRecord.y == y, 
            UserRecord.user_id == user_id
         ).first()
         
         if cell_type is not None:
            cell_type = CellType(cell_type[0])
         
         return cell_type

   def get_all_user_record(self, user_id):
      with self.db.Session() as s:
         return s.query(UserRecord).filter(
            UserRecord.user_id == user_id
         ).order_by(UserRecord.x, UserRecord.y).all()

   def get_user_records_by_cell_type(self, user_id, cell_type):
      with self.db.Session() as s:
         return s.query(UserRecord).filter(
            UserRecord.user_id == user_id,
            UserRecord.cell_type == cell_type.value
         ).order_by(UserRecord.x, UserRecord.y).all()

   def get_users_and_types_by_coords(self, x, y):
      with self.db.Session() as s:
         return s.query(UserRecord.cell_type, UserRecord.user_id).filter(
            UserRecord.x == x,
            UserRecord.y == y
         ).order_by(UserRecord.cell_type).all()

   def update_user_record(self, user_id, x, y, cell_type, session = None):
      s = session
      if s is None:
         s = self.db.Session()

      user_record = UserRecord(
         user_id = user_id, x = x, y = y, cell_type = cell_type)
      s.merge(user_record)

      if session is None:
         s.commit()
         s.close()

   def delete_user_record(self, user_id, x, y, session = None):
      s = session
      if s is None:
         s = self.db.Session()

      user_record = s.query(UserRecord).filter(
         UserRecord.user_id == user_id, 
         UserRecord.x == x, 
         UserRecord.y == y
      ).first()

      if user_record is not None:
         s.delete(user_record)

      if session is None:
         s.commit()
         s.close()

   def update_user_record_and_cell(self, user_id, coords, cell_type):
      with self.db.Session() as s:
         self.update_user_record(user_id, *coords, cell_type, session=s)
         self.update_cell(*coords, cell_type, +1, session=s)
         s.commit()

   def delete_user_record_and_update_cell(self, user_id, coords, cell_type):
      with self.db.Session() as s:
         self.delete_user_record(user_id, *coords, session=s)
         self.update_cell(*coords, cell_type, -1, session=s)
         s.commit()