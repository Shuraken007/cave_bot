#!python3
import discord
from typing import Literal, Optional
from discord.ext import tasks, commands

from dotenv import load_dotenv
import os
import io
from datetime import datetime, timezone

from utils import get_last_monday
from db_init import Db
from db_process import DbProcess
from view import View
from controller import Controller
from myhelp import MyHelp
from const import UserRole as ur, CleanMap
from report import Report
from reaction import process_reactions, Reactions
from parser import Parser
from helpo import help
from logger import Logger
from render.ascii import RenderAscii
from render.image import RenderImage

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

scan_allowed_channel_ids = [int(x) for x in os.getenv('SCAN_ALLOWED_CHANNEL_IDS').split(',')]
allowed_channel_ids = [int(x) for x in os.getenv('ALLOWED_CHANNEL_IDS').split(',')]

class MyBot(commands.Bot):
   async def on_command_error(self, ctx, error):
      if isinstance(error, (commands.CommandError, commands.BadArgument, commands.CheckFailure, commands.CommandNotFound)):
         self.init_ctx(ctx)
         if len(str(error)) > 0:
            ctx.report.add_error(str(error))
            ctx.report.add_log({'exception': str(error)})

         await postprocess(ctx)
      else:
         await super().on_command_error(ctx, error)  # вызывает изначальное поведение on_error_message

   def create_report(self, args = None):
      report = Report()
      report.set_key('default')
      if args is not None and len(args) > 1:
         report.add_log({'args': args[1:]})

      return report

   def init_ctx(self, ctx):
      if hasattr(ctx, 'report'):
         return
      
      ctx.report = self.create_report(ctx.args)

bot = MyBot(command_prefix='!', intents=intents, help_command=commands.DefaultHelpCommand())
bot.help_command = MyHelp(width=1000)
bot.db = None
bot.db_process = None
bot.view = None
bot.parser = None
bot.logger = None
bot.render_ascii = None
bot.render_image = None

async def restart():
   if hasattr(bot, 'model') and hasattr(bot.db_process, 'tmp') and hasattr(bot.db_process.tmp, 'connection'):
      bot.db_process.tmp.connection.close()
   bot.db = Db('db', const_db_name='const', admin_id = os.getenv('ADMIN_ID'))
   bot.db_process = DbProcess(bot.db)
   bot.view = View(bot.db_process)
   bot.controller = Controller(bot.db_process, bot.view)
   bot.parser = Parser()
   bot.logger = Logger('output')
   bot.render_ascii = RenderAscii()
   bot.render_image = RenderImage(2000, 'img', 'output', ['font', 'AlegreyaSC-Regular_384.ttf'], bot)
   await spawn_scan()

@tasks.loop(hours=1)
async def restart_on_monday():
   utc = timezone.utc
   bot.now_day = datetime.now(tz=utc).weekday()

   if bot.now_day == 0 and bot.prev_day is not None and bot.prev_day == 6:
      await restart()
      print('restarted')

   bot.prev_day = bot.now_day

def strict_channels():
   def predicate(ctx):
      bot.init_ctx(ctx)
      if not (
            isinstance(ctx.channel, discord.DMChannel) or
            ctx.channel.id in allowed_channel_ids
         ):
         channel_name = hasattr(ctx.channel, 'name') or type(ctx.channel).__name__
         raise commands.CheckFailure(f"Channel {channel_name} not allowed!")
      return True
   return commands.check(predicate)

def strict_users(min_role):
   def predicate(ctx):
      bot.init_ctx(ctx)
      is_role_ok, err_msg = bot.controller.user_have_role_greater_or_equal(ctx.message.author, min_role, ctx.report)
      if not is_role_ok:
         raise commands.CommandError(err_msg)
         # ctx.report.add_error(err_msg)
         # ctx.report.add_reaction(Reactions.fail)
         return False
      return True
   return commands.check(predicate)

@bot.event
async def on_ready():
   print(f'We have logged in as {bot.user}')
   await restart()

async def spawn_scan():
   for channel_id in scan_allowed_channel_ids:
      channel = bot.get_channel(channel_id)
      ctx = type('',(object,),{"channel": channel, 'report': bot.create_report(), 'message': None})()
      scan_cmd = bot.get_command('scan')
      await scan_cmd(ctx)

      ctx.report.off = True
      await postprocess(ctx)

