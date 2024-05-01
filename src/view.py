#!python3
from const import MAP_SIZE, CellType as ct
from utils import is_cell_type_mandatory

class Cell:
   def __init__(self, cell_type_counters = None):
      if cell_type_counters is None:
         cell_type_counters = [0] * len(ct)
      
      self.val = cell_type_counters

   def get_most_cell_type(self):
      most_i, prev_most_i = 0, 0
      arr = self.val
      for i in range(0, len(self.val)):
         if arr[most_i] < arr[i]:
            prev_most_i = most_i
            most_i = i

      most_cell_type = ct(most_i)

      # safe priority is lower, than idle
      if most_cell_type == ct.safe and arr[prev_most_i] > 0:
         prev_cell_type = ct(prev_most_i)
         if prev_cell_type != ct.unknown:
            most_cell_type = prev_cell_type

      return most_cell_type
   
   def get_cell_type_counter(self, cell_type):
      return self.val[cell_type.value]
   
   def update(self, cell_type_counters):
      self.val = cell_type_counters
      
class View:
   def update_cell(self, x, y, cell_type_counters):
      self.cells[x-1][y-1].update(cell_type_counters)

   def get_cell(self, x, y):
      return self.cells[x-1][y-1]
   
   def get_cell_type(self, x, y):
      return self.cells[x-1][y-1].get_most_cell_type()

   def __init__(self, model):
      cells = []
      for i in range(0, MAP_SIZE[0]):
         row = []
         for j in range(0, MAP_SIZE[1]):
            row.append(Cell())
         cells.append(row)
      
      self.cells = cells