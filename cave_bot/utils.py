from pathlib import Path
import os
from datetime import datetime, timezone, timedelta
from .const import MSG_CONSTRAINT
import tracemalloc
import objgraph
from io import StringIO

import cProfile
import io
import pstats

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

def time_to_global_timezone(dt):
   global_timezone = timezone.utc
   dt = dt.replace(tzinfo=global_timezone)
   return dt

def build_sending_msg_arr_consider_constraint(arr):
   new_arr = []
   start_idx, end_idx = 0, 0
   cur_len = 0
   for e in arr:
      if cur_len + len(e) + (end_idx - start_idx) > MSG_CONSTRAINT:
         joined = '\n'.join(arr[start_idx:end_idx])
         if joined:
            new_arr.append(joined)
         start_idx = end_idx
         cur_len = 0

      cur_len += len(e)
      end_idx += 1

   if not end_idx > len(arr):
      joined = '\n'.join(arr[start_idx:end_idx])
      if joined:
         new_arr.append(joined)

   return new_arr

def get_mock_class_with_attr(attribute_dict):
   return type('',(object,),attribute_dict)()

def start_memory_tracker():
   tracemalloc.start() 

def print_memory_tracker(ctx):
   # snapshot = tracemalloc.take_snapshot() 
   # top_stats = snapshot.statistics('lineno') 
   
   # for stat in top_stats[:10]: 
   #    ctx.report.msg.add(str(stat))

   mem_info = StringIO()
   objgraph.show_most_common_types(limit = 10, file=mem_info)
   ctx.report.msg.add(mem_info.getvalue())

def profile_start(ctx):
   ctx.bot.pr = cProfile.Profile()
   ctx.bot.pr.enable()

def profile_end(ctx):
   ctx.bot.pr.disable()

   s = io.StringIO()
   ps = pstats.Stats(ctx.bot.pr, stream=s).sort_stats("cumulative")
   ps.print_stats(20)
   msg = s.getvalue()
   msg_arr = msg.split("\n")
   # uncomment this to see who's calling what
   # ps.print_callers()
   ctx.report.msg.add('Profile start <--------------------------')
   ctx.report.msg.add(msg_arr)
   ctx.report.msg.add('Profile end <--------------------------')

def copy_dict_with_exclude(dict, exclude):
   res = {}
   for k, v in dict.items():
      if k in exclude:
         continue
      res[k] = v
   return res