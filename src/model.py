import sqlite3
from datetime import datetime, timezone, timedelta
import sys
from const import CellType, MAP_SIZE, UserRole as ur
from utils import build_path

class DbConnection:
   def connect(self, db_name, db_dir):
      try:
         db_file_path = build_path([db_dir], db_name + '.db', mkdir=True)
         connection = sqlite3.connect(
            db_file_path,
            detect_types=sqlite3.PARSE_DECLTYPES
         )
         cursor = connection.cursor()
         if connection:
            print(f"DataBase connected to {db_name}...OK")

         return cursor, connection
      except Exception as e:
         sys.exit(e)
   
   def __init__(self, db_name, db_dir):
      self.cursor, self.connection = \
      self.connect(db_name, db_dir)
      # self.week.connection.set_trace_callback(print)



def get_last_monday():
   utc = timezone.utc
   now = datetime.now(tz=utc)
   monday = now + timedelta(days=-now.weekday(), weeks=0)
   monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
   return monday

def get_uniq_db_name():
   return get_last_monday().strftime('%d_%m_%Y')

def get_cell_type_str():
   enum_cells = []
   for cell_type in CellType:
      enum_cells.append('{} INT DEFAULT 0'.format(cell_type.name))
   return '{}'.format(','.join(enum_cells))

