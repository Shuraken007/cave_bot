#!python3
from const import MAP_SIZE, CellType

class Cell:
   def __init__(self, cell_type_counters = None):
      if cell_type_counters is None:
         cell_type_counters = [0] * len(CellType)
      
      self.val = cell_type_counters

   def get_most_cell_type(self):
      return CellType(self.val.index(max(self.val)))
   
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