from const import UserRole as ur
from utils import build_path, get_last_monday

import sqlalchemy as sa

from model import Week, Const, UserRole

DB_CONNECTION = 'sqlite:///'

def get_engine(db_name, db_dir):
   db_file_path = build_path([db_dir], db_name + '.db', mkdir=True)
   engine = sa.create_engine(DB_CONNECTION+db_file_path)
   # engine = sa.create_engine(DB_CONNECTION+db_file_path, echo = True)
   return engine

def get_uniq_db_name():
   return get_last_monday().strftime('%d_%m_%Y')

class Db:
   def __init__(self, db_dir, const_db_name, admin_id=None):
      tmp_db_name = get_uniq_db_name()
      week_engine = get_engine(tmp_db_name, db_dir)
      const_engine = get_engine(const_db_name, db_dir)
      
      self.Session = self.get_session(week_engine, const_engine)
      self.add_admin(admin_id)

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