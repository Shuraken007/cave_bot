from os import getenv
from dotenv import load_dotenv

from .const import DEFAULT_DB_NAME
from .utils import build_path

load_dotenv()

class Config:
   def init_allowed_channel_ids(self):
      value_str = getenv('ALLOWED_CHANNEL_IDS')
      allowed_channel_ids = [int(x) for x in value_str.split(',')]
      return allowed_channel_ids

   def init_scan_allowed_channel_ids(self):
      value_str = getenv('SCAN_ALLOWED_CHANNEL_IDS')
      scan_allowed_channel_ids = [int(x) for x in value_str.split(',')]
      return scan_allowed_channel_ids

   def get_db_connection_str(self):
      dialect = getenv('DB_DIALECT')
      driver = getenv('DB_DRIVER', default = None)
      username = getenv('DB_USERNAME', default = None)
      pwd = getenv('DB_PWD', default = None)
      host = getenv('DB_HOST', default = None)
      port = getenv('DB_PORT', default = None)
      dir = getenv('DB_DIR', default = None)
      db_name = getenv('DB_NAME', default = DEFAULT_DB_NAME)

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

   def __init__(self):
      self.allowed_channel_ids = self.init_allowed_channel_ids()
      self.scan_allowed_channel_ids = self.init_allowed_channel_ids()
      self.admin_id = getenv('ADMIN_ID', None)
      self.token = getenv('DISCORD_TOKEN')
      self.db_connection_str = self.get_db_connection_str()