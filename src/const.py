import enum

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
   ct.demon_hands          : ["dh", "demon's hand"],
   ct.demon_head           : ["d", "demon"],
   ct.demon_tail           : ["dt", "demon's tail"],
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

cell_max_amount = {
   ct.demon_head : 4,
   ct.demon_tail : 20,
   ct.demon_hands : 20,
   ct.spider : 20,
   'artifact' : 5,
   ct.summon_stone : 10,
   ct.empty : 125,
}

all_items_total = 0
for _, v in cell_max_amount.items():
   all_items_total += v

cell_max_amount[ct.idle_reward] = 400 - all_items_total

# build reverted cell_aliases: "u" : ct.unknown

cell_aliases = {}
for k, v in cell_aliases_config.items():
   for alias in v:
      cell_aliases[alias] = k


MAP_SIZE = [20, 20]

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


if __name__ == '__main__':
   CellType.print()