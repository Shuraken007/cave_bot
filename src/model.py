from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, Column, DateTime, BigInteger

from .const import CellType
from .utils import get_week_start_as_str

class Models:
   def __init__(self, Cell, UserRecord, LastScan, Role, Base):
      self.Base = Base
      self.Cell = Cell
      self.UserRecord = UserRecord
      self.LastScan = LastScan
      self.Role = Role

def get_table_names():
   week_postfix = get_week_start_as_str()
   table_names = {
      'Role': 'role',
      'LastScan': 'last_scan',
      'Cell': 'cell_' + week_postfix,
      'UserRecord': 'user_record_' + week_postfix,
   }
   return table_names

def generate_models(table_names):
   class Base(DeclarativeBase):
      pass

   cell_spec = {
      '__tablename__': table_names['Cell'],
      'x': Column(Integer, primary_key = True),
      'y': Column(Integer, primary_key = True),   
   }
   for cell_type in CellType:
      cell_spec[cell_type.name] = Column(Integer, default=0)

   Cell = type('Cell', (Base,), cell_spec)

   class UserRecord(Base):
      __tablename__ = table_names['UserRecord']
      user_id       = Column(BigInteger, primary_key = True)
      x             = Column(Integer, primary_key = True)
      y             = Column(Integer, primary_key = True)
      cell_type     = Column(Integer)

   class LastScan(Base):
      __tablename__ = table_names['LastScan']
      id            = Column(Integer, default = 1, primary_key = True)
      last_scan     = Column(DateTime(timezone=True))

   class Role(Base): 
      __tablename__ = table_names['Role']
      id       = Column(BigInteger, primary_key = True)
      role     = Column(Integer)
   

   return Models(Cell, UserRecord, LastScan, Role, Base)
