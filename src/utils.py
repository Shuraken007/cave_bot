from pathlib import Path
import os
from datetime import datetime, timezone, timedelta

def build_path(path_arr, file_name=None, mkdir=False):
   path = os.path.join(os.path.dirname( __file__ ), '..', *path_arr)
   if mkdir:
      Path(path).mkdir(parents=True, exist_ok=True)
   if file_name:
      path = os.path.join(path, file_name)
   elif not path.endswith(os.path.sep):
      path += os.path.sep
   return path

def my_assert(val):
  assert val, 'value not exists'
  return val

def get_last_monday():
   utc = timezone.utc
   now = datetime.now(tz=utc)
   monday = now + timedelta(days=-now.weekday(), weeks=0)
   monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
   return monday

def get_week_start_as_str():
   return get_last_monday().strftime('%d_%m_%Y')

def is_time_anaware(dt):
   return not dt.strftime('%Z') == 'UTC'

def time_to_local_timezone(dt):
   local_timezone = datetime.now().astimezone().tzinfo
   dt = dt.replace(tzinfo=local_timezone)
   return dt
