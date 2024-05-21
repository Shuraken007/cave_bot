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
      self.memory_db = sa.create_engine("sqlite://")
      self.load_db = get_engine(db_connection_str)

      self.m.Base.metadata.create_all(self.memory_db)
      self.m.Base.metadata.create_all(self.load_db)

      self.load_from_one_db_to_another(self.load_db, self.memory_db)

      self.Session = self.get_session(self.memory_db)
      self.LoadSession = self.get_session(self.load_db)

      self.add_admin(admin_id)

      with self.Session() as s:
         last_scan_record = s.query(self.m.LastScan).first()
         print(f'last_scan: {str(last_scan_record and last_scan_record.last_scan)}')


   def drop_tables(self):
      self.m.Base.metadata.drop_all(bind = self.load_db)

   def add_admin(self, admin_id):
      if admin_id is None:
         return
      with self.Session() as s:
         admin = self.m.Role(id = admin_id, role = ur.super_admin)
         s.merge(admin)
         s.commit()

   def get_session(self, engine):
      Session = sa.orm.sessionmaker()
      Session.configure(bind=engine)
      return Session
   
   def save_to_load_db(self):
      self.load_from_one_db_to_another(self.memory_db, self.load_db)

   def load_from_one_db_to_another(self, engine_from, engine_to):
      with engine_from.connect() as db_from:
         with engine_to.connect() as db_to:
            for table in self.m.Base.metadata.sorted_tables:
               db_to.execute(table.delete())
               db_to.commit()
               for row in db_from.execute(sa.select(table.c)):
                  db_to.execute(table.insert().values(row._mapping))
                  db_to.commit()