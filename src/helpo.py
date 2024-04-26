from discord.ext import commands
from const import field_aliases

def grouped(iterable, n):
    return zip(*[iter(iterable)]*n)
what_str = []
for a1, a2, a3, a4, a5, a6, a7, a8 in grouped(field_aliases.keys(), 8):
   what_str.append(' | '.join([a1, a2, a3, a4, a5, a6, a7, a8]))
what_str = "\n".join(what_str)
what_descr = commands.parameter(description=what_str)

help = {

'add_description' : """
   add item by coords:
   !a empty 3-5 | !a e 3-5
   !a "idle reward" 6-8 | !a i 6-8
   !add "summon stone" 2-1 3-4 8-12
   !a ss 2-1 3-4 8-12
""",
'remove_description': """
   if you gave wrong info, you can remove it:
   !remove 2-2
   !r 2-2
   !r 2-2 2-5 6-4 8-9
""",
'what_descr': what_descr,
'coord_descr': commands.parameter(description="x-y: 1-2 11-9"),
'me_descr': commands.parameter(description="don't render what you reported, it's easier to find rest items"),
'ascii': commands.parameter(description="use text map instead of image"),
}