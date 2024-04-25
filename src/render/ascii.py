import color_util
from const import MAP_SIZE, FieldType as f

color_scheme = {
   f.unknown              : None,
   f.demon_hands          : ['red', None],
   f.demon_head           : ['red', None],
   f.demon_tail           : ['red', None],
   f.spider               : ['red', None],
   f.idle_reward          : ['green', None],
   f.summon_stone         : ['cyan', None],
   f.amulet_of_fear       : ['yellow', None],
   f.demon_skull          : ['yellow', None],
   f.golden_compass       : ['yellow', None],
   f.lucky_bones          : ['yellow', None],
   f.scepter_of_domination: ['yellow', None],
   f.spiral_of_time       : ['yellow', None],
   f.token_of_memories    : ['yellow', None],
}

field_to_ascii = {
     f.unknown              : ["░", "▒"],
   # f.unknown              : ["░", "⍣", "◆"],
     f.empty                : "▁",
     f.demon_hands          : '▇',
     f.demon_head           : '▇',
     f.demon_tail           : '▇',
     f.spider               : '▇',
     f.idle_reward          : '○︎',
     f.summon_stone         : '●︎',
     f.amulet_of_fear       : "◆",
     f.demon_skull          : "◆",
     f.golden_compass       : "◆",
     f.lucky_bones          : "◆",
     f.scepter_of_domination: "◆",
     f.spiral_of_time       : "◆",
     f.token_of_memories    : "◆",
}

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
      return '\n'.join(arr), None