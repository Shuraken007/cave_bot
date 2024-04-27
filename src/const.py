import enum

class CellType(enum.IntEnum):
   unknown = 0,
   empty = 1,
   demon_hands = 2
   demon_head = 3
   demon_tail = 4
   spider = 5
   idle_reward = 6
   summon_stone = 7
   amulet_of_fear = 8
   demon_skull = 9
   golden_compass = 10
   lucky_bones = 11
   scepter_of_domination = 12
   spiral_of_time = 13
   token_of_memories = 14

f = CellType

cell_description = {
   f.demon_hands: "Loose next turn",
   f.spider     : "Run back to previous room",
   f.demon_tail : "Next direction will be random",
   f.demon_head : "Loose all remaining turns",
}

cell_aliases_config = {
   f.unknown              : ["u", "unknown"],
   f.empty                : ["e", "empty"],
   f.demon_hands          : ["dh", "demon's hand"],
   f.demon_head           : ["d", "demon"],
   f.demon_tail           : ["dt", "demon's tail"],
   f.spider               : ["s", "spider"],
   f.idle_reward          : ["i", "idle reward"],
   f.summon_stone         : ["ss", "summoning stone", "summon stone"],
   f.amulet_of_fear       : ["af", "amulet of fear"],
   f.demon_skull          : ["ds", "demon skull"],
   f.golden_compass       : ["gc", "golden compass"],
   f.lucky_bones          : ["lb", "lucky bones"],
   f.scepter_of_domination: ["sd", "scepter of domination"],
   f.spiral_of_time       : ["st", "spiral of time"],
   f.token_of_memories    : ["tm", "token of memories"],
}

# build reverted cell_aliases: "u" : f.unknown

cell_aliases = {}
for k, v in cell_aliases_config.items():
   for alias in v:
      cell_aliases[alias] = k

# scan_allowed = [1231401015228497981]
scan_allowed_channel_ids = [1214291351945093120]
allowed_channel_ids = [1214291351945093120, 1231401015228497981]

MAP_SIZE = [20, 20]

if __name__ == '__main__':
   CellType.print()