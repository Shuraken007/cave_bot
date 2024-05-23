from collections import OrderedDict

from .const import CellType as ct, MapType
from .reaction import Reactions as r
from .controller_.role import Role
from .controller_.config import Config
from .controller_.leaderboard import Leaderboard
from .view import View

class Controller:
   def __init__(self, db_process):
      self.db_process = db_process
      self.view = {}
      self.user_roles = {}

      self.role = Role(db_process)
      self.config = Config(db_process)
      self.leaderboard = Leaderboard(db_process)

   def get_view(self, map_type):
      if view:= self.view.get(map_type):
         return view
      
      view = View(map_type)
      self.init_view(view)
      self.view[map_type] = view
      return view

   def init_view(self, view):
      cells = self.db_process.get_all_cells(view.map_type)
      for cell in cells:
         counters = [getattr(cell, x.name) for x in ct]
         view.update_cell(cell.x, cell.y, counters)

   def detect_user_map_type(self, user, ctx, with_error = True):
      user_config = self.db_process.get_user_config(user.id)
      map_type = MapType.unknown
      if user_config:
         map_type = user_config.map_type
      
      if map_type != MapType.unknown:
         return map_type
      
      map_types = self.db_process.get_user_map_types_unique(user.id)
      
      if len(map_types) == 0:
         msg = ("can't detect user map difficulty, please select\n"
                "   !config map normal\n"
                "   !co m e\n"
                "   \n"
                "   !help config map\n"
                "   !h co m")

         if with_error:
            ctx.report.unique.add(msg)
      elif len(map_types) > 1:
         msg = ("detected more, than one difficulty ({}): {}, \n"
                "please select smth one\n"
                "\n"
                "!config map normal\n"
                "!co m e\n"
                "\n"
                "!help config map\n"
                "!h co m").format(len(map_types), [x.name for x in map_types])
         if with_error:
            ctx.report.unique.add(msg)
      else:
         map_type = map_types[0]

      return map_type
   
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

   def delete_config(self, ctx):
      user = ctx.message.author
      self.config.delete(user, ctx.report)

   def show_config(self, ctx):
      user = ctx.message.author
      self.config.show(user, ctx.report)

#  Leaderboard functions
   async def show_leaderboard(self, ctx, limit):
      user = ctx.message.author
      map_type = self.detect_user_map_type(user, ctx)
      if map_type == MapType.unknown:
         ctx.report.reaction.add(r.fail)
         return

      view = self.get_view(map_type)

      await self.leaderboard.show(user, view, map_type, ctx, limit)

