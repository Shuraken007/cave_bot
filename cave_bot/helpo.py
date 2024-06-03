from discord.ext import commands

from .const import cell_aliases_config, color_config_cell_aliases_config, icon_config_cell_aliases_config, map_type_aliases_config, MapType

what_str = ['']
for k, v in cell_aliases_config.items():
   what = f'\t\t{k.name}: ' + ', '.join(v)
   what_str.append(what)
what_descr = commands.parameter(description="\n".join(what_str))

color_config_what_str = ['']
for k, v in color_config_cell_aliases_config.items():
   what = f'\t\t{k}: ' + ', '.join(v)
   color_config_what_str.append(what)
color_config_what_descr = commands.parameter(description="\n".join(color_config_what_str))

icon_config_what_str = ['']
for k, v in icon_config_cell_aliases_config.items():
   what = f'\t\t{k}: ' + ', '.join(v)
   icon_config_what_str.append(what)
icon_config_what_descr = commands.parameter(description="\n".join(icon_config_what_str))

map_level_values = ['']
for map_type in MapType:
   if map_type == MapType.unknown:
      continue
   key = map_type.name
   aliases = map_type_aliases_config[map_type]
   msg = f'\t\t{key}: {aliases}'
   map_level_values.append(msg)
map_level_values = '\n'.join(map_level_values)

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
'color_config_what_descr': color_config_what_descr,
'icon_config_what_descr': icon_config_what_descr,
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
   dreams of any admin - ban hammer, hit them nightmare

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
'reset_description': """
   if new monday detected - all data get and load to new db
""",
'map_level_descr': commands.parameter(description=map_level_values),
'lead_limit': commands.parameter(description="limit output to first N scores"),
'color_descr': """
set color for map cells
!warning: to see effect - unsubscribe from current color_scheme 
`!scheme unsubscribe` -> `!sc un`

!config color summon_stone 153 51 255 100
!config color ss 153 51 255 100
where [153, 51, 255, 100] = [red, green, blue, alpha]

alpha is optional, get from config by default
!config color ss 153 51 255

!config color ss 50
change only alpha to 50%

also hexademical colors supported
!co c art #268BD2 60
!co c art 268bd2 60
!co c art 268bd2

where [268BD2, 60] = [hex_color, alpha]
alpha also is optional

""",
'text_threshold_descr': """
number in [0, 255]

helps to decide - when use dark text, when light

How it works:
   there are lot of colors on map, not possible to have one text color
   so there are 2 text colors:
   light text for dark parts of map
   dark text for light parts of map
   before text printed on map, it check brightness - is it dark or not
   formula: 30% of red + 60% of green + 10% of blue - gives us brightness [0, 255]
   more precisly: r*0.299 + g*0.587 + b*0.114

Example:
   let's have threshold = 60
   we want to put pixel on place with color: [100, 40, 100]
   100*0.299 + 40*0.587 + 100*0.114 = 64.78 = 65
   65 > 60, so we think that this place is too bright, select dark text
""",
'icon_descr': """
turn on / off icons

!config icon idle_reward on
!config icon idle_reward off

!co i i on
!co i en y
!co i ss n
""",
'r': commands.parameter(description="red component in [0, 255]"),
'g': commands.parameter(description="green component in [0, 255]"),
'b': commands.parameter(description="blue component in [0, 255]"),
'alpha': commands.parameter(description="transparency - value [0, 100], 0 - not visible, 100 - absolute visible"),
'hex': commands.parameter(description="""
      example: "#FFFF00" - yellow
      read as r: 'FF' + g: 'FF' + b: 'FF'                          
      FF = 255 at hexadecimal format                 
"""),
'yes_no': commands.parameter(description="""
\t\tpossible values: [y, n, yes, no, on, off, 1, 0, enable, disable, true, false, t ,f]
"""),
'scheme_save': """
save your config as color_scheme

!scheme save my_someScheme
!sch s solarLight
""",
'scheme_search': """
search color_schemes and load what you like

show all schemes:
!scheme search -> !sc se

search by name, name could be not full:
!sc se dark
name could be part of name: `lav` or `lava` vs `lava_light_bright`

search by user:
!sc se @someUser

search by name and user:
!sc @user dark
""",
'scheme_load': """
load color_scheme by user or name
you should specify conditions to get only one scheme

use `!scheme search`, if you don't know what to select

!scheme load @someUser scheme_name
!sc l @oldfag
!sc l dark_groove
!sc l @oldfag dark_groove
""",
'scheme_subscribe': """
subscribe to some scheme
if author change scheme - you'll get effect
your settings not overrided

same syntax as for load
!scheme subscribe @someUser scheme_name
!sc sub @oldfag
!sc su dark_groove
!sc su @oldfag dark_groove

unsubscribe at any moment `!sc unsubscribe`
""",
'scheme_unsubscribe': """
unsubscribe from some color scheme
your settings would be apllying now
""",
'scheme_delete': """
delete color_scheme by name
you should specify conditions to get only one scheme

use `!scheme search`, if you forgot scheme name

!scheme delete my_scheme
!sc d groove_box_light

name could be partial
!sc d gro
"""
}