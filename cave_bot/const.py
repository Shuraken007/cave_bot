import enum
import sqlalchemy as sa

class CellType(enum.IntEnum):
   unknown               = 0,
   empty                 = 1,
   demon_hands           = 2
   demon_head            = 3
   demon_tail            = 4
   spider                = 5
   idle_reward           = 6
   summon_stone          = 7
   amulet_of_fear        = 8
   demon_skull           = 9
   golden_compass        = 10
   lucky_bones           = 11
   scepter_of_domination = 12
   spiral_of_time        = 13
   token_of_memories     = 14

ct = CellType

cell_description = {
   ct.demon_hands: "Loose next turn",
   ct.spider     : "Run back to previous room",
   ct.demon_tail : "Next direction will be random",
   ct.demon_head : "Loose all remaining turns",
   'artifact' : "Any of 7 artifacts",
   ct.summon_stone : "future gacha",
   ct.idle_reward : "30 min of farming",
   ct.empty : "no rewards, better avoid",
}

cell_aliases_config = {
   ct.unknown              : ["u", "unknown"],
   ct.empty                : ["e", "empty"],
   ct.demon_hands          : ["dh", "demon's hand", "demon hands"],
   ct.demon_head           : ["d", "demon"],
   ct.demon_tail           : ["dt", "demon's tail", "demon tail"],
   ct.spider               : ["s", "spider"],
   ct.idle_reward          : ["i", "idle reward", "idle rewards"],
   ct.summon_stone         : ["ss", "summoning stone", "summon stone"],
   ct.amulet_of_fear       : ["af", "amulet of fear"],
   ct.demon_skull          : ["ds", "demon skull"],
   ct.golden_compass       : ["gc", "golden compass"],
   ct.lucky_bones          : ["lb", "lucky bones"],
   ct.scepter_of_domination: ["sd", "scepter of domination"],
   ct.spiral_of_time       : ["st", "spiral of time"],
   ct.token_of_memories    : ["tm", "token of memories"],
}

for k,v in cell_aliases_config.items():
   if k.name not in v:
      v.append(k.name)

# build reverted cell_aliases: "u" : ct.unknown

cell_aliases = {}
for k, v in cell_aliases_config.items():
   for alias in v:
      cell_aliases[alias] = k

map_cell_name_to_shortest_alias = {}
for k, v in cell_aliases_config.items():
   map_cell_name_to_shortest_alias[k.name] = min(v, key=len)

class CleanMap(enum.IntEnum):
   no_clean = 0,
   c = 1,
   clean = 1,
   idle = 1,
   cc = 2,
   enemy = 2,
   ccc = 3,
   ss_arts = 3,

class UserRole(enum.IntEnum):
   banned = 0,
   nobody = 1,
   admin = 2,
   super_admin = 3,

   @classmethod
   def has_value(cls, value):
      return value in cls._value2member_map_ 

   @classmethod
   def next(cls, ct):
      v = ct.value + 1
      if not cls.has_value(v):
         return ct      
      return cls(v)

   @classmethod
   def prev(cls, ct):
      v = ct.value - 1
      if not cls.has_value(v):
         return ct
      return cls(v)

class MapType(enum.IntEnum):
   unknown = 0,
   normal = 20,
   hard = 25,
   nightmare = 30,

map_type_aliases_config = {
   MapType.normal: ['Normal', 'n', '1', '20', 'easy'],
   MapType.hard: ['Hard', 'h', '2', '25', 'normal'],
   MapType.nightmare: ['Nightmare', 'nm', '3', '30', 'hard'],
}
map_type_aliases = {}
for k, v in map_type_aliases_config.items():
   for element in v:
      map_type_aliases[element] = k

DEFAULT_DB_NAME = 'cave.db'
MSG_CONSTRAINT = 2000 - len("```ansi\n\n```")

