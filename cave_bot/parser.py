import re, regex

from .const import cell_aliases, CellType as ct, map_type_aliases, MapType
from .reaction import Reactions as r
from .bot.bot_util import strict_channels_f, strict_users_f
from .const import UserRole as ur

MATCH_MAP = re.compile(r"Cave Difficulty\s*:\s*([\d\w]+)")
MATCH_REPORT = re.compile(r"(\d+\-\d+)\s*:\s*([\w' ]+)")
MATCH_COMPACT_REPORT = regex.compile(r"([\w' ]+)\s*:\s*(\d+\-\d+\s*)+")

def convert_coords_due_bug(x, y, size, report):
   absolute_number = (x-1)  * 20 + y
   a = int(absolute_number / size) + 1
   b = absolute_number % size
   if b == 0:
      b = size
      a -= 1
   return a, b
   # report.msg.add(f'[{x}-{y}] -> [{a}-{b}]')

def validate_coords(coords_arr, report, map_type=None, is_new_version = False, is_bug_converter = False):
   validated_coords_arr = []
   for coords in coords_arr:
      try:
         extracted_coords = coords.split('-')

         if len(extracted_coords) != 2:
            err_msg = f'error: only {len(extracted_coords)} coords {extracted_coords}'
            report.err.add(err_msg)
            report.reaction.add(r.fail)
            return

         x = int(extracted_coords[0])
         y = int(extracted_coords[1])

         if is_bug_converter and not is_new_version and map_type.value > MapType.normal:
            x, y = convert_coords_due_bug(x, y, map_type.value, report)

         if map_type in [None,  MapType.unknown]:
            map_type = MapType.nightmare

         map_size = map_type.value

         if x < 1 or x > map_size or y < 1 or y > map_size:
            err_msg = f'error: x - {x} or y - {y} failed bounds'
            report.err.add(err_msg)
            report.reaction.add(r.fail)
            continue
      
         validated_coords_arr.append([x, y])
      except Exception as e:
         report.log.add({'exception': str(e)})
   return validated_coords_arr

def validate_what(what, report):
   what = what.lower()
   if not what in cell_aliases:
      err_msg = f'error: unknown "what" {what}'
      report.err.add(err_msg)
      report.reaction.add(r.fail)
      return
   return ct(cell_aliases[what])

def validate_map_type(map_type_val, ctx):
   is_new_version = False
   map_type = map_type_aliases.get(map_type_val)
   if map_type is None:
      err_msg = f'unknown map difficulty {map_type_val}'
      ctx.report.err.add(err_msg)
      ctx.report.reaction.add(r.fail)

   if len(map_type_val) > 1:
      is_new_version = True

   return map_type, is_new_version

def validate_and_add(what, coords_arr, bot, map_type, ctx, is_new_version, is_bug_converter):
   try:
      strict_channels_f(ctx)
      strict_users_f(ctx, ur.nobody)
   except Exception as error:
      ctx.report.err.add(str(error))
      return

   what = validate_what(what, ctx.report)
   coords_arr = validate_coords(coords_arr, ctx.report, map_type, is_new_version, is_bug_converter)

   if what is None or coords_arr is None or len(coords_arr) == 0:
      return
   bot.controller.add(what, coords_arr, ctx, map_type)

def parse_msg(ctx, bot):   
   arr = ctx.message.content.split("\n")
   i = 1

   map_type = bot.controller.detect_user_map_type(ctx.message.author, ctx, with_error = False)
   is_new_version = False
   is_bug_converter = False

   for e in arr:
      ctx.report.set_key(f'line {i}')
      i += 1
      if match := MATCH_MAP.match(e):
         map_type_alias = match.group(1)
         map_type, is_new_version = validate_map_type(map_type_alias, ctx)
         is_bug_converter = True
         if not map_type:
            return
         bot.controller.config.set(ctx.message.author, 'map_type', map_type, ctx.report)
      if match := MATCH_REPORT.match(e):
         coords = match.group(1).strip()
         what = match.group(2).strip()
         validate_and_add(what, [coords], bot, map_type, ctx, is_new_version, is_bug_converter)
      elif match:= MATCH_COMPACT_REPORT.match(e):
         what = match.group(1).strip()
         coords_arr = match.captures(2)
         coords_arr = [x.strip() for x in coords_arr]
         validate_and_add(what, coords_arr, bot, map_type, ctx, is_new_version, is_bug_converter)
      else:
         ctx.report.log.add({'error': f'not match'})