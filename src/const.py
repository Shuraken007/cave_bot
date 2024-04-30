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
   ct.idle_reward          : ["i", "idle reward"],
   ct.summon_stone         : ["ss", "summoning stone", "summon stone"],
   ct.amulet_of_fear       : ["af", "amulet of fear"],
   ct.demon_skull          : ["ds", "demon skull"],
   ct.golden_compass       : ["gc", "golden compass"],
   ct.lucky_bones          : ["lb", "lucky bones"],
   ct.scepter_of_domination: ["sd", "scepter of domination"],
   ct.spiral_of_time       : ["st", "spiral of time"],
   ct.token_of_memories    : ["tm", "token of memories"],
}

# build reverted cell_aliases: "u" : ct.unknown

cell_aliases = {}
for k, v in cell_aliases_config.items():
   for alias in v:
      cell_aliases[alias] = k


# scan_allowed_channel_ids = [1231401015228497981]
# allowed_channel_ids = [1231401015228497981]

scan_allowed_channel_ids = [1214291351945093120]
allowed_channel_ids = [1214291351945093120]

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