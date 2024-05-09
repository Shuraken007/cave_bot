import re

from .const import cell_aliases, MAP_SIZE, CellType as ct
from .reaction import Reactions as r

MATCH_REPORT = re.compile(r"(\d+\-\d+) : ([\w' ]+)")

class Parser:
   def validate_coords(self, coords, report):
      try:
         extracted_coords = coords.split('-')

         if len(extracted_coords) != 2:
            err_msg = f'error: only {len(extracted_coords)} coords {extracted_coords}'
            report.add_error(err_msg)
            report.add_reaction(r.fail)
            return

         x = int(extracted_coords[0])
         y = int(extracted_coords[1])

         if x < 1 or x > MAP_SIZE[0] or y < 1 or y > MAP_SIZE[1]:
            err_msg = f'error: x - {x} or y - {y} failed bounds'
            report.add_error(err_msg)
            report.add_reaction(r.fail)
            return
      
         return [x, y]
      except Exception as e:
         report.add_log({'exception': str(e)})

   def validate_what(self, what, report):
      what = what.lower()
      if not what in cell_aliases:
         err_msg = f'error: unknown "what" {what}'
         report.add_error(err_msg)
         report.add_reaction(r.fail)
         return
      return ct(cell_aliases[what])
   
   def parse_msg(self, ctx, bot):
      arr = ctx.message.content.split("\n")
      i = 1
      for e in arr:
         ctx.report.set_key(f'line {i}')
         i += 1
         if match := MATCH_REPORT.match(e):
            coords = match.group(1)
            what = match.group(2).strip()

            what = self.validate_what(what, ctx.report)
            coords = self.validate_coords(coords, ctx.report)

            if what is None or coords is None:
               continue
            
            bot.controller.add(what, coords, ctx)
         else:
            ctx.report.add_log({'error': f'not match'})