color_scheme = {
   ct.unknown              : None,
   ct.empty                : 'brightblue',
   ct.demon_hands          : 'red',
   ct.demon_head           : 'red',
   ct.demon_tail           : 'red',
   ct.spider               : 'red',
   ct.idle_reward          : 'blue',
   ct.summon_stone         : 'epic',
   ct.amulet_of_fear       : 'orange',
   ct.demon_skull          : 'orange',
   ct.golden_compass       : 'orange',
   ct.lucky_bones          : 'orange',
   ct.scepter_of_domination: 'orange',
   ct.spiral_of_time       : 'orange',
   ct.token_of_memories    : 'orange',
}

map_colour_alias_to_rgb = {
   "empty": [0, 0, 0, 0],
   "white": [255, 255, 255, 50],
   "black": [0, 0, 0, 50],
   "red": [255, 0, 0, 20],
   "green": [83, 255, 77, 20],
   "brightblue": [95, 135, 255, 20],
   "orange": [255, 153, 51, 100],
   "epic": [153, 51, 255, 100],
   "yellow": [255, 255, 0, 20],
   "blue": [133, 179, 255, 20],
   "white": [255, 255, 255, 50],
   "grey": [140, 140, 140, 50],
   "light_yellow": [255, 255, 153, 50],
   "white_blue": [185, 240, 255, 100],
   "black_blue": [0, 0, 10, 100],
}
c = map_colour_alias_to_rgb

DEFAULT_USER_CONFIG = {
   'map_type': MapType.normal,

   'idle_reward_icon': True,
   'summon_stone_icon': True,
   'enemy_icon': True,
   'artifact_icon': True,

   'unknown_color': c['empty'],
   'empty_color': c['brightblue'],
   'idle_reward_color': c['blue'],
   'summon_stone_color': c['epic'],
   'me_color'   : c['green'],
   'enemy_color': c['red'],
   'artifact_color'   : c['orange'],
   
   'background_color'   : c['black_blue'],
   'background_border_color'   : c['white_blue'],
}

def color_to_str(color):
   res = ','.join([str(x) for x in color])
   return res

SERVER_DEFAULT_USER_CONFIG = {
   'map_type': "20",

   'idle_reward_icon': sa.sql.expression.true(),
   'summon_stone_icon': sa.sql.expression.true(),
   'enemy_icon': sa.sql.expression.true(),
   'artifact_icon': sa.sql.expression.true(),

   'unknown_color': color_to_str(c['empty']),
   'empty_color': color_to_str(c['brightblue']),
   'idle_reward_color': color_to_str(c['blue']),
   'summon_stone_color': color_to_str(c['epic']),
   'me_color'   : color_to_str(c['green']),
   'enemy_color': color_to_str(c['red']),
   'artifact_color'   : color_to_str(c['orange']),

   'background_color'       : color_to_str(c['black_blue']),
   'background_border_color': color_to_str(c['white_blue']),
}

color_config_cell_aliases_config = {
   'unknown'     : ["u", "unknown"],
   'empty'       : ["e", "empty"],
   'idle_reward' : ["i", "idle reward", "idle rewards"],
   'summon_stone': ["ss", "summoning stone", "summon stone"],
   'enemy'       : ["en", "enemy"],
   'artifact'    : ["a", "art"],
   'me'          : ["m"],
   'background'  : ["bg", "back"],
   'background_border'  : ["bgb", "backb", "bo", "bab", "board"],
}

for k,v in color_config_cell_aliases_config.items():
   if k not in v:
      v.append(k)

color_config_cell_aliases = {}
for k, v in color_config_cell_aliases_config.items():
   for alias in v:
      color_config_cell_aliases[alias] = k

icon_config_cell_aliases_config = {
   'idle_reward' : ["i", "idle reward", "idle rewards"],
   'summon_stone': ["ss", "summoning stone", "summon stone"],
   'enemy'       : ["en", "enemy"],
   'artifact'    : ["a", "art"],
}

for k,v in icon_config_cell_aliases_config.items():
   if k not in v:
      v.append(k)

icon_config_cell_aliases = {}
for k, v in icon_config_cell_aliases_config.items():
   for alias in v:
      icon_config_cell_aliases[alias] = k