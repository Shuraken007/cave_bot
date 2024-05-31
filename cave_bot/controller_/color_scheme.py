import prettytable
import operator

from ..const import DEFAULT_USER_CONFIG
from ..reaction import Reactions
from ..bot.bot_util import pil_image_to_dfile
from discord import Embed, Colour

class ColorScheme:
   def __init__(self, db_process):
      self.db_process = db_process

   async def get_one_scheme(self, user, name, ctx):
      color_schemes = self.db_process.search_color_schemes(user and user.id, name)
      if not color_schemes or len(color_schemes) == 0:
         ctx.report.err.add("can't find scheme")
         ctx.report.reaction.add(Reactions.fail)
         return None
      elif len(color_schemes) > 1:
         ctx.report.msg.add("founded more, than one scheme")
         ctx.report.reaction.add(Reactions.fail)
         await self.search_as_table(user, name, ctx)
         return None
      return color_schemes[0]

   def save(self, user, name, ctx):
      user_config = self.db_process.get_user_config(user.id)
      if user_config is None:
         ctx.report.reaction.add(Reactions.fail)
         ctx.report.msg.add(f'user have not config')

      if len(name) > 255:
         ctx.report.reaction.add(Reactions.fail)
         ctx.report.msg.add(f'too long name, expected 255 chars, got {len(name)}')
      
      scheme_dict = {}
      for key in DEFAULT_USER_CONFIG.keys():
         if key in [ 'map_type', 'idle_reward_icon','summon_stone_icon','enemy_icon','artifact_icon' ]:
            continue
         value = getattr(user_config, key)
         scheme_dict[key] = value

      self.db_process.add_color_scheme(user.id, name, scheme_dict)
      ctx.report.reaction.add(Reactions.ok)

   async def delete(self, user, name, ctx):
      scheme = await self.get_one_scheme(user, name, ctx)
      if not scheme:
         return
      
      self.db_process.delete_color_scheme(scheme.user_id, scheme.name)
      ctx.report.reaction.add(Reactions.ok)

   async def search_as_table(self, user, partial_name, ctx):
      color_schemes = self.db_process.search_color_schemes(user and user.id, partial_name)
      tabl = prettytable.PrettyTable(['user', 'scheme'])
      for color_scheme in color_schemes:
         user_name = await ctx.bot.get_user_name_by_id(color_scheme.user_id)
         row = [user_name, color_scheme.name]
         tabl.add_row(row)

      msg = tabl.get_string(sort_key=operator.itemgetter(0, 1), sortby="user")
      msg_arr = msg.split('\n')
      ctx.report.msg.add(msg_arr)       

   async def search(self, user, partial_name, ctx):
      color_schemes = self.db_process.search_color_schemes(user and user.id, partial_name)
      embeds_and_files = []
      for color_scheme in color_schemes:
         user_name = await ctx.bot.get_user_name_by_id(color_scheme.user_id)
         scheme_name = color_scheme.name
         img = ctx.bot.render_theme.get_theme_img(color_scheme)

         file = pil_image_to_dfile(img, f'{scheme_name}.png')
         embed = Embed(
            title=f'{user_name}: {scheme_name}',
            colour = Colour.from_rgb(*color_scheme.background_color[:3]),
            type = "article"
         )
         embed.set_image(url=f"attachment://{scheme_name}.png")
         embeds_and_files.append([embed, file, user_name, scheme_name])

      embeds_and_files.sort(key = lambda x: (x[2], x[3]))

      for [embed, file, _, _] in embeds_and_files:
         ctx.report.embed_and_files.add(embed, file)

   async def load(self, user, user_from, name, ctx):
      color_scheme = await self.get_one_scheme(user_from, name, ctx)
      if not color_scheme:
         return      
      if color_scheme is None:
         ctx.msg.add(f'no such color_scheme')
         ctx.report.reaction.add(Reactions.fail)
         return

      new_config = {}
      for key in DEFAULT_USER_CONFIG.keys():
         if key in [ 'map_type', 'idle_reward_icon','summon_stone_icon','enemy_icon','artifact_icon' ]:
            continue
         value = getattr(color_scheme, key)
         new_config[key] = value

      self.db_process.set_user_config(user.id, new_config)
      ctx.report.reaction.add(Reactions.ok)