# Cell functions

   def update_cell(self, coords, view):
      view.set_update_tracker('up')
      new_cell_type_counters = self.db_process.get_cell_type_counters(*coords, view.map_type)
      view.update_cell(*coords, new_cell_type_counters)
      return view.get_update_tracker('up')

   def get_total_cells(self, cell_type, map_type, user_id = None):
      view = self.get_view(map_type)
      amount = 0
      if not user_id:
         amount = view.get_cell_type_amount(cell_type)
      else:
         records = self.db_process.get_user_records_by_cell_type(user_id, cell_type, map_type)
         if records is not None:
            amount = len(records)
      return amount

   def add(self, what, coords, ctx, map_type = MapType.unknown):
      if map_type == MapType.unknown:
         map_type = self.detect_user_map_type(ctx.message.author, ctx)

      if map_type == MapType.unknown:
         ctx.report.reaction.add(r.fail)
         return



      view = self.get_view(map_type)

      user_id = ctx.message.author.id
      cell_type_new = what
      cell_type_was = self.db_process.get_user_record(user_id, *coords, map_type)

      if cell_type_was is not None and cell_type_was == cell_type_new:
         ctx.report.reaction.add(r.user_data_equal)
         return

      is_cell_type_changed = False
      if cell_type_was:
         self.db_process.update_cell(*coords, cell_type_was, map_type, -1)
         is_cell_type_changed |= self.update_cell(coords, view)

      self.db_process.update_user_record_and_cell(user_id, coords, cell_type_new, map_type, ctx.message.created_at)
      is_cell_type_changed |= self.update_cell(coords, view)

      if cell_type_was is None:
         ctx.report.reaction.add(r.user_data_new)
      else:
         ctx.report.reaction.add(r.user_data_changed)

      if is_cell_type_changed:
         if cell_type_was is None:
            ctx.report.reaction.add(r.cell_new)
         else:
            ctx.report.reaction.add(r.cell_update)
      
      cell = view.get_cell(*coords)
      cell_type_most = cell.get_most_cell_type()
      if cell_type_most not in [ct.unknown, cell_type_new]:
         cell_type_most_counter = cell.get_cell_type_counter(cell_type_most)
         cell_type_new_counter = cell.get_cell_type_counter(cell_type_new)
         msg = 'adding wrong item: coords: {}, popular item: {} added {} times, you add item: {} added {} times'
         error = msg.format(coords, cell_type_most.name, cell_type_most_counter, cell_type_new.name, cell_type_new_counter - 1)
         ctx.report.err.add(error)
         ctx.report.reaction.add(r.user_data_wrong)

   def delete(self, coords, user, ctx):
      map_type = self.detect_user_map_type(user, ctx)
      if map_type == MapType.unknown:
         ctx.report.reaction.add(r.fail)
         return
      
      view = self.get_view(map_type)

      author_role = self.role.get(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.role.user_have_role_less_than(user, author_role, ctx.report):
         return

      cell_type_was = self.db_process.get_user_record(user.id, *coords, map_type)

      if cell_type_was is None:
         ctx.report.reaction.add(r.user_data_equal)
         return

      self.db_process.delete_user_record_and_update_cell(user.id, coords, cell_type_was, map_type)
      ctx.report.reaction.add(r.user_data_deleted)
      is_cell_type_changed = self.update_cell(coords, view)

      if is_cell_type_changed:
         ctx.report.reaction.add(r.cell_update)

   def deleteall(self, user, ctx):
      map_type = self.detect_user_map_type(user, ctx)
      if map_type == MapType.unknown:
         ctx.report.reaction.add(r.fail)
         return

      view = self.get_view(map_type)

      author_role = self.role.get(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.role.user_have_role_less_than(user, author_role, ctx.report):
         return

      user_records = self.db_process.get_all_user_record(user.id, map_type)

      self.report(ctx.message.author, 'c', ctx, map_type)

      for user_record in user_records:
         x             = user_record.x
         y             = user_record.y
         cell_type = user_record.cell_type

         self.db_process.delete_user_record_and_update_cell(user.id, [x, y], cell_type, map_type)
         ctx.report.reaction.add(r.user_data_deleted)
         is_cell_type_changed = self.update_cell([x, y], view)
         if is_cell_type_changed:
            ctx.report.reaction.add(r.cell_update)

   def report(self, user, is_compact, ctx, map_type = None):
      author_role = self.role.get(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.role.user_have_role_less_than(user, author_role, ctx.report):
         return
      
      map_types = []
      if map_type is not None:
         map_types = [map_type]
      else:
         map_types = self.db_process.get_user_map_types_unique(user.id)
      
      if len(map_types) == 0:
         ctx.report.msg.add('nothing to report')
         return
      
      for map_type in map_types:

         msg_arr = []
         compact = {}

         user_records = self.db_process.get_all_user_record(user.id, map_type)
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
         
         msg_arr.insert(0, f'\nMap: {map_type.name}')

         ctx.report.msg.add(msg_arr)

   async def report_cell(self, coords, ctx, bot):
      map_type = self.detect_user_map_type(ctx.message.author, ctx)
      if map_type == MapType.unknown:
         ctx.report.reaction.add(r.fail)
         return

      view = self.get_view(map_type)
      users_and_types_by_coords = self.db_process.get_users_and_types_by_coords(*coords, map_type)
      map_ct_to_usernames = OrderedDict()
      for (cell_type, user_id) in users_and_types_by_coords:
         if cell_type not in map_ct_to_usernames:
            map_ct_to_usernames[cell_type] = []
         user_name = await bot.get_user_name_by_id(user_id)
         map_ct_to_usernames[cell_type].append(user_name)

      cell = view.get_cell(*coords)
      msg_arr = []
      for key, value in map_ct_to_usernames.items():
         value.sort()
         val_as_str = ' | '.join(value)
         key_as_str = '{} ({})' \
            .format(key.name, cell.get_cell_type_counter(key))
         msg_arr.append(f'{key_as_str} : {val_as_str}')

      if len(msg_arr) == 0:
         msg_arr.append('nobody reported')

      msg_arr.insert(0, f'Map: {map_type.name}')
      
      ctx.report.msg.add(msg_arr)