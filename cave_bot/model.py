from sqlalchemy.orm import DeclarativeBase
import sqlalchemy as sa
from sqlalchemy import Integer, Column, DateTime, BigInteger, TypeDecorator

from .const import CellType, UserRole, MapType
from .utils import get_week_start_as_str

class CellTypeValue(TypeDecorator):
   impl = Integer
   cache_ok = True

   def process_bind_param(self, cell_type, dialect):
      return cell_type.value

   def process_result_value(self, value, dialect):
      return CellType(value)
   
class UserRoleValue(TypeDecorator):
   impl = Integer
   cache_ok = True

   def process_bind_param(self, user_role, dialect):
      return user_role.value

   def process_result_value(self, value, dialect):
      return UserRole(value)

class MapTypeValue(TypeDecorator):
   impl = Integer
   cache_ok = True

   def process_bind_param(self, map_type, dialect):
      return map_type.value

   def process_result_value(self, value, dialect):
      return MapType(value)
   
class Models:
   def __init__(self, Cell, UserRecord, LastScan, Role, UserConfig, Base):
      self.Base = Base
      self.Cell = Cell
      self.UserRecord = UserRecord
      self.LastScan = LastScan
      self.Role = Role
      self.UserConfig = UserConfig

def get_table_names():
   week_postfix = get_week_start_as_str()
   table_names = {
      'Role': 'role',
      'LastScan': 'last_scan',
      'UserConfig': 'user_config',
      'Cell': 'cell_' + week_postfix,
      'UserRecord': 'user_record_' + week_postfix,
   }
   return week_postfix, table_names

def generate_models(table_names):
   class Base(DeclarativeBase):
      pass

   cell_spec = {
      '__tablename__': table_names['Cell'],
      'x'            : Column(Integer, primary_key = True),
      'y'            : Column(Integer, primary_key = True),
      'map_type'     : Column(MapTypeValue, default = MapType.unknown, primary_key = True)
   }
   for cell_type in CellType:
      cell_spec[cell_type.name] = Column(Integer, default=0)

   Cell = type('Cell', (Base,), cell_spec)

   class UserRecord(Base):
      __tablename__ = table_names['UserRecord']
      user_id       = Column(BigInteger, primary_key = True)
      x             = Column(Integer, primary_key = True)
      y             = Column(Integer, primary_key = True)
      map_type      = Column(MapTypeValue, default = MapType.unknown, primary_key = True)
      cell_type     = Column(CellTypeValue)

   class LastScan(Base):
      __tablename__ = table_names['LastScan']
      id            = Column(Integer, default = 1, primary_key = True)
      last_scan     = Column(DateTime(timezone=True))

   class Role(Base): 
      __tablename__ = table_names['Role']
      id       = Column(BigInteger, primary_key = True)
      role     = Column(UserRoleValue)

   class UserConfig(Base):
      __tablename__ = table_names['UserConfig']
      id       = Column(BigInteger, primary_key = True)
      map_type = Column(MapTypeValue, default = MapType.unknown)

   return Models(Cell, UserRecord, LastScan, Role, UserConfig, Base)