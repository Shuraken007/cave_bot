from ..const import DEFAULT_USER_CONFIG
from ..reaction import Reactions
import prettytable

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

      keys = sorted(DEFAULT_USER_CONFIG.keys())
      text_keys = [x for x in keys if 'text_' in x]
      color_keys = [x for x in keys if '_color' in x and x not in text_keys]
      icon_keys = [x for x in keys if '_icon' in x]

      tabl1 = prettytable.PrettyTable(['Main', 'Settings'])
      for key in keys:
         if key in [*text_keys, *color_keys, *icon_keys]:
            continue
         value = getattr(user_config, key)

         if key == 'subscribe_id':
            key = 'color_scheme'
            if user_config.subscribe is not None:
               value = user_config.subscribe.name

         if value is None:
            value = 'None'

         tabl1.add_row([key, value])
         
      tabl2 = prettytable.PrettyTable(['Icon', 'Settings'])
      for key in icon_keys:
         value = getattr(user_config, key)
         key_str = key.removesuffix('_icon')
         tabl2.add_row([key_str, value])

      tabl3 = prettytable.PrettyTable(['Color', 'Settings'])
      for key in color_keys:
         value = getattr(user_config, key)
         key_str = key.removesuffix('_color')
         tabl3.add_row([key_str, value])

      tabl4 = prettytable.PrettyTable(['Text', 'Settings'])
      for key in text_keys:
         value = getattr(user_config, key)
         key_str = key.removesuffix('_color')
         tabl4.add_row([key_str, value])
      
      for t in [tabl1,tabl2,tabl3,tabl4]:
         msg = t.get_string()
         msg_arr = msg.split('\n')
         report.msg.add(msg_arr)         

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