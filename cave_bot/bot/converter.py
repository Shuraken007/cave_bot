from discord.ext.commands import Converter, BadArgument

from ..parser import validate_coords, validate_what
from .bot_util import init_ctx
from ..const import color_config_cell_aliases, icon_config_cell_aliases
from ..reaction import Reactions
from PIL import ImageColor

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

   def validate_hex(self, hex, report):
      if not hex.startswith("#"):
         hex = "#" + hex
      rgb = None
      try:
         rgb = list(ImageColor.getcolor(hex, "RGB"))
      except Exception as e:
         report.err.add(str(e))
         return
      return rgb

   def validate_alpha(self, alpha, report):
      if alpha > 100 or alpha < 0:
         report.err.add(INVALID_COLOR_TRANSPARENCY.format(alpha))
         return
      return alpha

   def validate_color_rgba(self, color_arr, hex, report):
      # search alpha
      if len(color_arr) == 3 and hex is not None and hex.isdigit():
         alpha = int(hex)
         color_arr.append(alpha)
         hex = None

      alpha = None
      if len(color_arr) in [1, 4]:
         alpha = color_arr.pop()
         alpha = self.validate_alpha(alpha, report)
         if alpha is None:
            return None, None

      rgb_from_hex = None
      if hex is not None:
         rgb_from_hex = self.validate_hex(hex, report)
         if rgb_from_hex is None:
            return None, None

      if rgb_from_hex is not None and len(color_arr) > 1:
         report.err.add('error: both - rgb and hex colors were given')
         return None, None
      elif rgb_from_hex:
         return rgb_from_hex, alpha
      elif len(color_arr) == 0:
         return None, alpha

      if len(color_arr) != 3:
         report.err.add(INVALID_COLOR_ERR_BOUND.format(len(color_arr)))
         return None, None

      for c in range(3):
         if color_arr[c] < 0 or color_arr[c] > 255:
            report.err.add(INVALID_COLOR_COMPONENT_ERR_BOUND.format(color_arr[c]))
            return None, None

      return color_arr, alpha

   def convert(self, ctx, color_arr, hex):
      
      init_ctx(ctx)
      if len(color_arr) == 0 and hex is None:
         return
      color_rgb, alpha = self.validate_color_rgba(color_arr, hex, ctx.report)
      if color_rgb is None and alpha is None:
         raise BadArgument()
      
      color = []
      if color_rgb is not None:
         color.extend(color_rgb)
      if alpha is not None:
         color.append(alpha)

      return color