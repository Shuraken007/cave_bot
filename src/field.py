#!python3
from const import field_aliases, MAP_SIZE, emoji

class Field:
   def add(self, alias, x, y, bot, message):
      field_type = field_aliases[alias].value
      
      if bot.db.add_user_request(message.author.id, x, y, field_type):
         self.fields[x-1][y-1][int(field_type)] += 1
         return None, emoji['yes']
      else:
         return None, emoji['already']

   def remove(self, x, y, db, message):
      field_type = db.remove_user_request(message.author.id, x, y)
      if field_type is not False:
         self.fields[x-1][y-1][int(field_type)] -= 1
         return None, emoji['yes']
      else:
         return None, emoji['already']

   def __init__(self, db):
      fields = []
      for i in range(1, MAP_SIZE[0] + 1):
         row = []
         for j in range(1, MAP_SIZE[1] + 1):
            column = list(db.get_field_by_coords(i, j))
            row.append(column)
         fields.append(row)
      
      self.fields = fields
      