from collections import OrderedDict

from .const import CellType as ct, MAP_SIZE, DEFAULT_MAP_TYPE
from .reaction import Reactions as r
from .controller_.role import Role
from .controller_.config import Config
from .view import View

class Controller:
   def __init__(self, db_process):
      self.db_process = db_process
      self.view = View()
      self.user_roles = {}
      self.init_view()

      self.role = Role(db_process)
      self.config = Config(db_process)

   def init_view(self):
      for i in range(0, MAP_SIZE[0]):
         for j in range(0, MAP_SIZE[1]):
            self.update_cell([i+1, j+1])

#    Role Functions
   def add_user_role(self, user, user_role, ctx):
      self.role.add(user, user_role, ctx)

   def delete_user_role(self, user, ctx):
      self.role.delete(user, ctx)

   async def report_user_roles(self, bot, report):
      await self.role.report(bot, report)

#  Config functions
   def set_config(self, field, value, ctx):
      user = ctx.message.author
      self.config.set(user, field, value, ctx.report)

   def reset_config(self, ctx):
      user = ctx.message.author
      self.config.reset(user, ctx.report)

   def show_config(self, ctx):
      user = ctx.message.author
      self.config.show(user, ctx.report)

# Cell functions

   def update_cell(self, coords):
      self.view.set_update_tracker('up')
      new_cell_type_counters = self.db_process.get_cell_type_counters(*coords, DEFAULT_MAP_TYPE)
      self.view.update_cell(*coords, new_cell_type_counters)
      return self.view.get_update_tracker('up')

   def get_total_cells(self, cell_type, user_id = None):
      amount = 0
      if not user_id:
         amount = self.view.get_cell_type_amount(cell_type)
      else:
         records = self.db_process.get_user_records_by_cell_type(user_id, cell_type, DEFAULT_MAP_TYPE)
         if records is not None:
            amount = len(records)
      return amount

   def add(self, what, coords, ctx):

      user_id = ctx.message.author.id
      cell_type_new = what
      cell_type_was = self.db_process.get_user_record(user_id, *coords, DEFAULT_MAP_TYPE)

      if cell_type_was is not None and cell_type_was == cell_type_new:
         ctx.report.reaction.add(r.user_data_equal)
         return

      is_cell_type_changed = False
      if cell_type_was:
         self.db_process.update_cell(*coords, cell_type_was, DEFAULT_MAP_TYPE, -1)
         is_cell_type_changed |= self.update_cell(coords)

      self.db_process.update_user_record_and_cell(user_id, coords, cell_type_new, DEFAULT_MAP_TYPE)
      is_cell_type_changed |= self.update_cell(coords)

      if cell_type_was is None:
         ctx.report.reaction.add(r.user_data_new)
      else:
         ctx.report.reaction.add(r.user_data_changed)

      if is_cell_type_changed:
         if cell_type_was is None:
            ctx.report.reaction.add(r.cell_new)
         else:
            ctx.report.reaction.add(r.cell_update)
      
      cell = self.view.get_cell(*coords)
      cell_type_most = cell.get_most_cell_type()
      if cell_type_most not in [ct.unknown, cell_type_new]:
         cell_type_most_counter = cell.get_cell_type_counter(cell_type_most)
         cell_type_new_counter = cell.get_cell_type_counter(cell_type_new)
         msg = 'adding wrong item: coords: {}, popular item: {} added {} times, you add item: {} added {} times'
         error = msg.format(coords, cell_type_most.name, cell_type_most_counter, cell_type_new.name, cell_type_new_counter - 1)
         ctx.report.err.add(error)
         ctx.report.reaction.add(r.user_data_wrong)

   def delete(self, coords, user, ctx):
      author_role = self.role.get(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.role.user_have_role_less_than(user, author_role, ctx.report):
         return

      cell_type_was = self.db_process.get_user_record(user.id, *coords, DEFAULT_MAP_TYPE)

      if cell_type_was is None:
         ctx.report.reaction.add(r.user_data_equal)
         return

      self.db_process.delete_user_record_and_update_cell(user.id, coords, cell_type_was, DEFAULT_MAP_TYPE)
      ctx.report.reaction.add(r.user_data_deleted)
      is_cell_type_changed = self.update_cell(coords)

      if is_cell_type_changed:
         ctx.report.reaction.add(r.cell_update)

   def deleteall(self, user, ctx):
      author_role = self.role.get(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.role.user_have_role_less_than(user, author_role, ctx.report):
         return

      user_records = self.db_process.get_all_user_record(user.id, DEFAULT_MAP_TYPE)

      for user_record in user_records:
         x             = user_record.x
         y             = user_record.y
         cell_type = user_record.cell_type

         self.db_process.delete_user_record_and_update_cell(user.id, [x, y], cell_type, DEFAULT_MAP_TYPE)
         ctx.report.reaction.add(r.user_data_deleted)
         is_cell_type_changed = self.update_cell([x, y])
         if is_cell_type_changed:
            ctx.report.reaction.add(r.cell_update)

   def report(self, user, is_compact, ctx):
      author_role = self.role.get(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.role.user_have_role_less_than(user, author_role, ctx.report):
         return

      msg_arr = []
      compact = {}

      user_records = self.db_process.get_all_user_record(user.id, DEFAULT_MAP_TYPE)
      for user_record in user_records:
         x             = user_record.x
         y             = user_record.y
         cell_type = user_record.cell_type

         coords_as_str = f'{x}-{y}'
         ct_name = cell_type.name
         msg_arr.append(f'{coords_as_str} : {ct_name}')

         if not ct_name in compact:
            compact[ct_name] = []
         compact[ct_name].append(coords_as_str)

      if is_compact:
         msg_arr = []
         for key, value in compact.items():
            val_as_str = ' | '.join(value)
            msg_arr.append(f'{key} : {val_as_str}')
      ctx.report.msg.add(msg_arr)

   async def report_cell(self, coords, ctx, bot):
      users_and_types_by_coords = self.db_process.get_users_and_types_by_coords(*coords, DEFAULT_MAP_TYPE)
      map_ct_to_usernames = OrderedDict()
      for (cell_type, user_id) in users_and_types_by_coords:
         if cell_type not in map_ct_to_usernames:
            map_ct_to_usernames[cell_type] = []
         user_name = await bot.get_user_name_by_id(user_id)
         map_ct_to_usernames[cell_type].append(user_name)

      cell = self.view.get_cell(*coords)
      msg_arr = []
      for key, value in map_ct_to_usernames.items():
         value.sort()
         val_as_str = ' | '.join(value)
         key_as_str = '{} ({})' \
            .format(key.name, cell.get_cell_type_counter(key))
         msg_arr.append(f'{key_as_str} : {val_as_str}')

      if len(msg_arr) == 0:
         msg_arr.append('nobody reported')
         
      ctx.report.msg.add(msg_arr)