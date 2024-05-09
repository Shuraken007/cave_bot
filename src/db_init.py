import os
import sqlalchemy as sa
from sqlalchemy_utils import database_exists, create_database, drop_database

from .const import UserRole as ur
from .utils import build_path
from .model import Week, Const, UserRole

from dotenv import load_dotenv
load_dotenv()

def get_db_connection_str():
   dialect = os.getenv('DB_DIALECT')
   driver = os.getenv('DB_DRIVER', default = None)
   username = os.getenv('DB_USERNAME', default = None)
   pwd = os.getenv('DB_PWD', default = None)
   host = os.getenv('DB_HOST', default = None)
   port = os.getenv('DB_PORT', default = None)
   dir = os.getenv('DB_DIR', default = None)

   dialect_driver = dialect
   if driver:
      dialect_driver += f'+{driver}'

   username_pwd = ''
   if username:
      username_pwd += username
   if pwd:
      username_pwd += f':{pwd}'
   
   host_port = ''
   if host:
      host_port = f'@{host}'
   if port:
      host_port += f':{port}'

   dir_path = ''
   if dir:
      dir_path = build_path([dir], None, mkdir=True)

   conn_str = '{}://{}{}/{}'.format(
      dialect_driver, username_pwd, host_port, dir_path
   )
   
   return conn_str

DB_CONNECTION = get_db_connection_str()

def get_engine(db_name):
   db_file_path = db_name + '.db'   
   engine = sa.create_engine(DB_CONNECTION+db_file_path)
   print(f'created engine {engine.url}')
   # engine = sa.create_engine(DB_CONNECTION+db_file_path, echo = True)
   if not database_exists(engine.url): create_database(engine.url)
   return engine

class Db:
   def __init__(self, const_db_name = None, week_db_name = None, admin_id=None):
      self.week_engine = get_engine(week_db_name)
      self.const_engine = get_engine(const_db_name)
      
      self.Session = self.get_session(self.week_engine, self.const_engine)
      self.add_admin(admin_id)

   def drop_db(self):
      drop_database(self.week_engine.url)
      drop_database(self.const_engine.url)

   def add_admin(self, admin_id):
      if admin_id is None:
         return
      with self.Session() as s:
         admin = UserRole(id = admin_id, role = ur.super_admin.value)
         s.merge(admin)
         s.commit()

   def get_session(self, engine1, engine2):
      Session = sa.orm.sessionmaker()
      Session.configure(binds={Week:engine1, Const:engine2})
      Week.metadata.create_all(engine1)
      Const.metadata.create_all(engine2)
      return Session

if __name__ == '__main__':
   db = Db('db', const_db_name='const', admin_id = 18297365238475)
   pass