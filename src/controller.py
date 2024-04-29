from const import cell_aliases, CellType as ct, UserRole as ur
from reaction import Reactions as r
from const import MAP_SIZE
from collections import OrderedDict

class Controller:
   def __init__(self, model, view):
      self.model = model
      self.view = view
      self.user_roles = {}
      self.init_view()
      self.init_user_roles()
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

   def init_user_roles(self):
      roles = self.model.get_user_roles()
      for (user_id, user_role) in roles:
         self.user_roles[user_id] = ur(user_role)
   
   def get_user_role(self, user):
      if not user.id in self.user_roles:
         return ur.nobody
      return self.user_roles[user.id]

   def user_have_role_greater_or_equal(self, user, min_role, report):
      user_role = self.get_user_role(user)

      if user_role < min_role:
         err_msg = "required {} privilige, while {} have {}" \
            .format(min_role.name, user.name, user_role.name)
         report.add_reaction(r.fail)
         report.add_error(err_msg)
         return False
      return True

   def user_have_role_less_than(self, user, max_role, report):
      user_role = self.get_user_role(user)

      if max_role <= user_role:
         err_msg = "{} have role {}, but must be less than {}" \
            .format(user.name, user_role.name, max_role.name)
         report.add_reaction(r.fail)
         report.add_error(err_msg)
         return False
      return True

   def add_user_role(self, user, user_role, ctx):
      author_role = self.get_user_role(ctx.message.author)
      if not self.user_have_role_less_than(user, author_role, ctx.report):
         return
      if have_role:= self.user_roles.get(user.id):
         have_role = ur(have_role)
         if have_role == user_role:
            ctx.report.add_reaction(r.user_data_equal)
            ctx.report.add_message(f'user {user.name} already have role {user_role.name}')
            return
         else:
            ctx.report.add_reaction(r.user_data_changed)
            ctx.report.add_message(f'user {user.name}: {have_role.name} -> {user_role.name}')
      
      self.model.add_user_role(user.id, user_role)
      ctx.report.add_reaction(r.ok)
      self.user_roles[user.id] = user_role

   def delete_user_role(self, user, ctx):
      author_role = self.get_user_role(ctx.message.author)
      if not self.user_have_role_less_than(user, author_role, ctx.report):
         return
      if not user.id in self.user_roles:
         ctx.report.add_message(f'user {user.name} has no privileges')
         return
      
      self.model.delete_user_role(user.id)
      ctx.report.add_reaction(r.ok)
      del self.user_roles[user.id]

   async def get_user_name_by_id(self, user_id, bot):
      user_id = int(user_id)

      user = bot.get_user(user_id)
      if user is None:
         user = await bot.fetch_user(user_id)
      if user is None:
         return f'unknown name ({user_id} id)'

      return user.name

   async def report_user_roles(self, bot, report):
      role_report = []
      for user_id, user_role in self.user_roles.items():
         user_name = await self.get_user_name_by_id(user_id, bot)
         role_report.append(f'{user_name} : {user_role.name}')

      msg = "\n".join(role_report)
      report.add_message(msg)

   def add(self, what, coords, ctx):

      user_id = ctx.message.author.id
      cell_type_new = what
      cell_type_was = self.model.get_user_record(user_id, *coords)

      if cell_type_was is not None and cell_type_was == cell_type_new:
         ctx.report.add_reaction(r.user_data_equal)
         return

      is_cell_type_changed = False
      if cell_type_was:
         self.model.update_cell(*coords, cell_type_was, -1)
         is_cell_type_changed |= self.update_cell(coords)

      self.model.update_user_record_and_cell(user_id, coords, cell_type_new)
      is_cell_type_changed |= self.update_cell(coords)

      if cell_type_was is None:
         ctx.report.add_reaction(r.user_data_new)
      else:
         ctx.report.add_reaction(r.user_data_changed)

      if is_cell_type_changed:
         if cell_type_was is None:
            ctx.report.add_reaction(r.cell_new)
         else:
            ctx.report.add_reaction(r.cell_update)
      
      cell = self.view.get_cell(*coords)
      cell_type_most = cell.get_most_cell_type()
      if cell_type_most != cell_type_new:
         cell_type_most_counter = cell.get_cell_type_counter(cell_type_most)
         cell_type_new_counter = cell.get_cell_type_counter(cell_type_new)
         msg = 'adding wrong item: coords: {}, popular item: {} added {} times, you add item: {} added {} times'
         error = msg.format(coords, cell_type_most.name, cell_type_most_counter, cell_type_new.name, cell_type_new_counter - 1)
         ctx.report.add_error(error)
         ctx.report.add_reaction(r.user_data_wrong)

   def delete(self, coords, user, ctx):
      author_role = self.get_user_role(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.user_have_role_less_than(user, author_role, ctx.report):
         return

      cell_type_was = self.model.get_user_record(user.id, *coords)

      if cell_type_was is None:
         ctx.report.add_reaction(r.user_data_equal)
         return

      self.model.delete_user_record_and_update_cell(user.id, coords, cell_type_was)
      ctx.report.add_reaction(r.user_data_deleted)
      is_cell_type_changed = self.update_cell(coords)

      if is_cell_type_changed:
         ctx.report.add_reaction(r.cell_update)

   def deleteall(self, user, ctx):
      author_role = self.get_user_role(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.user_have_role_less_than(user, author_role, ctx.report):
         return

      data = self.model.get_all_user_record(user.id)

      for (x, y, cell_type_val) in data:
         self.model.delete_user_record_and_update_cell(user.id, [x, y], ct(cell_type_val))
         ctx.report.add_reaction(r.user_data_deleted)
         is_cell_type_changed = self.update_cell([x, y])
         if is_cell_type_changed:
            ctx.report.add_reaction(r.cell_update)



   # def report(self, is_compact, ctx):
   #    user_id = ctx.message.author.id
   #    msg_arr = []
   #    compact = {}

   #    for i in range(0, MAP_SIZE[0]):
   #       for j in range(0, MAP_SIZE[1]):
   #          cell_type = self.model.get_user_record(user_id, i+1, j+1)
   #          if cell_type is None:
   #             continue

   #          coords_as_str = f'{i+1}-{j+1}'
   #          msg_arr.append(f'{coords_as_str} : {cell_type.name}')

   #          if not cell_type.name in compact:
   #             compact[cell_type.name] = []
   #          compact[cell_type.name].append(coords_as_str)

   #    if is_compact:
   #       msg_arr = []
   #       for key, value in compact.items():
   #          val_as_str = ' | '.join(value)
   #          msg_arr.append(f'{key} : {val_as_str}')

   #    msg = '\n'.join(msg_arr)
   #    ctx.report.add_message(msg)
   def report(self, user, is_compact, ctx):
      author_role = self.get_user_role(ctx.message.author)
      if user.id != ctx.message.author.id and \
         not self.user_have_role_less_than(user, author_role, ctx.report):
         return

      msg_arr = []
      compact = {}

      data = self.model.get_all_user_record(user.id)

      for (x, y, cell_type_val) in data:
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

      msg = '\n'.join(msg_arr)
      ctx.report.add_message(msg)

   async def report_cell(self, coords, ctx, bot):
      users_and_types_by_coords = self.model.get_users_and_types_by_coords(*coords)
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

      msg = '\n'.join(msg_arr)
      ctx.report.add_message(msg)