from ..const import DEFAULT_USER_CONFIG
from ..reaction import Reactions

class Config:
   def __init__(self, db_process):
      self.db_process = db_process

   def set(self, user, field, value, report):
      self.db_process.set_user_config(user.id, {field: value})
      report.reaction.add(Reactions.ok)

   def reset(self, user, report):
      self.db_process.set_user_config(user.id, DEFAULT_USER_CONFIG)
      report.reaction.add(Reactions.ok)

   def delete(self, user, report):
      self.db_process.delete_user_config(user.id)
      report.reaction.add(Reactions.ok)

   def show(self, user, report):
      user_config = self.db_process.get_user_config(user.id)
      if user_config is None:
         report.msg.add(f'no config settings')
         return

      report.msg.add(f'map: {user_config.map_type.name}')