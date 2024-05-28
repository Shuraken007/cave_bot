from discord.ext.commands import Converter, BadArgument

from ..parser import validate_coords, validate_what
from .bot_util import init_ctx
from ..const import color_config_cell_aliases, icon_config_cell_aliases
from ..reaction import Reactions

class CoordsConverter(Converter):
   async def convert(self, ctx, coords: str):
      init_ctx(ctx)
      [coords] = validate_coords([coords], ctx.report)
      if coords is None:
         raise BadArgument('failed coords')
      
      return coords
    
class AliasConverter(Converter):
   async def convert(self, ctx, alias: str):
      init_ctx(ctx)
      alias = validate_what(alias, ctx.report)
      if alias is None:
         raise BadArgument()
      
      return alias
   
class ColorConfigAliasConverter(Converter):
   def validate_what(self, what, report):
      what = what.lower()
      if not what in color_config_cell_aliases:
         err_msg = f'error: unknown "what" {what}'
         report.err.add(err_msg)
         report.reaction.add(Reactions.fail)
         return
      return color_config_cell_aliases[what]
      
   async def convert(self, ctx, alias: str):
      init_ctx(ctx)
      alias = self.validate_what(alias, ctx.report)
      if alias is None:
         raise BadArgument()
      
      return alias
   
class IconConfigAliasConverter(Converter):
   def validate_what(self, what, report):
      what = what.lower()
      if not what in icon_config_cell_aliases:
         err_msg = f'error: unknown "what" {what}'
         report.err.add(err_msg)
         report.reaction.add(Reactions.fail)
         return
      return icon_config_cell_aliases[what]
      
   async def convert(self, ctx, alias: str):
      init_ctx(ctx)
      alias = self.validate_what(alias, ctx.report)
      if alias is None:
         raise BadArgument()
      
      return alias


INVALID_COLOR_ERR_BOUND = """
expected 3 numbers, founded {}
"""
INVALID_COLOR_COMPONENT_ERR_BOUND = """
color component must be any number in [0, 255], got {}
"""
INVALID_COLOR_TRANSPARENCY = """
transparency must be any number in [0, 100], got {}
"""
class ColorConverter(Converter):

   def validate_alpha(self, alpha, report):
      if alpha > 100 or alpha < 0:
         report.err.add(INVALID_COLOR_TRANSPARENCY.format(alpha))
         return
      return alpha

   def validate_color_rgba(self, color_arr, report):
      if len(color_arr) not in [1, 3, 4]:
         report.err.add(INVALID_COLOR_ERR_BOUND.format(len(color_arr)))
         return

      # only transparency
      alpha = None
      if len(color_arr) in [1, 4]:
         alpha = color_arr.pop()
      elif len(color_arr) == 3:
         alpha = 100
      alpha = self.validate_alpha(alpha, report)
      if alpha is None:
         return
      
      color_arr.append(alpha)
      if len(color_arr) == 1:
         return color_arr
      
      for c in range(3):
         if color_arr[c] < 0 or color_arr[c] > 255:
            report.err.add(INVALID_COLOR_COMPONENT_ERR_BOUND.format(color_arr[c]))
            return
         
      return color_arr

   def convert(self, ctx, color_arr):
      
      init_ctx(ctx)
      if len(color_arr) == 0:
         return
      color = self.validate_color_rgba(color_arr, ctx.report)
      if color is None:
         raise BadArgument()
      
      return color