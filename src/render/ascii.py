from . import color_util
from ..const import MAP_SIZE, CellType as ct

color_scheme = {
   ct.unknown              : None,
   ct.demon_hands          : ['red', None],
   ct.demon_head           : ['red', None],
   ct.demon_tail           : ['red', None],
   ct.spider               : ['red', None],
   ct.idle_reward          : ['blue', None],
   ct.summon_stone         : ['cyan', None],
   ct.amulet_of_fear       : ['yellow', None],
   ct.demon_skull          : ['yellow', None],
   ct.golden_compass       : ['yellow', None],
   ct.lucky_bones          : ['yellow', None],
   ct.scepter_of_domination: ['yellow', None],
   ct.spiral_of_time       : ['yellow', None],
   ct.token_of_memories    : ['yellow', None],
}

cell_to_ascii = {
     ct.unknown              : ["░", "▒"],
   # ct.unknown              : ["░", "⍣", "◆"],
     ct.empty                : "▁",
     ct.demon_hands          : '▇',
     ct.demon_head           : '▇',
     ct.demon_tail           : '▇',
     ct.spider               : '▇',
     ct.idle_reward          : '○︎',
     ct.summon_stone         : '●︎',
     ct.amulet_of_fear       : "◆",
     ct.demon_skull          : "◆",
     ct.golden_compass       : "◆",
     ct.lucky_bones          : "◆",
     ct.scepter_of_domination: "◆",
     ct.spiral_of_time       : "◆",
     ct.token_of_memories    : "◆",
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

   def get_char(self, cell_type, i, j):
      c = cell_to_ascii[cell_type]
      if type(c) == list:
         c = c[(i+j) % len(c)]
         # c = c[(i) % len(c)]

      color = color_scheme.get(cell_type)
      if color:
         c = color_util.color_msg(c, *color)

      return c

   def render(self, user_id, bot, ctx):
      arr = []
      # arr.append(color_util.ansi_message_start())
      for i in range(0, MAP_SIZE[0]):
         line = ""
         # if i % 10 == 0 and i > 0:
         #    arr.append("")
         for j in range(0, MAP_SIZE[1]):
            # if j % 5 == 0 and j > 0:
            #    line += " "
            cell_type = bot.view.get_cell_type(i+1, j+1)
            if user_id and bot.db_process.get_user_record(user_id, i+1, j+1) is not None:
               cell_type = ct.unknown

            c = self.get_char(cell_type, i, j)
            line += c
         line = self.wrap_line(line, i)
         arr.append(line)
      
      # arr.append(color_util.ansi_message_end())
      ctx.report.msg.add(arr)
