import os
import sqlalchemy as sa
from sqlalchemy_utils import database_exists, create_database

from .const import UserRole as ur, DEFAULT_DB_NAME
from .utils import build_path

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
   db_name = os.getenv('DB_NAME', default = DEFAULT_DB_NAME)

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

   conn_str = '{}://{}{}/{}{}'.format(
      dialect_driver, username_pwd, host_port, dir_path, db_name
   )
   
   return conn_str

DB_CONNECTION = get_db_connection_str()

def get_engine():
   engine = sa.create_engine(DB_CONNECTION)
   # engine = sa.create_engine(DB_CONNECTION, echo = True)
   print(f'created engine {engine.url}')
   if not database_exists(engine.url): create_database(engine.url)
   return engine

class Db:
   def __init__(self, models, admin_id=None):
      self.m = models
      self.engine = get_engine()
      
      self.Session = self.get_session()
      self.add_admin(admin_id)

   def drop_tables(self):
      self.m.Base.metadata.drop_all(bind = self.engine)

   def add_admin(self, admin_id):
      if admin_id is None:
         return
      with self.Session() as s:
         admin = self.m.Role(id = admin_id, role = ur.super_admin.value)
         s.merge(admin)
         s.commit()

   def get_session(self):
      Session = sa.orm.sessionmaker()
      Session.configure(bind=self.engine)

      self.m.Base.metadata.create_all(self.engine)
      return Session

if __name__ == '__main__':
   db = Db('db', const_db_name='const', admin_id = 18297365238475)
   pass