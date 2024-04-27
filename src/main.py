#!python3
import discord
from typing import Literal, Optional
from discord.ext import tasks, commands

from dotenv import load_dotenv
import os
import io
from datetime import datetime, timezone

from model import Model, get_last_monday
from view import View
from controller import Controller

from const import scan_allowed_channel_ids, allowed_channel_ids
from report import Report
from emoji import add_emoji
from parser import Parser
from helpo import help
from logger import Logger
from render.ascii import RenderAscii
from render.image import RenderImage

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
   async def on_command_error(self, ctx, error):
      if isinstance(error, (commands.BadArgument, commands.CheckFailure, commands.CommandNotFound)):
         self.init_ctx(ctx)
         if len(str(error)) > 0:
            ctx.report.add_error(str(error))
            ctx.report.add_log({'exception': str(error)})

         await postprocess(ctx)
      else:
         await super().on_command_error(ctx, error)  # вызывает изначальное поведение on_error_message

   def init_ctx(self, ctx):
      if hasattr(ctx, 'report'):
         return
      
      ctx.report = Report()
      ctx.report.set_key('1')
      if len(ctx.args) > 1:
         ctx.report.add_log({'args': ctx.args[1:]})

bot = MyBot(command_prefix='!', intents=intents)
bot.model = None
bot.view = None
bot.parser = None
bot.logger = None
bot.render_ascii = None
bot.render_image = None

async def restart():
   if bot.model is not None:
      bot.model.connection.close()
   bot.model = Model('db')
   bot.view = View(bot.model)
   bot.controller = Controller(bot.model, bot.view)
   bot.parser = Parser()
   bot.logger = Logger('output')
   bot.render_ascii = RenderAscii()
   bot.render_image = RenderImage(2000, 'img', 'output', ['font', 'AlegreyaSC-Regular_384.ttf'])
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
      if ctx.channel.id not in allowed_channel_ids:
         raise commands.CheckFailure(f"Channel {ctx.channel.name} not allowed!")
      return True
   return commands.check(predicate)

@bot.event
async def on_ready():
   print(f'We have logged in as {bot.user}')
   await restart()

async def spawn_scan():
   guild = discord.utils.get(bot.guilds, name="MksiDev Games")
   for channel_id in scan_allowed_channel_ids:
      channel = bot.get_channel(channel_id)
      ctx = type('',(object,),{"channel": channel, 'report': Report()})()
      ctx.report.set_key('1')
      scan_cmd = bot.get_command('scan')
      await scan_cmd(ctx)

      ctx.report.off = True
      await postprocess(ctx)

@strict_channels()
@bot.event
async def on_message(message):
   if message.author == bot.user:
      return
   
   ctx = type('',(object,),{'report': Report(), 'message': message})()
   ctx.report.set_key('1')

   bot.parser.parse_msg(message, bot, ctx.report)

   await postprocess(ctx)

   await bot.process_commands(message)

@strict_channels()
@bot.command(hidden=True)
async def scan(ctx, limit=2000):
   ctx.report.off = True

   event_start = get_last_monday()
   last_scan = bot.model.get_last_scan() or event_start
   after = max([event_start, last_scan])

   messages = [message async for message in ctx.channel.history(limit=limit, after=after)]

   last_msg_datetime = None
   for msg in messages:
      if msg.author == bot.user:
         continue
      bot.parser.parse_msg(msg, bot, ctx.report)
      last_msg_datetime = msg.created_at

   if last_msg_datetime:
      bot.model.set_last_scan(last_msg_datetime)

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
   keys_len = len(r.get_keys())
   
   if reactions:= r.get_reactions():
      for reaction, value in reactions.items():
         await add_emoji(reaction, value, ctx.message)

   for key in r.get_keys():
      total_msg = ""
      msg_prefix = ""
      if keys_len > 1:
         msg_prefix = key + ': '

      if messages:= r.get_messages(key):
         total_msg += msg_prefix +"\n".join(messages)
      if errors:= r.get_errors(key):
         total_msg += msg_prefix +"\n".join(errors)
      if len(total_msg) > 0:
         await ctx.message.channel.send(total_msg)

      if log:= r.get_log(key):
         bot.logger.dump_msg(log, 'log', mode='dump')

@strict_channels()
@bot.command(aliases=['a'], brief = "add item by coords", description = help['add_description'])
async def add(ctx, what: AliasConverter = help['what_descr'], coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
   for coord in coords:
      bot.controller.add(what, coord, ctx.message, ctx.report)

@strict_channels()
@bot.command(aliases=['d'], brief = "deletes your record by coords x-y", description=help['delete_description'])
async def delete(ctx, coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
   for coord in coords:
      bot.controller.delete(coord, ctx.message, ctx.report)

@strict_channels()
@bot.command(aliases=['r'], brief = "reportes what you already reported")
async def report(ctx, c: Optional[Literal['c']] = help['compact_descr'],):
   bot.controller.report(c, ctx.message, ctx.report)

@strict_channels()
@bot.command(aliases=['m'], brief = "render map as image or text", description = help['map_description'])
async def map(ctx, me: Optional[Literal['me']] = help['me_descr'], ascii: Optional[Literal['ascii']] = help['ascii']):
   image = None
   if me:
      me = ctx.message.author.id
   async with ctx.typing():
      if ascii:
         bot.render_ascii.render(bot.view, me, bot, ctx.report)
      else:
         image = bot.render_image.render(bot.view, me, bot)

   if image:
      with io.BytesIO() as image_binary:
         image.save(image_binary, 'PNG')
         image_binary.seek(0)
         await ctx.message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)