@strict_channels()
@bot.event
async def on_message(message):
   if message.author == bot.user:
      return
   
   ctx = type('',(object,),{'report': bot.create_report(), 'message': message})()

   bot.parser.parse_msg(ctx, bot)

   await postprocess(ctx)

   await bot.process_commands(message)

@strict_channels()
@strict_users(ur.admin)
@bot.command(hidden=True)
async def scan(ctx, limit=2000):
   ctx.report.off = True

   event_start = get_last_monday()
   last_scan = bot.db_process.get_last_scan() or event_start
   after = max([event_start, last_scan])

   messages = [message async for message in ctx.channel.history(limit=limit, after=after)]

   last_msg_datetime = None
   for msg in messages:
      if msg.author == bot.user:
         continue
      ctx.message = msg
      bot.parser.parse_msg(ctx, bot)
      last_msg_datetime = msg.created_at

   if last_msg_datetime:
      bot.db_process.set_last_scan(last_msg_datetime)

   ctx.report.off = False
   msg = f'scanned {len(messages)} from {after}'
   print(msg)
   ctx.report.add_message(msg)

class CoordsConverter(commands.Converter):
   async def convert(self, ctx: commands.Context, coords: str):
      bot.init_ctx(ctx)
      coords = bot.parser.validate_coords(coords, ctx.report)
      if coords is None:
         raise commands.BadArgument('failed coords')
      
      return coords
    
class AliasConverter(commands.Converter):
   async def convert(self, ctx: commands.Context, alias: str):
      bot.init_ctx(ctx)
      alias = bot.parser.validate_what(alias, ctx.report)
      if alias is None:
         raise commands.BadArgument()
      
      return alias

@bot.before_invoke
async def preprocess(ctx):
   bot.init_ctx(ctx)

@bot.after_invoke
async def postprocess(ctx):
   if not hasattr(ctx, 'report'):
      return
   
   if ctx.report.off is True:
      return
   
   r = ctx.report
   report_keys = r.get_keys()
   keys_len = len(report_keys)
   if 'reactions' in report_keys:
      keys_len -= 1
   if 'default' in report_keys:
      keys_len -= 1
   if reactions:= r.get_reactions():
      await process_reactions(reactions, ctx.message, ctx.report)

   total_msg = []
   for key in r.get_keys():
      key_msg = []
      msg_prefix = None
      if keys_len > 1:
         msg_prefix = key + ': '
         if key == 'reactions':
            msg_prefix = ""

      if messages:= r.get_messages(key):
         key_msg.extend(messages)
      if errors:= r.get_errors(key):
         key_msg.extend(errors)
      if len(key_msg) > 0:
         if msg_prefix is not None:
            total_msg.append(msg_prefix)
            if key != 'reactions':
               key_msg = ["\t" + msg for msg in key_msg]

         total_msg.extend(key_msg)

      if log:= r.get_log(key):
         bot.logger.dump_msg(log, 'log', mode='dump')

   total_msg_str = "\n".join(total_msg)
   if len(total_msg_str) > 0:
      wrapped_msg = ["```ansi", total_msg_str, '```']
      await ctx.message.channel.send("\n".join(wrapped_msg))
   
   for image in r.get_images():
      with io.BytesIO() as image_binary:
         image.save(image_binary, 'PNG')
         image_binary.seek(0)
         await ctx.message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))


class SuperAdminCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@strict_channels()
@strict_users(ur.super_admin)
@bot.command(aliases=['aa'], brief = "add user with admin role - more commands available", description = help['addadmin_description'])
async def adminadd(ctx, users: commands.Greedy[discord.User]):
   for user in users:
      ctx.report.set_key(f'{user.name}')
      bot.controller.add_user_role(user, ur.admin, ctx)

@strict_channels()
@strict_users(ur.super_admin)
@bot.command(aliases=['ad'], brief = "delete user with admin", description = help['deleteadmin_description'])
async def admindelete(ctx, users: commands.Greedy[discord.User]):
   for user in users:
      ctx.report.set_key(f'{user.name}')
      bot.controller.delete_user_role(user, ctx)

@strict_channels()
@strict_users(ur.admin)
@bot.command(aliases=['al'], brief = "list user priveleges", description = help['adminlist_description'])
async def adminlist(ctx):
   await bot.controller.report_user_roles(bot, ctx.report)

