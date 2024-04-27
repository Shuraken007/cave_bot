from const import cell_aliases, CellType as ct
from emoji import Reactions
from const import MAP_SIZE
from collections import OrderedDict

class Controller:
   def __init__(self, model, view):
      self.model = model
      self.view = view
      self.init_view()
      pass

   def update_cell(self, coords):
      was_cell_type = self.view.get_cell_type(*coords)

      new_cell_type_counters = self.model.get_cell_type_counters(*coords)
      self.view.update_cell(*coords, new_cell_type_counters)
      
      new_cell_type = self.view.get_cell_type(*coords)

      if was_cell_type == new_cell_type:
         return False

      return True

   def init_view(self):
      for i in range(0, MAP_SIZE[0]):
         for j in range(0, MAP_SIZE[1]):
            self.update_cell([i+1, j+1])

   def add(self, what, coords, message, report):

      user_id = message.author.id
      cell_type_new = what
      cell_type_was = self.model.get_user_record(user_id, *coords)

      if cell_type_was is not None and cell_type_was == cell_type_new:
         report.add_reaction(Reactions.user_data_equal)
         return

      is_cell_type_changed = False
      if cell_type_was:
         self.model.update_cell(*coords, cell_type_was, -1)
         is_cell_type_changed |= self.update_cell(coords)

      self.model.update_user_record_and_cell(user_id, coords, cell_type_new)
      is_cell_type_changed |= self.update_cell(coords)

      if cell_type_was is None:
         report.add_reaction(Reactions.user_data_new)
      else:
         report.add_reaction(Reactions.user_data_changed)

      if is_cell_type_changed:
         if cell_type_was is None:
            report.add_reaction(Reactions.cell_new)
         else:
            report.add_reaction(Reactions.cell_update)
      
      cell = self.view.get_cell(*coords)
      cell_type_most = cell.get_most_cell_type()
      if cell_type_most != cell_type_new:
         cell_type_most_counter = cell.get_cell_type_counter(cell_type_most)
         cell_type_new_counter = cell.get_cell_type_counter(cell_type_new)
         msg = 'adding wrong item: coords: {}, popular item: {} added {} times, you add item: {} added {} times'
         error = msg.format(coords, cell_type_most.name, cell_type_most_counter, cell_type_new.name, cell_type_new_counter - 1)
         report.add_error(error)
         report.add_reaction(Reactions.user_data_wrong)

   def delete(self, coords, message, report):
      user_id = message.author.id
      cell_type_was = self.model.get_user_record(user_id, *coords)

      if cell_type_was is None:
         report.add_reaction(Reactions.user_data_equal)
         return

      self.model.delete_user_record_and_update_cell(user_id, coords, cell_type_was)
      report.add_reaction(Reactions.user_data_deleted)
      is_cell_type_changed = self.update_cell(coords)

      if is_cell_type_changed:
         report.add_reaction(Reactions.cell_update)

   def report(self, is_compact, message, report):
      user_id = message.author.id
      msg_arr = []
      compact = {}

      for i in range(0, MAP_SIZE[0]):
         for j in range(0, MAP_SIZE[1]):
            cell_type = self.model.get_user_record(user_id, i+1, j+1)
            if cell_type is None:
               continue

            coords_as_str = f'{i+1}-{j+1}'
            msg_arr.append(f'{coords_as_str} : {cell_type.name}')

            if not cell_type.name in compact:
               compact[cell_type.name] = []
            compact[cell_type.name].append(coords_as_str)

      if is_compact:
         msg_arr = []
         for key, value in compact.items():
            val_as_str = ' | '.join(value)
            msg_arr.append(f'{key} : {val_as_str}')

      msg = '\n'.join(msg_arr)
      report.add_message(msg)