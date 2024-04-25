import re
from const import field_aliases, MAP_SIZE

MATCH_REPORT = re.compile(r"(\d+\-\d+) : ([\w' ]+)")

class Parser:
   def validate_coords(self, coords, ctx):
      try:
         extracted_coords = coords.split('-')
         if len(extracted_coords) != 2:
            err_msg = f'error: only {len(extracted_coords)} coords {extracted_coords}'
            return None, None, err_msg

         x = int(extracted_coords[0])
         y = int(extracted_coords[1])

         if x < 1 or x > MAP_SIZE[0] or y < 1 or y > MAP_SIZE[1]:
            err_msg = f'error: x - {x} or y - {y} failed bounds'
            return None, None, err_msg
      
         return x, y, None
      except Exception as e:
         ctx.report['exception'] = str(e)
         return None, None, None

   def validate_alias(self, alias):
      alias = alias.lower()
      if not alias in field_aliases:
         err_msg = f'error: unknown alias {alias}'
         return None, err_msg
         # return f'alias {alias} is not known'
      return alias, None
   
   def parse_msg(self, message, ctx, bot):
      arr = message.content.split("\n")
      for e in arr:
         log = {'args': e}
         if match := MATCH_REPORT.match(e):
            coords = match.group(1)
            alias = match.group(2).strip()

            alias, err_msg = self.validate_alias(alias, bot)
            x, y, err_msg = self.validate_coords(coords, bot)

            if err_msg:
               log['error'] = err_msg
               ctx.log.append(log)
               continue

            bot.field.add(alias, x, y, bot, message)
         else:
            log['error'] = f'not match'
            ctx.log.append(log)
      return None, None