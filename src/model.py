from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator
from sqlalchemy import Integer, Column, DateTime

from datetime import datetime, timezone
from const import CellType

class TimeStamp(TypeDecorator):
   impl = DateTime
   LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo
   cache_ok = True
   
   def process_bind_param(self, value: datetime, dialect):
      if value.tzinfo is None:
         value = value.astimezone(self.LOCAL_TIMEZONE)

      return value.astimezone(timezone.utc)

   def process_result_value(self, value, dialect):
      if value.tzinfo is None:
         return value.replace(tzinfo=timezone.utc)

      return value.astimezone(timezone.utc)

class Week(DeclarativeBase):
    pass

class Const(DeclarativeBase):
    pass

cell_spec = {
   '__tablename__': 'cell',
   'x': Column(Integer, primary_key = True),
   'y': Column(Integer, primary_key = True),   
}
for cell_type in CellType:
   cell_spec[cell_type.name] = Column(Integer, default=0)

Cell = type('Cell', (Week,), cell_spec)

class UserRecord(Week):
   __tablename__ = 'user_record'
   user_id       = Column(Integer, primary_key = True)
   x             = Column(Integer, primary_key = True)
   y             = Column(Integer, primary_key = True)
   cell_type     = Column(Integer)

class LastScan(Const):
   __tablename__ = 'last_scan'
   id            = Column(Integer, default = 1, primary_key = True)
   last_scan     = Column(TimeStamp(), default=datetime.now())

class UserRole(Const): 
   __tablename__ = 'user_role'
   id       = Column(Integer, primary_key = True)
   role     = Column(Integer)