from collections import OrderedDict

from .const import cell_aliases, CellType as ct, UserRole as ur, MAP_SIZE, DEFAULT_MAP_SIZE
from .reaction import Reactions as r

class Controller:
   def __init__(self, db_process, view):
      self.db_process = db_process
      self.view = view
      self.user_roles = {}
      self.init_view()
      self.init_user_roles()
      pass

   def update_cell(self, coords):
      self.view.set_update_tracker('up')
      new_cell_type_counters = self.db_process.get_cell_type_counters(*coords, DEFAULT_MAP_SIZE)
      self.view.update_cell(*coords, new_cell_type_counters)
      return self.view.get_update_tracker('up')
   
   def init_view(self):
      for i in range(0, MAP_SIZE[0]):
         for j in range(0, MAP_SIZE[1]):
            self.update_cell([i+1, j+1])

   def init_user_roles(self):
      user_roles = self.db_process.get_user_roles()
      for user_role in user_roles:
         self.user_roles[user_role.id] = ur(user_role.role)
   
   def get_user_role(self, user):
      if not user.id in self.user_roles:
         return ur.nobody
      return self.user_roles[user.id]

   def user_have_role_greater_or_equal(self, user, min_role, report):
      user_role = self.get_user_role(user)

      if user_role < min_role:
         err_msg = "required {} privilige, while {} have {}" \
            .format(min_role.name, user.name, user_role.name)
         return False, err_msg
      return True, None

   def user_have_role_less_than(self, user, max_role, report):
      user_role = self.get_user_role(user)

      if max_role <= user_role:
         err_msg = "{} have role {}, but must be less than {}" \
            .format(user.name, user_role.name, max_role.name)
         report.reaction.add(r.fail)
         report.err.add(err_msg)
         return False
      return True

   def add_user_role(self, user, user_role, ctx):
      author_role = self.get_user_role(ctx.message.author)
      if not self.user_have_role_less_than(user, author_role, ctx.report):
         return
      if have_role:= self.user_roles.get(user.id):
         have_role = ur(have_role)
         if have_role == user_role:
            ctx.report.reaction.add(r.user_data_equal)
            ctx.report.msg.add(f'user {user.name} already have role {user_role.name}')
            return
         else:
            ctx.report.reaction.add(r.user_data_changed)
            ctx.report.msg.add(f'user {user.name}: {have_role.name} -> {user_role.name}')
      
      self.db_process.add_user_role(user.id, user_role)
      ctx.report.reaction.add(r.ok)
      self.user_roles[user.id] = user_role

   def delete_user_role(self, user, ctx):
      author_role = self.get_user_role(ctx.message.author)
      if not self.user_have_role_less_than(user, author_role, ctx.report):
         return
      if not user.id in self.user_roles:
         ctx.report.msg.add(f'user {user.name} has no privileges')
         return
      
      self.db_process.delete_user_role(user.id)
      ctx.report.reaction.add(r.ok)
      del self.user_roles[user.id]

   async def get_user_name_by_id(self, user_id, bot):
      user_id = int(user_id)
      
      user = bot.get_user(user_id)
      if user is None:
         try:
            user = await bot.fetch_user(user_id)
         except:
            pass
      if user is None:
         return f'unknown name ({user_id} id)'

      return user.name

   async def report_user_roles(self, bot, report):
      role_report = []
      for user_id, user_role in self.user_roles.items():
         user_name = await self.get_user_name_by_id(user_id, bot)
         role_report.append(f'{user_name} : {user_role.name}')

      report.msg.add(role_report)

   def get_total_cells(self, cell_type, user_id):
      amount = 0
      if not user_id:
         amount = self.view.get_cell_type_amount(cell_type)
      else:
         records = self.db_process.get_user_records_by_cell_type(user_id, cell_type, DEFAULT_MAP_SIZE)
         if records is not None:
            amount = len(records)
      return amount


   def add(self, what, coords, ctx):

      user_id = ctx.message.author.id
      cell_type_new = what
      cell_type_was = self.db_process.get_user_record(user_id, *coords, DEFAULT_MAP_SIZE)

      if cell_type_was is not None and cell_type_was == cell_type_new:
         ctx.report.reaction.add(r.user_data_equal)
         return

      is_cell_type_changed = False
      if cell_type_was:
         self.db_process.update_cell(*coords, cell_type_was, DEFAULT_MAP_SIZE, -1)
         is_cell_type_changed |= self.update_cell(coords)

      self.db_process.update_user_record_and_cell(user_id, coords, cell_type_new, DEFAULT_MAP_SIZE)
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
      author_role = self.get_user_role(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.user_have_role_less_than(user, author_role, ctx.report):
         return

      cell_type_was = self.db_process.get_user_record(user.id, *coords, DEFAULT_MAP_SIZE)

      if cell_type_was is None:
         ctx.report.reaction.add(r.user_data_equal)
         return

      self.db_process.delete_user_record_and_update_cell(user.id, coords, cell_type_was, DEFAULT_MAP_SIZE)
      ctx.report.reaction.add(r.user_data_deleted)
      is_cell_type_changed = self.update_cell(coords)

      if is_cell_type_changed:
         ctx.report.reaction.add(r.cell_update)

   def deleteall(self, user, ctx):
      author_role = self.get_user_role(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.user_have_role_less_than(user, author_role, ctx.report):
         return

      user_records = self.db_process.get_all_user_record(user.id, DEFAULT_MAP_SIZE)

      for user_record in user_records:
         x             = user_record.x
         y             = user_record.y
         cell_type_val = user_record.cell_type

         self.db_process.delete_user_record_and_update_cell(user.id, [x, y], ct(cell_type_val), DEFAULT_MAP_SIZE)
         ctx.report.reaction.add(r.user_data_deleted)
         is_cell_type_changed = self.update_cell([x, y])
         if is_cell_type_changed:
            ctx.report.reaction.add(r.cell_update)

   def report(self, user, is_compact, ctx):
      author_role = self.get_user_role(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.user_have_role_less_than(user, author_role, ctx.report):
         return

      msg_arr = []
      compact = {}

      user_records = self.db_process.get_all_user_record(user.id, DEFAULT_MAP_SIZE)
      for user_record in user_records:
         x             = user_record.x
         y             = user_record.y
         cell_type_val = user_record.cell_type

         coords_as_str = f'{x}-{y}'
         ct_name = ct(cell_type_val).name
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
      users_and_types_by_coords = self.db_process.get_users_and_types_by_coords(*coords, DEFAULT_MAP_SIZE)
      map_ct_to_usernames = OrderedDict()
      for (cell_type_val, user_id) in users_and_types_by_coords:
         if cell_type_val not in map_ct_to_usernames:
            map_ct_to_usernames[cell_type_val] = []
         user_name = await self.get_user_name_by_id(user_id, bot)
         map_ct_to_usernames[cell_type_val].append(user_name)

      cell = self.view.get_cell(*coords)
      msg_arr = []
      for key, value in map_ct_to_usernames.items():
         value.sort()
         val_as_str = ' | '.join(value)
         key_as_str = '{} ({})' \
            .format(ct(key).name, cell.get_cell_type_counter(ct(key)))
         msg_arr.append(f'{key_as_str} : {val_as_str}')

      if len(msg_arr) == 0:
         msg_arr.append('nobody reported')
         
      ctx.report.msg.add(msg_arr)