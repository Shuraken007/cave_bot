from sqlalchemy.orm import DeclarativeBase
import sqlalchemy as sa
from sqlalchemy import Integer, Column, DateTime, BigInteger, TypeDecorator, \
                        Boolean, String, UniqueConstraint, Identity, \
                        ForeignKeyConstraint, ForeignKey
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
   impl = String(15)
   cache_ok = True

   def process_bind_param(self, color, dialect):
      return color_to_str(color)

   def process_result_value(self, color_str, dialect):
      color = color_str.split(',')
      color = [int(x) for x in color]
      return color
   
class Models:
   def __init__(self, Cell, UserRecord, LastScan, Role, UserConfig, ColorScheme, MapConfig, Base):
      self.Base = Base
      self.Cell = Cell
      self.UserRecord = UserRecord
      self.LastScan = LastScan
      self.Role = Role
      self.MapConfig = MapConfig
      self.UserConfig = UserConfig
      self.ColorScheme = ColorScheme

def get_table_names():
   week_postfix = get_week_start_as_str()
   table_names = {
      'Role': 'role',
      'LastScan': 'last_scan',
      'UserConfig': 'user_config',
      'ColorScheme': 'color_scheme',
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

   # class ColorScheme
   
   common_columns_user_config_and_color_scheme = [ 
      Column('cell_icon', Boolean, default=DEFAULT_USER_CONFIG['cell_icon']),
      Column('text_dark_light_threshold', Integer, default=DEFAULT_USER_CONFIG['text_dark_light_threshold']),
   ]
   common_columns_user_config_and_color_scheme_copy = [ 
      Column('cell_icon', Boolean, default=DEFAULT_USER_CONFIG['cell_icon']),
      Column('text_dark_light_threshold', Integer, default=DEFAULT_USER_CONFIG['text_dark_light_threshold']),
   ]
   for k, v in DEFAULT_USER_CONFIG.items():
      if not k.endswith('_color'):
         continue
      col = Column(k, ColorValue, default=v)
      col_copy = Column(k, ColorValue, default=v)
      common_columns_user_config_and_color_scheme.append(col)
      common_columns_user_config_and_color_scheme_copy.append(col_copy)

   common_column_names = [x.name for x in common_columns_user_config_and_color_scheme]

   class ColorScheme(Base): 
      id      = Column(Integer, primary_key=True, server_default=Identity(start=1, cycle=True))
      user_id = Column(BigInteger)
      name    = Column(String(255))

      uniq_1 = UniqueConstraint(user_id, name, name = 'uniq_1')
      user_configs = sa.orm.relationship('UserConfig', back_populates="subscribe")

      __tablename__ = table_names['ColorScheme']
      __table_args__ = tuple(common_columns_user_config_and_color_scheme)

      @staticmethod
      def get_common_column_names():
         return common_column_names

      @classmethod
      def get_common_column_names(cls):
         return common_column_names

   # class UserConfig

   user_config_icon_columns = [ ]
   for k, v in DEFAULT_USER_CONFIG.items():
      if not k.endswith('_icon'):
         continue
      if k in common_column_names:
         continue

      col = Column(k, Boolean, default=v)
      user_config_icon_columns.append(col)

   user_config_auto_columns = [
      *common_columns_user_config_and_color_scheme_copy, 
      *user_config_icon_columns
   ]

   class UserConfig(Base): 
      id            = Column(BigInteger,   primary_key = True)
      map_type      = Column(MapTypeValue, default = MapType.unknown)
      subscribe_id  = Column(Integer,      default=DEFAULT_USER_CONFIG['subscribe_id'], nullable=True)
      is_subscribed = Column(Boolean,      default=DEFAULT_USER_CONFIG['is_subscribed'])
      
      subscribe_fk  = ForeignKeyConstraint(
         [subscribe_id], [ColorScheme.id], 
         ondelete = 'SET NULL', 
         onupdate = 'CASCADE',
         name = 'subscribe_fk',
      )
      subscribe     = sa.orm.relationship(ColorScheme, back_populates="user_configs", lazy='subquery')

      __tablename__ = table_names['UserConfig']
      __table_args__ = tuple(user_config_auto_columns)

      @staticmethod
      def get_common_column_names():
         return common_column_names

      @classmethod
      def get_common_column_names(cls):
         return common_column_names
      
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

   return Models(Cell, UserRecord, LastScan, Role, UserConfig, ColorScheme, MapConfig, Base)
