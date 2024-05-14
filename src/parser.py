import re, regex

from .const import cell_aliases, MAP_SIZE, CellType as ct
from .reaction import Reactions as r

MATCH_REPORT = re.compile(r"(\d+\-\d+) : ([\w' ]+)")
MATCH_COMPACT_REPORT = regex.compile(r"([\w' ]+)\s*:\s*(\d+\-\d+\s*)+")

def validate_coords(coords, report):
   try:
      extracted_coords = coords.split('-')

      if len(extracted_coords) != 2:
         err_msg = f'error: only {len(extracted_coords)} coords {extracted_coords}'
         report.err.add(err_msg)
         report.reaction.add(r.fail)
         return

      x = int(extracted_coords[0])
      y = int(extracted_coords[1])

      if x < 1 or x > MAP_SIZE[0] or y < 1 or y > MAP_SIZE[1]:
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

def validate_and_add(what, coords, bot, ctx):
   what = validate_what(what, ctx.report)
   coords = validate_coords(coords, ctx.report)

   if what is None or coords is None:
      return
   
   bot.controller.add(what, coords, ctx)


def parse_msg(ctx, bot):
   arr = ctx.message.content.split("\n")
   i = 1
   for e in arr:
      ctx.report.set_key(f'line {i}')
      i += 1
      if match := MATCH_REPORT.match(e):
         coords = match.group(1)
         what = match.group(2).strip()
         validate_and_add(what, coords, bot, ctx)
      elif match:= MATCH_COMPACT_REPORT.match(e):
         what = match.group(1).strip()
         coords_arr = match.captures(2)
         for coords in coords_arr:
            coords = coords.strip()
            validate_and_add(what, coords, bot, ctx)
      else:
         ctx.report.log.add({'error': f'not match'})