class Model():
   def create_table_cells(self):
      table_exists = self.week.cursor.execute('''
         SELECT name FROM sqlite_master WHERE type='table' AND name="cells"
      ''').fetchall()

      if table_exists:
         return
      
      try:
         self.week.cursor.execute('BEGIN')

         self.week.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cells(
               x INT, y INT, 
               {},
               UNIQUE(x, y)
            );
         '''.format(self.cell_type_str))

         for i in range(1, MAP_SIZE[0] + 1):
            for j in range(1, MAP_SIZE[1] + 1):
               self.week.cursor.execute('''
                  INSERT INTO cells(x, y) VALUES(?, ?);
               ''', 
                  (i, j)
               )
         self.week.connection.commit()
      except:
         self.week.cursor.execute('ROLLBACK')

   def get_cell_type_counters(self, x, y):
      cell = self.week.cursor.execute(f'''
         select * from cells
         WHERE x == ? AND y == ?
      ''',
         (x, y)
      ).fetchall()

      if cell is not None:
         cell = cell[0]
         return cell[2:]

   def create_table_user_request(self):
      self.week.cursor.execute('''
         CREATE TABLE IF NOT EXISTS user_request(
            user_id INTERGER, 
            x INT, y INT,
            cell_type INT,
            UNIQUE(user_id, x, y) ON CONFLICT REPLACE
         );
      ''')
      
      self.week.connection.commit()

   def create_table_util(self):
      self.week.cursor.execute('''
         CREATE TABLE IF NOT EXISTS util(
            id INT DEFAULT 1, last_scan TIMESTAMP,
            UNIQUE(id)
         );
      ''')      

      self.week.connection.commit()

   def create_table_user_role(self):
      self.const.cursor.execute('''
         CREATE TABLE IF NOT EXISTS user_role(
            user_id INTERGER, role INT,
            UNIQUE(user_id)
         );
      ''')      

      self.week.connection.commit()

   def get_last_scan(self):
      last_scan = self.week.cursor.execute('''
         SELECT last_scan FROM util''',
      ).fetchone()      

      if last_scan is not None:
         return last_scan[0].replace(tzinfo=timezone.utc)
      return None
   
   def set_last_scan(self, last_scan):
      self.week.cursor.execute('''
         INSERT OR REPLACE INTO util(id, last_scan) VALUES(1, ?);
      ''', 
         (last_scan,)
      )

      self.week.connection.commit()

   def update_cell(self, x, y, cell_type, delta, is_commit=True):
      self.week.cursor.execute(f'''
         UPDATE cells set {cell_type.name} = {cell_type.name} {delta:+} 
         WHERE x == ? AND y == ?
      ''',
         (x, y)
      )
      if is_commit:
         self.week.connection.commit()

   def add_user_role(self, user_id, role):
      self.const.cursor.execute(
         '''INSERT OR REPLACE INTO user_role VALUES( ?, ?); ''',
         (user_id, role)
      )
      self.const.connection.commit()
      
      return role       
   
   def delete_user_role(self, user_id):
      self.const.cursor.execute(
         '''DELETE FROM user_role WHERE user_id == ? ''',
         (user_id,)
      )
      self.const.connection.commit()

   def get_user_role(self, user_id):
      role = self.const.cursor.execute(
         '''SELECT role FROM user_role
            WHERE user_id == ?
         ''',
         (user_id,)
      ).fetchone()

      if role is not None:
         role = ur(role[0])
      
      return role            
   
   def get_user_roles(self)  :
      roles = self.const.cursor.execute(
         '''SELECT * FROM user_role''',
      ).fetchall()
      return roles

   def get_user_record(self, user_id, x, y):
      cell_type = self.week.cursor.execute(
         '''SELECT cell_type FROM user_request 
            WHERE user_id == ? AND x == ? AND y == ?
         ''',
         (user_id, x, y)
      ).fetchone()

      if cell_type is not None:
         cell_type = CellType(cell_type[0])
      
      return cell_type

   def get_all_user_record(self, user_id):
      data = self.week.cursor.execute(
         '''SELECT x, y, cell_type FROM user_request 
            WHERE user_id == ? 
            ORDER BY x ASC, y ASC;
         ''',
         (user_id,)
      ).fetchall()

      return data
   
   def get_user_records_by_cell_type(self, user_id, cell_type):
      data = self.week.cursor.execute(
         '''SELECT x, y FROM user_request 
            WHERE user_id == ? AND cell_type == ? 
            ORDER BY x ASC, y ASC;
         ''',
         (user_id, cell_type)
      ).fetchall()

      return data

   def get_users_and_types_by_coords(self, x, y):
      data = self.week.cursor.execute(
         '''SELECT cell_type, user_id FROM user_request 
            WHERE x == ? AND y == ?
            ORDER BY cell_type ASC;
         ''',
         (x, y)
      )

      return data
   
   def update_user_record(self, user_id, x, y, cell_type):
      self.week.cursor.execute('''
         INSERT OR REPLACE INTO user_request VALUES( ?, ?, ?, ? );
      ''', 
         (user_id, x, y, cell_type.value)
      )      

   def delete_user_record(self, user_id, x, y):
      self.week.cursor.execute('''
         DELETE FROM user_request 
         WHERE user_id == ? AND x == ? AND y == ?;
      ''', 
         (user_id, x, y)
      )

   def update_user_record_and_cell(self, user_id, coords, cell_type):
      try:
         self.week.cursor.execute('BEGIN')

         self.update_user_record(user_id, *coords, cell_type)
         self.update_cell(*coords, cell_type, +1, is_commit=False)

         self.week.cursor.execute('COMMIT')

         return True
      except Exception as e:
         self.week.cursor.execute('ROLLBACK')
         print(e)
         return False

   def delete_user_record_and_update_cell(self, user_id, coords, cell_type):
      try:
         self.week.cursor.execute('BEGIN')
         self.delete_user_record(user_id, *coords)
         self.update_cell(*coords, cell_type, -1, is_commit=False)

         self.week.cursor.execute('COMMIT')

         return True
      except Exception as e:
         self.week.cursor.execute('ROLLBACK')
         print(e)
         return False
      
   def delete_user_records(self, user_id):
      coords = self.week.cursor.execute(
         '''SELECT x, y FROM user_request 
            WHERE user_id == ?
         ''',
         (user_id,)
      ).fetchall()      

      for x_y in coords:
         self.delete_user_record(user_id, x_y[0], x_y[1])

   def __init__(self, db_dir, const_db_name, admin_id=None):
      tmp_db_name = get_uniq_db_name()
      self.week = DbConnection(tmp_db_name, db_dir)
      self.const = DbConnection(const_db_name, db_dir)

      self.cell_type_str = get_cell_type_str()
      self.create_table_cells()
      self.create_table_user_request()
      self.create_table_util()
      self.create_table_user_role()
      if admin_id:
         self.add_user_role(admin_id, ur.super_admin)

if __name__ == '__main__':
   model = Model('model')
   model.connection.set_trace_callback(print)

   model.create_table_cells()
   model.create_table_user_request()
   model.add_user_request('shuraken007', 1, 1, 1)
   model.add_user_request('shuraken007', 1, 2, 0)
   print(model.get_cell_values(1, 1))
   # model.delete_user_records('shuraken007')
   model.connection.close()