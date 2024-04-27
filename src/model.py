import sqlite3
from datetime import datetime, timezone, timedelta
import sys
from const import CellType, MAP_SIZE
from utils import build_path

def get_last_monday():
   utc = timezone.utc
   now = datetime.now(tz=utc)
   monday = now + timedelta(days=-now.weekday(), weeks=0)
   monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
   return monday

def get_uniq_db_name():
   return get_last_monday().strftime('%d_%m_%Y.db')

def get_cell_type_str():
   enum_cells = []
   for cell_type in CellType:
      enum_cells.append('{} INT DEFAULT 0'.format(cell_type.name))
   return '{}'.format(','.join(enum_cells))

class Model():
   def connect(self):
      db_name = get_uniq_db_name()
      try:
         db_file_path = build_path(['db'], db_name, mkdir=True)
         connection = sqlite3.connect(
            db_file_path,
            detect_types=sqlite3.PARSE_DECLTYPES
         )
         cursor = connection.cursor()
         if connection:
            print(f"DataBase connected to {db_name}...OK")

         return connection, cursor
      except Exception as e:
         sys.exit(e)

   def create_table_cells(self):
      table_exists = self.cursor.execute('''
         SELECT name FROM sqlite_master WHERE type='table' AND name="cells"
      ''').fetchall()

      if table_exists:
         return
      
      try:
         self.cursor.execute('BEGIN')

         self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cells(x INT, y INT, {})
         '''.format(self.cell_type_str))

         for i in range(1, MAP_SIZE[0] + 1):
            for j in range(1, MAP_SIZE[1] + 1):
               self.cursor.execute('''
                  INSERT INTO cells(x, y) VALUES(?, ?);
               ''', 
                  (i, j)
               )
         self.connection.commit()
      except:
         self.cursor.execute('ROLLBACK')

   def get_cell_type_counters(self, x, y):
      cell = self.cursor.execute(f'''
         select * from cells
         WHERE x == ? AND y == ?
      ''',
         (x, y)
      ).fetchall()

      if cell is not None:
         cell = cell[0]
         return cell[2:]

   def create_table_user_request(self):
      self.cursor.execute('''
         CREATE TABLE IF NOT EXISTS user_request(
            user_id TEXT, 
            x INT, y INT,
            cell_type INT,
            UNIQUE(user_id, x, y) ON CONFLICT REPLACE
         );
      ''')
      
      self.connection.commit()

   def create_table_util(self):
      self.cursor.execute('''
         CREATE TABLE IF NOT EXISTS util(
            id INT DEFAULT 1, last_scan TIMESTAMP,
            UNIQUE(id)
         );
      ''')      

      self.connection.commit()

   def get_last_scan(self):
      last_scan = self.cursor.execute('''
         SELECT last_scan FROM util''',
      ).fetchone()      

      if last_scan is not None:
         return last_scan[0].replace(tzinfo=timezone.utc)
      return None
   
   def set_last_scan(self, last_scan):
      self.cursor.execute('''
         INSERT OR REPLACE INTO util(id, last_scan) VALUES(1, ?);
      ''', 
         (last_scan,)
      )

      self.connection.commit()

   def update_cell(self, x, y, cell_type, delta):
      self.cursor.execute(f'''
         UPDATE cells set {cell_type.name} = {cell_type.name} {delta:+} 
         WHERE x == ? AND y == ?
      ''',
         (x, y)
      )

   def get_user_record(self, user_id, x, y):
      cell_type = self.cursor.execute(
         '''SELECT cell_type FROM user_request 
            WHERE user_id == ? AND x == ? AND y == ?
         ''',
         (user_id, x, y)
      ).fetchone()

      if cell_type is not None:
         cell_type = CellType(cell_type[0])
      
      return cell_type

   def update_user_record(self, user_id, x, y, cell_type):
      self.cursor.execute('''
         INSERT OR REPLACE INTO user_request VALUES( ?, ?, ?, ? );
      ''', 
         (user_id, x, y, cell_type.value)
      )      

   def delete_user_record(self, user_id, x, y):
      self.cursor.execute('''
         DELETE FROM user_request 
         WHERE user_id == ? AND x == ? AND y == ?;
      ''', 
         (user_id, x, y)
      )

   def update_user_record_and_cell(self, user_id, coords, cell_type):
      try:
         self.cursor.execute('BEGIN')

         self.update_user_record(user_id, *coords, cell_type)
         self.update_cell(*coords, cell_type, +1)

         self.cursor.execute('COMMIT')

         return True
      except Exception as e:
         self.cursor.execute('ROLLBACK')
         print(e)
         return False

   def delete_user_record_and_update_cell(self, user_id, coords, cell_type):
      try:
         self.cursor.execute('BEGIN')
         self.delete_user_record(user_id, *coords)
         self.update_cell(*coords, cell_type, -1)

         self.cursor.execute('COMMIT')

         return True
      except Exception as e:
         self.cursor.execute('ROLLBACK')
         print(e)
         return False
      
   def delete_user_records(self, user_id):
      coords = self.cursor.execute(
         '''SELECT x, y FROM user_request 
            WHERE user_id == ?
         ''',
         (user_id,)
      ).fetchall()      

      for x_y in coords:
         self.delete_user_record(user_id, x_y[0], x_y[1])

   def __init__(self, db_dir):
      self.db_dir = db_dir
      self.connection, self.cursor = self.connect()
      self.cell_type_str = get_cell_type_str()
      self.create_table_cells()
      self.create_table_user_request()
      self.create_table_util()
      # self.connection.set_trace_callback(print)

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