import re, regex

from .const import cell_aliases, CellType as ct, map_type_aliases, MapType
from .reaction import Reactions as r
from .bot.bot_util import strict_channels_f, strict_users_f
from .const import UserRole as ur

MATCH_MAP = re.compile(r"Cave Difficulty\s*:\s*([\d\w]+)")
MATCH_REPORT = re.compile(r"(\d+\-\d+)\s*:\s*([\w' ]+)")
MATCH_COMPACT_REPORT = regex.compile(r"([\w' ]+)\s*:\s*(\d+\-\d+\s*)+")

def validate_coords(coords, report, map_type=MapType.easy):
   try:
      extracted_coords = coords.split('-')

      if len(extracted_coords) != 2:
         err_msg = f'error: only {len(extracted_coords)} coords {extracted_coords}'
         report.err.add(err_msg)
         report.reaction.add(r.fail)
         return

      x = int(extracted_coords[0])
      y = int(extracted_coords[1])

      map_size = map_type.value
      if x < 1 or x > map_size or y < 1 or y > map_size:
         err_msg = f'error: x - {x} or y - {y} failed bounds'
         report.err.add(err_msg)
         report.reaction.add(r.fail)
         return
   
      return [x, y]
   except Exception as e:
      report.log.add({'exception': str(e)})

def validate_what(what, report):
   what = what.lower()
   if not what in cell_aliases:
      err_msg = f'error: unknown "what" {what}'
      report.err.add(err_msg)
      report.reaction.add(r.fail)
      return
   return ct(cell_aliases[what])

def validate_map_type(map_type_val, ctx):
   map_type = map_type_aliases.get(map_type_val)
   if map_type is None:
      err_msg = f'unknown map difficulty {map_type_val}'
      ctx.report.err.add(err_msg)
      ctx.report.reaction.add(r.fail)
      return
   return map_type

def validate_and_add(what, coords, bot, map_type, ctx):
   try:
      strict_channels_f(ctx)
      strict_users_f(ctx, ur.nobody)
   except Exception as error:
      ctx.report.err.add(str(error))
      return

   what = validate_what(what, ctx.report)
   coords = validate_coords(coords, ctx.report, map_type)

   if what is None or coords is None:
      return
   bot.controller.add(what, coords, ctx, map_type)

def parse_msg(ctx, bot):   
   arr = ctx.message.content.split("\n")
   i = 1

   map_type = bot.controller.detect_user_map_type(ctx.message.author, ctx, with_error = False)
   
   for e in arr:
      ctx.report.set_key(f'line {i}')
      i += 1
      if match := MATCH_MAP.match(e):
         map_type_alias = match.group(1)
         map_type = validate_map_type(map_type_alias, ctx)

         if not map_type:
            return
         bot.controller.config.set(ctx.message.author, 'map_type', map_type, ctx.report)
      if match := MATCH_REPORT.match(e):
         coords = match.group(1)
         what = match.group(2).strip()
         validate_and_add(what, coords, bot, map_type, ctx)
      elif match:= MATCH_COMPACT_REPORT.match(e):
         what = match.group(1).strip()
         coords_arr = match.captures(2)
         for coords in coords_arr:
            coords = coords.strip()
            validate_and_add(what, coords, bot, map_type, ctx)
      else:
         ctx.report.log.add({'error': f'not match'})