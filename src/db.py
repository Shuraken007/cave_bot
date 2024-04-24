import sqlite3
from datetime import datetime, timezone, timedelta
import sys
from const import FieldType as ft, MAP_SIZE
from pathlib import Path
import os

def get_last_monday():
   utc = timezone.utc
   now = datetime.now(tz=utc)
   monday = now + timedelta(days=-now.weekday(), weeks=0)
   monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
   return monday

def get_uniq_db_name():
   return get_last_monday().strftime('%d_%m_%Y.db')

def get_field_type_str():
   enum_fields = []
   for e in ft:
      enum_fields.append('{} INT DEFAULT 0'.format(e.name))
   return '{}'.format(','.join(enum_fields))

class Db():
   def connect(self):
      db_name = get_uniq_db_name()
      try:
         db_dir_path = os.path.join(os.path.dirname( __file__ ), '..', self.db_dir)
         Path(db_dir_path).mkdir(parents=True, exist_ok=True)
         db_file_path = os.path.join(db_dir_path, db_name)

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

   def create_table_fields(self):
      table_exists = self.cursor.execute('''
         SELECT name FROM sqlite_master WHERE type='table' AND name="fields"
      ''').fetchall()

      if table_exists:
         return
      
      try:
         self.cursor.execute('BEGIN')

         self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fields(x INT, y INT, {})
         '''.format(self.field_type_str))

         for i in range(1, MAP_SIZE[0] + 1):
            for j in range(1, MAP_SIZE[1] + 1):
               self.cursor.execute('''
                  INSERT INTO fields(x, y) VALUES(?, ?);
               ''', 
                  (i, j)
               )
         self.connection.commit()
      except:
         self.cursor.execute('ROLLBACK')

   def get_field_by_coords(self, x, y):
      field = self.cursor.execute(f'''
         select * from fields
         WHERE x == ? AND y == ?
      ''',
         (x, y)
      ).fetchall()

      if field is not None:
         field = field[0]
         return field[2:]

   def create_table_user_request(self):
      self.cursor.execute('''
         CREATE TABLE IF NOT EXISTS user_request(
            user_id TEXT, 
            x INT, y INT,
            field_type INT,
            UNIQUE(x, y) ON CONFLICT REPLACE
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

   def change_field_value(self, x, y, field, delta):
      self.cursor.execute(f'''
         UPDATE fields set {field} = {field} {delta:+} 
         WHERE x == ? AND y == ?
      ''',
         (x, y)
      )

   def add_user_request(self, user_id, x, y, field_type):
      field_name = ft(field_type).name

      field_type_added = self.cursor.execute(
         '''SELECT field_type FROM user_request 
            WHERE user_id == ? AND x == ? AND y == ?
         ''',
         (user_id, x, y)
      ).fetchone()

      if field_type_added is not None:
         field_type_added = field_type_added[0]

      if field_type_added is not None and field_type_added == field_type:
         return False
      
      try:
         self.cursor.execute('BEGIN')

         if field_type_added is not None:
            field_name_added = ft(field_type_added).name
            self.change_field_value(x, y, field_name_added, -1)

         self.cursor.execute('''
            INSERT OR REPLACE INTO user_request VALUES( ?, ?, ?, ? );
         ''', 
            (user_id, x, y, field_type)
         )
         self.change_field_value(x, y, field_name, +1)

         self.cursor.execute('COMMIT')

         return True
      except Exception as e:
         self.cursor.execute('ROLLBACK')
         print(e)
         return False

   def remove_user_request(self, user_id, x, y):
      field_type_added = self.cursor.execute(
         '''SELECT field_type FROM user_request 
            WHERE user_id == ? AND x == ? AND y == ?
         ''',
         (user_id, x, y)
      ).fetchone()

      if field_type_added is None:
         return False

      field_type_added = field_type_added[0]

      try:
         self.cursor.execute('BEGIN')

         field_name_added = ft(field_type_added).name
         self.change_field_value(x, y, field_name_added, -1)

         self.cursor.execute('''
            DELETE FROM user_request 
            WHERE user_id == ? AND x == ? AND y == ?;
         ''', 
            (user_id, x, y)
         )
         self.cursor.execute('COMMIT')

         return field_type_added
      except Exception as e:
         self.cursor.execute('ROLLBACK')
         print(e)
         return False
      
   def remove_user_records(self, user_id):
      coords = self.cursor.execute(
         '''SELECT x, y FROM user_request 
            WHERE user_id == ?
         ''',
         (user_id,)
      ).fetchall()      

      print(coords)

      for x_y in coords:
         self.remove_user_request(user_id, x_y[0], x_y[1])

   def __init__(self, db_dir):
      self.db_dir = db_dir
      self.connection, self.cursor = self.connect()
      self.field_type_str = get_field_type_str()
      self.create_table_fields()
      self.create_table_user_request()
      self.create_table_util()


if __name__ == '__main__':
   db = Db('db')
   db.connection.set_trace_callback(print)

   db.create_table_fields()
   db.create_table_user_request()
   db.add_user_request('shuraken007', 1, 1, 1)
   db.add_user_request('shuraken007', 1, 2, 0)
   print(db.get_field_by_coords(1, 1))
   # db.remove_user_records('shuraken007')
   db.connection.close()