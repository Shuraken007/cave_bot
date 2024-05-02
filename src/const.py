import enum

class CellType(enum.IntEnum):
   unknown               = 0,
   safe                  = 1,
   empty                 = 2,
   demon_hands           = 3
   demon_head            = 4
   demon_tail            = 5
   spider                = 6
   idle_reward           = 7
   summon_stone          = 8
   amulet_of_fear        = 9
   demon_skull           = 10
   golden_compass        = 11
   lucky_bones           = 12
   scepter_of_domination = 13
   spiral_of_time        = 14
   token_of_memories     = 15

ct = CellType

cell_description = {
   ct.demon_hands: "Loose next turn",
   ct.spider     : "Run back to previous room",
   ct.demon_tail : "Next direction will be random",
   ct.demon_head : "Loose all remaining turns",
}

cell_aliases_config = {
   ct.unknown              : ["u", "unknown"],
   ct.empty                : ["e", "empty"],
   ct.safe                 : ["s", "safe"],
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
   ct.empty : 100,
   ct.idle_reward : 400 - 100 - 20 - 20 - 20 - 10 - 5 - 4,
}

# build reverted cell_aliases: "u" : ct.unknown

cell_aliases = {}
for k, v in cell_aliases_config.items():
   for alias in v:
      cell_aliases[alias] = k


MAP_SIZE = [20, 20]

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