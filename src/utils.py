from pathlib import Path
from const import CellType as ct
import os

def build_path(path_arr, file_name=None, mkdir=False):
   path = os.path.join(os.path.dirname( __file__ ), '..', *path_arr)
   if mkdir:
      Path(path).mkdir(parents=True, exist_ok=True)
   if file_name:
      path = os.path.join(path, file_name)
   return path

def my_assert(val):
  assert val, 'value not exists'
  return val

def is_cell_type_mandatory(cell_type):
   if cell_type in [ct.unknown, ct.empty, ct.safe, ct.idle_reward]:
      return False
   else:
      return True