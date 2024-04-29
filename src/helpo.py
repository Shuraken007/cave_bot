from discord.ext import commands
from const import cell_aliases

def grouped(iterable, n):
    return zip(*[iter(iterable)]*n)
what_str = []
for a1, a2, a3, a4, a5, a6, a7, a8 in grouped(cell_aliases.keys(), 8):
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
'delete_description': """
   if you gave wrong info, you can delete it:
   !delete 2-2
   !d 2-2
   !d 2-2 2-5 6-4 8-9
""",
'deleteuser_description': """
   same as !delete , but with specifying users:
   !delete @user1 2-2
   !d @user1 2-2
   !d @user1 @user2 2-2 2-5 6-4 8-9
""",
'deletealluser_description': """
   just delete all user records
   !deletealluser @user1
   !dau @user1
   !dau @user1 @user2
""",
'what_descr': what_descr,
'coord_descr': commands.parameter(description="x-y: 1-2 11-9"),
'me_descr': commands.parameter(description="don't render what you reported, it's easier to find rest items"),
'ascii': commands.parameter(description="use text map instead of image"),
'compact_descr': commands.parameter(description="make report Compact"),
'map_description': """
   !map
   !map me
   !map ascii
   !map me ascii
""",
'addadmin_description': """
   add user with admin role - more commands available
   * check any users reports
   * find liars
   * remove users data
   * ban users for bot

   !addadmin @DearFreeHelper
   !aa @FirstUser @SecondUser
""",
'banadd_description': """
   dreams of any admin - ban hammer, hit them hard

   !banadd @SillyDebater
   !ba @SillyDebater @SmartAss5
""",
'deleteban_description': """
   unban somebody

   !bandelete @LuckyFirst
   !ba @BribeGiver3 @JudgeAcquitted2
""",
'deleteadmin_description': """
   delete user from admins
   !admindelete @SmartAss
   !ad @noname1 @noname2
""",
'adminlist_description': """
   check admin names and privilege lvl
""",
'cell_descr': """
   show cell by coords - which item which player reportes
   helps to search - who added wrong data
   !cell 5-3
   !c 5-3 6-7 9-1
""",
'reportusers_description': """
   report what users reported
   !reportuser @user1
   !ru @user1, @user2
   !ru @user1, @user2 c
      where c - compact
""",
}