#!python3
from const import MAP_SIZE, CellType as ct

class Cell:
   def __init__(self, cell_type_counters = None):
      if cell_type_counters is None:
         cell_type_counters = [0] * len(ct)
      
      self.val = cell_type_counters
      self.most = None

   def get_most_cell_type(self):
      if self.most is None:
         self.most = self.calc_cell_type()
      return self.most
   
   def calc_cell_type(self):
      if not self.val:
         return ct.unknown

      max_index = self.val.index(max(self.val))
      return ct(max_index)
   
   def get_cell_type_counter(self, cell_type):
      if not self.val:
         return 0

      return self.val[cell_type.value]
   
   def update(self, cell_type_counters):
      self.val = cell_type_counters
      most_was = self.most
      
      self.most = self.calc_cell_type()
      
      if self.most != most_was:
         return True
      
      return False
      
class View:
   def update_cell(self, x, y, cell_type_counters):
      is_update = self.cells[x-1][y-1].update(cell_type_counters)
      if is_update:
         self.update_tracker()


   def get_cell(self, x, y):
      return self.cells[x-1][y-1]
   
   def get_cell_type(self, x, y):
      return self.cells[x-1][y-1].get_most_cell_type()

   def get_cell_type_amount(self, cell_type):
      counter = 0
      for i in range(0, MAP_SIZE[0]):
         for j in range(0, MAP_SIZE[1]):
            if self.get_cell_type(i, j) == cell_type:
               counter += 1

      return counter

   def update_tracker(self):
      for k in self.tracker.keys():
         self.tracker[k] += 1

   def set_update_tracker(self, key):
      self.tracker[key] = 0

   def get_update_tracker(self, key):
      return self.tracker[key]

   def init_grid(self):
      for i in range(0, MAP_SIZE[0]):
         row = []
         for j in range(0, MAP_SIZE[1]):
            row.append(Cell())
         self.cells.append(row)

   def __init__(self, model):
      self.cells = []
      self.init_grid()
      self.tracker = {}