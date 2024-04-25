import enum

class FieldType(enum.IntEnum):
   unknown = 0,
   empty = 1,
   demon_hands = 2
   demon_head = 3
   demon_tail = 4
   spider = 5
   idle_reward = 6
   summon_stone = 7
   artifact = 8
   amulet_of_fear = 9
   demon_skull = 10
   golden_compass = 11
   lucky_bones = 12
   scepter_of_domination = 13
   spiral_of_time = 14
   token_of_memories = 15

f = FieldType

field_description = {
   f.demon_hands: "Loose next turn",
   f.spider     : "run back to previous room",
   f.demon_tail : "next direction will be random",
   f.demon_head : "Loose all remaining turns",
}

field_aliases_config = {
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

# build reverted field_aliases: "u" : f.unknown

field_aliases = {}
for k, v in field_aliases_config.items():
   for alias in v:
      field_aliases[alias] = k

# scan_allowed = [1231401015228497981]
scan_allowed_channel_ids = [1214291351945093120]
allowed_channel_ids = [1214291351945093120, 1231401015228497981]

MAP_SIZE = [20, 20]

if __name__ == '__main__':
   FieldType.print()