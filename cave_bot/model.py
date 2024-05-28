from sqlalchemy.orm import DeclarativeBase
import sqlalchemy as sa
from sqlalchemy import Integer, Column, DateTime, BigInteger, TypeDecorator, Boolean, String
from datetime import datetime, timezone

from .const import CellType as ct, UserRole, MapType, DEFAULT_USER_CONFIG, color_to_str
from .utils import get_week_start_as_str

class CellTypeValue(TypeDecorator):
   impl = Integer
   cache_ok = True

   def process_bind_param(self, cell_type, dialect):
      return cell_type.value

   def process_result_value(self, value, dialect):
      return ct(value)
   
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
   
class ColorValue(TypeDecorator):
   impl = String(3*3+1+3)
   cache_ok = True

   def process_bind_param(self, color, dialect):
      return color_to_str(color)

   def process_result_value(self, color_str, dialect):
      color = color_str.split(',')
      color = [int(x) for x in color]
      return color
   
class Models:
   def __init__(self, Cell, UserRecord, LastScan, Role, UserConfig, MapConfig, Base):
      self.Base = Base
      self.Cell = Cell
      self.UserRecord = UserRecord
      self.LastScan = LastScan
      self.Role = Role
      self.MapConfig = MapConfig
      self.UserConfig = UserConfig

def get_table_names():
   week_postfix = get_week_start_as_str()
   table_names = {
      'Role': 'role',
      'LastScan': 'last_scan',
      'UserConfig': 'user_config',
      'MapConfig': 'map_config',
      'Cell': 'cell_' + week_postfix,
      'UserRecord': 'user_record_' + week_postfix,
   }
   return week_postfix, table_names

def generate_models(table_names):
   class Base(DeclarativeBase):
      pass

   # class Cell
   cell_spec = {
      '__tablename__': table_names['Cell'],
      'x'            : Column(Integer, primary_key = True),
      'y'            : Column(Integer, primary_key = True),
      'map_type'     : Column(MapTypeValue, default = MapType.unknown, primary_key = True)
   }
   for cell_type in ct:
      cell_spec[cell_type.name] = Column(Integer, default=0)

   Cell = type('Cell', (Base,), cell_spec)

   class UserRecord(Base):
      __tablename__ = table_names['UserRecord']
      user_id       = Column(BigInteger, primary_key = True)
      x             = Column(Integer, primary_key = True)
      y             = Column(Integer, primary_key = True)
      map_type      = Column(MapTypeValue, default = MapType.unknown, primary_key = True)
      cell_type     = Column(CellTypeValue)
      time          = Column(DateTime(timezone=True))

   class LastScan(Base):
      __tablename__ = table_names['LastScan']
      id            = Column(Integer, default = 1, primary_key = True)
      last_scan     = Column(DateTime(timezone=True))

   class Role(Base): 
      __tablename__ = table_names['Role']
      id       = Column(BigInteger, primary_key = True)
      role     = Column(UserRoleValue)

   # class UserConfig
   user_config_spec = {
      '__tablename__'   : table_names['UserConfig'],
      'id'              : Column(BigInteger, primary_key = True),
      'map_type'        : Column(MapTypeValue, default = MapType.unknown, primary_key = True),
      'background_color': Column(ColorValue, default=DEFAULT_USER_CONFIG['background_color']),
   }
   for cell_type in ['enemy', 'artifact', 'me', ct.summon_stone, \
                     ct.idle_reward, ct.empty, ct.unknown]:
      col_name = cell_type
      if type(cell_type) == ct:
         col_name = cell_type.name
      
      if cell_type not in [ct.empty, 'me', ct.unknown]:
         key = col_name + '_icon'
         user_config_spec[key] = Column(Boolean, default=True)
      
      key = col_name + '_color'
      user_config_spec[key] = Column(ColorValue, default=DEFAULT_USER_CONFIG[key])

   UserConfig = type('UserConfig', (Base,), user_config_spec)

   # class MapConfig
   map_config_spec = {
      '__tablename__': table_names['MapConfig'],
      'map_type'     : Column(MapTypeValue, default = MapType.unknown, primary_key = True)
   }
   for cell_type in [ct.demon_head, ct.demon_tail, ct.demon_hands, \
                     ct.spider, 'artifact', ct.summon_stone, \
                     ct.idle_reward, ct.empty]:
      col_name = cell_type
      if type(cell_type) == ct:
         col_name = cell_type.name
      map_config_spec[col_name] = Column(Integer, default=0, primary_key = True)

   MapConfig = type('MapConfig', (Base,), map_config_spec)

   return Models(Cell, UserRecord, LastScan, Role, UserConfig, MapConfig, Base)
