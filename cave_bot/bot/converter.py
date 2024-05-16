from discord.ext.commands import Converter, BadArgument

from ..parser import validate_coords, validate_what
from .bot_util import init_ctx

class CoordsConverter(Converter):
   async def convert(self, ctx, coords: str):
      init_ctx(ctx)
      coords = validate_coords(coords, ctx.report)
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
   
class ConfigConverter(Converter):
   async def convert(self, ctx, field: str):
      init_ctx(ctx)
      alias = validate_what(alias, ctx.report)
      if alias is None:
         raise BadArgument()
      
      return alias