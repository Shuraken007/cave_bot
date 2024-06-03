from ..const import UserRole as ur
from ..reaction import Reactions as r

class Role:
   def __init__(self, db_process, admin_id):
      self.db_process = db_process
      self.admin_id = admin_id
      self.user_roles = {}
      self.init_admin()
      self.init_all_roles()

   def init_admin(self):
      if self.admin_id is None:
         return
      
      self.db_process.add_user_role(self.admin_id, ur.super_admin)

   def init_all_roles(self):
      user_roles = self.db_process.get_user_roles()
      for user_role in user_roles:
         self.user_roles[user_role.id] = user_role.role

   def get(self, user):
      if not user.id in self.user_roles:
         return ur.nobody
      return self.user_roles[user.id]

   def user_have_role_greater_or_equal(self, user, min_role, report):
      user_role = self.get(user)

      if user_role < min_role:
         err_msg = "required {} privilige, while {} have {}" \
            .format(min_role.name, user.name, user_role.name)
         return False, err_msg
      return True, None

   def user_have_role_less_than(self, user, max_role, report):
      user_role = self.get(user)

      if max_role <= user_role:
         err_msg = "{} have role {}, but must be less than {}" \
            .format(user.name, user_role.name, max_role.name)
         report.reaction.add(r.fail)
         report.err.add(err_msg)
         return False
      return True

   def add(self, user, user_role, ctx):
      author_role = self.get(ctx.message.author)
      if not self.user_have_role_less_than(user, author_role, ctx.report):
         return
      if have_role:= self.user_roles.get(user.id):
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

   def delete(self, user, ctx):
      author_role = self.get(ctx.message.author)
      if not self.user_have_role_less_than(user, author_role, ctx.report):
         return
      if not user.id in self.user_roles:
         ctx.report.msg.add(f'user {user.name} has no privileges')
         return
      
      self.db_process.delete_user_role(user.id)
      ctx.report.reaction.add(r.ok)
      del self.user_roles[user.id]

   async def report(self, bot, report):
      role_report = []
      for user_id, user_role in self.user_roles.items():
         user_name = await bot.get_user_name_by_id(user_id)
         role_report.append(f'{user_name} : {user_role.name}')

      report.msg.add(role_report)