@strict_channels()
@strict_users(ur.admin)
@bot.command(aliases=['ba'], brief = "ban user - no interraction with bot", description = help['banadd_description'])
async def banadd(ctx, users: commands.Greedy[discord.User]):
   for user in users:
      ctx.report.set_key(f'{user.name}')
      bot.controller.add_user_role(user, ur.banned, ctx)

@strict_channels()
@strict_users(ur.admin)
@bot.command(aliases=['bd'], brief = "delete user ban", description = help['deleteban_description'])
async def bandelete(ctx, users: commands.Greedy[discord.User]):
   for user in users:
      ctx.report.set_key(f'{user.name}')
      bot.controller.delete_user_role(user, ctx)

@strict_channels()
@strict_users(ur.nobody)
@bot.command(aliases=['a'], brief = "add item by coords", description = help['add_description'])
async def add(ctx, what: AliasConverter = help['what_descr'], coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
   for coord in coords:
      ctx.report.set_key(f'{coord}')
      bot.controller.add(what, coord, ctx)

@strict_channels()
@strict_users(ur.nobody)
@bot.command(aliases=['d'], brief = "deletes your record by coords x-y", description=help['delete_description'])
async def delete(ctx, coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
   for coord in coords:
      ctx.report.set_key(f'{coord}')
      bot.controller.delete(coord, ctx.message.author, ctx)

@strict_channels()
@strict_users(ur.nobody)
@bot.command(aliases=['da'], brief = "deletes all your record")
async def deleteall(ctx):
   ctx.report.add_message(f'Removed coords:')
   bot.controller.report(ctx.message.author, 'c', ctx)
   bot.controller.deleteall(ctx.message.author, ctx)

@strict_channels()
@strict_users(ur.admin)
@bot.command(aliases=['du'], brief = "deletes user record by coords x-y", description=help['deleteuser_description'])
async def deleteuser(ctx, users: commands.Greedy[discord.User], coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
   for user in users:
      ctx.report.set_key(f'{user.name}')
      for coord in coords:
         bot.controller.delete(coord, user, ctx)

@strict_channels()
@strict_users(ur.admin)
@bot.command(aliases=['dau'], brief = "deletes all user records", description=help['deletealluser_description'])
async def deletealluser(ctx, users: commands.Greedy[discord.User]):
   for user in users:
      ctx.report.set_key(f'{user.name}')
      ctx.report.add_message(f'Removed coords:')
      bot.controller.report(user, 'c', ctx)
      bot.controller.deleteall(user, ctx)

@strict_channels()
@strict_users(ur.admin)
@bot.command(aliases=['ru'], brief = "reportes users", description=help['reportusers_description'])
async def reportuser(ctx, users: commands.Greedy[discord.User], c: Optional[Literal['c']] = help['compact_descr'],):
   for user in users:
      ctx.report.set_key(f'{user.name}')
      bot.controller.report(user, c, ctx)

@strict_channels()
@strict_users(ur.nobody)
@bot.command(aliases=['r'], brief = "reportes what you already reported")
async def report(ctx, c: Optional[Literal['c']] = help['compact_descr'],):
   bot.controller.report(ctx.message.author, c, ctx)

@strict_channels()
@strict_users(ur.nobody)
@bot.command(aliases=['c'], brief = "show cell by coords - which item which player reportes")
async def cell(ctx, coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
   for coord in coords:
      ctx.report.set_key(f'{coord}')
      await bot.controller.report_cell(coord, ctx, bot)

@strict_channels()
@strict_users(ur.nobody)
@bot.command(aliases=['m'], brief = "render map as image or text", description = help['map_description'])
async def map(ctx, me: Optional[Literal['me']] = help['me_descr'], ascii: Optional[Literal['ascii']] = help['ascii'], bright: Optional[Literal['b', 'bright']] = help['bright_descr'], clean: Optional[Literal['c', 'clean', 'cc', 'ccc']] = help['clean_descr']):
   if clean is None:
      clean = 'no_clean'
   clean = CleanMap[clean]
   if me:
      me = ctx.message.author.id
   async with ctx.typing():
      if ascii:
         bot.render_ascii.render(me, bot, ctx)
      else:
         bot.render_image.render(me, bright, clean, bot, ctx)

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)