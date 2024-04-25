import color_util
from const import field_to_ascii, color_scheme, MAP_SIZE

class RenderAscii:
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

   def render(self, field):
      arr = []
      arr.append(color_util.ansi_message_start())
      for i in range(0, MAP_SIZE[0]):
         line = ""
         if i % 10 == 0 and i > 0:
            arr.append("")
         for j in range(0, MAP_SIZE[1]):
            if j % 5 == 0 and j > 0:
               line += " "
            values = field.fields[i][j]
            field_type = values.index(max(values))
            c = self.get_char(field_type, i, j)
            line += c
         line = self.wrap_line(line, i)
         arr.append(line)
      
      arr.append(color_util.ansi_message_end())
      return '\n'.join(arr)