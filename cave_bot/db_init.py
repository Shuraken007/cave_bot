import sqlalchemy as sa
from sqlalchemy_utils import database_exists, create_database

from .const import UserRole as ur

def get_engine(db_connection_str):
   echo = False
   engine = sa.create_engine(db_connection_str, echo = echo)
   print(f'created engine {engine.url}')
   if not database_exists(engine.url): create_database(engine.url)
   return engine

class Db:
   def __init__(self, models, db_connection_str, admin_id=None):
      self.m = models
      self.engine = get_engine(db_connection_str)
      
      self.Session = self.get_session()
      self.add_admin(admin_id)

   def drop_tables(self):
      self.m.Base.metadata.drop_all(bind = self.engine)

   def add_admin(self, admin_id):
      if admin_id is None:
         return
      with self.Session() as s:
         admin = self.m.Role(id = admin_id, role = ur.super_admin)
         s.merge(admin)
         s.commit()

   def get_session(self):
      Session = sa.orm.sessionmaker()
      Session.configure(bind=self.engine)

      self.m.Base.metadata.create_all(self.engine)
      return Session