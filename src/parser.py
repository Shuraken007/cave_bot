import re
from const import field_aliases, MAP_SIZE

MATCH_REPORT = re.compile(r"(\d+\-\d+) : ([\w' ]+)")

class Parser:
   def validate_coords(self, coords, report):
      try:
         extracted_coords = coords.split('-')
         if len(extracted_coords) != 2:
            report['response'] = f'error: only {len(extracted_coords)} coords'
            return None, None

         x = int(extracted_coords[0])
         y = int(extracted_coords[1])

         if x < 1 or x > MAP_SIZE[0] or y < 1 or y > MAP_SIZE[1]:
            report['response'] = f'error: x - {x} or y - {y} failed bounds'
            return None, None
      
         return x, y
      except Exception as e:
         print(e)
         report['response'] = str(e)
         return None, None

   def validate_alias(self, alias, report):
      alias = alias.lower()
      if not alias in field_aliases:
         report['response'] = f'error: unknown alias {alias}'
         return None
         # return f'alias {alias} is not known'
      return alias
   
   def parse_msg(self, message, bot):
      if message.author == bot.user:
         return
      arr = message.content.split("\n")
      for e in arr:
         report = {'request': e}
         if match := MATCH_REPORT.match(e):
            coords = match.group(1)
            alias = match.group(2).strip()

            alias = self.validate_alias(alias, report)
            x, y = self.validate_coords(coords, report)

            if not (alias and x and y):
               bot.logger.dump_msg(report, 'log', mode='dump')
               return

            bot.field.add(alias, x, y, bot, message)
         else:
            report['response'] = f'not match'
            bot.logger.dump_msg(report, 'log', mode='dump')
