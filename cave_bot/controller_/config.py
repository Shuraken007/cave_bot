from ..const import DEFAULT_USER_CONFIG
from ..reaction import Reactions

class Config:
   def __init__(self, db_process):
      self.db_process = db_process

   def set(self, user, field, value, report):
      self.db_process.set_user_config(user.id, {field: value})
      report.reaction.add(Reactions.ok)

   def set_color(self, user, what, color, report):
      config_key = f'{what}_color'
      if len(color) in [1, 3]:
         user_config = self.db_process.get_user_config(user.id)
         color_was = getattr(user_config, config_key)
         if len(color) == 1:
            color_was[3] = color[0]
            color = color_was
         elif len(color) == 3:
            alpha_was = color_was[3]
            color.append(alpha_was)

      self.set(user, config_key, color, report)
      report.reaction.add(Reactions.ok)

   def reset(self, user, report):
      user_config = self.db_process.get_user_config(user.id)
      default_config = {**DEFAULT_USER_CONFIG}
      default_config['map_type'] = user_config.map_type
      self.db_process.set_user_config(user.id, default_config)
      report.reaction.add(Reactions.ok)

   def delete(self, user, report):
      self.db_process.delete_user_config(user.id)
      report.reaction.add(Reactions.ok)

   def show(self, user, report):
      user_config = self.db_process.get_user_config(user.id)
      if user_config is None:
         report.msg.add(f'no config settings')
         return

      for key in DEFAULT_USER_CONFIG.keys():
         value = getattr(user_config, key)
         report.msg.add(f'{key}: {value}')

   def copy(self, copy_from, copy_to, report):
      user_config = self.db_process.get_user_config(copy_from.id)
      if user_config is None:
         report.msg.add(f'user to copy from have not config')
         report.reaction.add(Reactions.fail)
         return

      new_config = {}
      for key in DEFAULT_USER_CONFIG.keys():
         if key == 'map_type':
            continue
         value = getattr(user_config, key)
         new_config[key] = value

      self.db_process.set_user_config(copy_to.id, new_config)
      report.reaction.add(Reactions.ok)