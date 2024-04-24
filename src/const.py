import re
import enum

MATCH_REPORT = re.compile(r"(\d+\-\d+) : (.+);")

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

field_aliases = {
   f.unknown              : ["u", "unknown"],
   f.empty                : ["e", "empty"],
   f.demon_hands          : ["dha", "demon hands"],
   f.demon_head           : ["dhe", "demon head"],
   f.demon_tail           : ["dt", "demon tail"],
   f.spider               : ["s", "spider"],
   f.idle_reward          : ["i", "idle reward"],
   f.summon_stone         : ["ss", "summon stone"],
   f.artifact             : ["a", "artifact"],
   f.amulet_of_fear       : ["af", "amulet of fear"],
   f.demon_skull          : ["ds", "demon skull"],
   f.golden_compass       : ["gc", "golden compass"],
   f.lucky_bones          : ["lb", "lucky bones"],
   f.scepter_of_domination: ["sd", "scepter of domination"],
   f.spiral_of_time       : ["st", "spiral of time"],
   f.token_of_memories    : ["tm", "token of memories"],
}

color_scheme = {
   f.unknown              : None,
   f.demon_hands          : ['red', None],
   f.demon_head           : ['red', None],
   f.demon_tail           : ['red', None],
   f.spider               : ['red', None],
   f.idle_reward          : ['green', None],
   f.summon_stone         : ['cyan', None],
   f.artifact             : ['yellow', None],
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
     f.artifact             : "◆",
     f.amulet_of_fear       : "◆",
     f.demon_skull          : "◆",
     f.golden_compass       : "◆",
     f.lucky_bones          : "◆",
     f.scepter_of_domination: "◆",
     f.spiral_of_time       : "◆",
     f.token_of_memories    : "◆",
}

# scan_allowed = [1231401015228497981]
scan_allowed_channel_ids = [1214291351945093120]
allowed_channel_ids = [1214291351945093120, 1231401015228497981]

MAP_SIZE = [20, 20]

if __name__ == '__main__':
   FieldType.print()