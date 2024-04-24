#!python3
import color_util
from const import FieldType, field_description, field_aliases, color_scheme, field_to_ascii, MATCH_REPORT, MAP_SIZE

reverted_field_aliases = {}
for k, v in field_aliases.items():
   for alias in v:
      reverted_field_aliases[alias] = k

class Field:   
   def wrap_line(self, line, i):
      prefix = " "
      if i % 5 == 0:
         prefix = "-"
      postfix = ""
      if i % 5 == 0:
         postfix += "- "
         postfix += str(i+1)
      return prefix + line + postfix

   def get_char(self, field_type, i, j):
      c = field_to_ascii[field_type]
      if type(c) == list:
         c = c[(i+j) % len(c)]
         # c = c[(i) % len(c)]

      color = color_scheme.get(field_type)
      if color:
         c = color_util.color_msg(c, *color)

      return c

   def show(self):
      arr = []
      arr.append(color_util.ansi_message_start())
      for i in range(0, MAP_SIZE[0]):
         line = ""
         if i % 10 == 0 and i > 0:
            arr.append("")
         for j in range(0, MAP_SIZE[1]):
            if j % 5 == 0 and j > 0:
               line += " "
            values = self.fields[i][j]
            field_type = values.index(max(values))
            c = self.get_char(field_type, i, j)
            line += c
         line = self.wrap_line(line, i)
         arr.append(line)
      
      arr.append(color_util.ansi_message_end())
      return '\n'.join(arr)

   def on_message(self, message, bot, db):
      if message.author == bot.user:
         return
      arr = message.content.split("\n")
      for e in arr:
         if match := MATCH_REPORT.match(e):
            coords = match.group(1)
            alias = match.group(2).strip()
            self.add(alias, coords, db, message)

   def validate_coords(self, coords):
      try:
         extracted_coords = coords.split('-')
         if len(extracted_coords) != 2:
            return None, None

         x = int(extracted_coords[0])
         y = int(extracted_coords[1])

         if x < 1 or x > MAP_SIZE[0] or y < 1 or y > MAP_SIZE[1]:
            return None, None
      
         return x, y
      except Exception as e:
         print(e)
         return None, None

   def add(self, alias, coords, db, message):
      alias = alias.lower()
      if not alias in reverted_field_aliases:
         return
         # return f'alias {alias} is not known'
      field_type = reverted_field_aliases[alias].value
      
      x, y = self.validate_coords(coords)
      if x is None:
         return
      
      if db.add_user_request(message.author.id, x, y, field_type):
         self.fields[x-1][y-1][int(field_type)] += 1

   def remove(self, coords, db, message):
      x, y = self.validate_coords(coords)
      if x is None:
         return

      field_type = db.remove_user_request(message.author.id, x, y)
      if field_type is not False:
         print(self.fields[x-1][y-1])
         self.fields[x-1][y-1][int(field_type)] -= 1
         print(self.fields[x-1][y-1])

   def __init__(self, db):
      fields = []
      for i in range(0, MAP_SIZE[0]):
         row = []
         for j in range(0, MAP_SIZE[1]):
            column = list(db.get_field_by_coords(i+1, j+1))
            row.append(column)
         fields.append(row)
      
      self.fields = fields
      