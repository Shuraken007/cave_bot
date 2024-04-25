#!python3
import discord
from typing import Literal
from discord.ext import tasks, commands
from dotenv import load_dotenv
import os
import io
from db import Db, get_last_monday
from field import Field
from parser import Parser
from datetime import datetime, timezone
from const import scan_allowed_channel_ids, allowed_channel_ids, emoji, FieldType, field_aliases
from logger import Logger
from render.ascii import RenderAscii
from render.image import RenderImage
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
   async def on_command_error(self, ctx, error):
      if isinstance(error, commands.BadArgument):
         await ctx.send(f"Wrong Argument: {error}")
      elif isinstance(error, commands.CheckFailure):
         await ctx.send(error)
      else:
         await super().on_command_error(ctx, error)  # вызывает изначальное поведение on_error_message

      if ctx.log is not None:
         ctx.log['error'] = str(error)
         bot.logger.dump_msg(ctx.log, 'log', mode='dump')


bot = MyBot(command_prefix='!', intents=intents)
bot.db = None
bot.field = None
bot.parser = None
bot.logger = None
bot.render_ascii = None
bot.render_image = None

async def restart():
   if bot.db is not None:
      bot.db.connection.close()
   bot.db = Db('db')
   bot.field = Field(bot.db)
   bot.parser = Parser()
   bot.logger = Logger('output')
   bot.render_ascii = RenderAscii()
   bot.render_image = RenderImage(2000, 'img', 'output', ['font', 'AlegreyaSC-Regular_384.ttf'])
   await spawn_scan()
   print('restarted')

@tasks.loop(hours=1)
async def restart_on_monday():
   utc = timezone.utc
   bot.now_day = datetime.now(tz=utc).weekday()

   if bot.now_day == 0 and bot.prev_day is not None and bot.prev_day == 6:
      await restart()

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
      ctx = type('',(object,),{"channel": channel, 'log': [], 'cmd_msg': None, 'cmd_emoji': None})()
      scan_cmd = bot.get_command('scan')
      await scan_cmd(ctx)

      await postprocess(ctx)

@strict_channels()
@bot.event
async def on_message(message):
   if message.author == bot.user:
      return
   
   ctx = type('',(object,),{'log': [], 'cmd_msg': None, 'cmd_emoji': None})()
   ctx.cmd_msg, ctx.cmd_emoji = bot.parser.parse_msg(message, ctx, bot)

   await postprocess(ctx)

   await bot.process_commands(message)

@strict_channels()
@bot.command()
async def scan(ctx, limit=200):
   event_start = get_last_monday()
   last_scan = bot.db.get_last_scan() or event_start
   after = max([event_start, last_scan])

   messages = [message async for message in ctx.channel.history(limit=limit, after=after)]

   last_msg_datetime = None
   for msg in messages:
      if msg.author == bot.user:
         continue
      ctx.cmd_msg, ctx.cmd_emoji = bot.parser.parse_msg(msg, ctx, bot)
      last_msg_datetime = msg.created_at

   if last_msg_datetime:
      bot.db.set_last_scan(last_msg_datetime)

   print(f'scanned {len(messages)} from {after}')

class CoordsConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, coords: str):
      x, y, err_msg = bot.parser.validate_coords(coords, bot)
      if x is None or y is None:
         await ctx.message.add_reaction(emoji['no'])
         raise commands.BadArgument(message=err_msg)
      
      return [x, y]
    
class AliasConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, alias: str):
      alias, err_msg = bot.parser.validate_alias(alias)
      if alias is None:
         await ctx.message.add_reaction(emoji['no'])
         raise commands.BadArgument(message=err_msg)
      
      return alias

@bot.before_invoke
async def preprocess(ctx):
   ctx.log = {}
   if len(ctx.args) > 1:
      ctx.log = {'args': ctx.args[1:]}
      

@bot.after_invoke
async def postprocess(ctx):
   if hasattr(ctx, 'cmd_msg') and getattr(ctx, 'cmd_msg'):
      await ctx.message.channel.send(ctx.cmd_msg)
   if hasattr(ctx, 'cmd_emoji') and getattr(ctx, 'cmd_emoji'):
      await ctx.message.add_reaction(ctx.cmd_emoji)
   if (type(ctx.log) == dict and ctx.log.get("error") is not None) or \
      (type(ctx.log) == list and len(ctx.log) > 0):
      bot.logger.dump_msg(ctx.log, 'log', mode='dump')

coord_descr = commands.parameter(description="x-y: 1-2 11-9")


def grouped(iterable, n):
    return zip(*[iter(iterable)]*n)
what_str = []
for a1, a2, a3, a4, a5, a6, a7, a8 in grouped(field_aliases.keys(), 8):
   what_str.append(' | '.join([a1, a2, a3, a4, a5, a6, a7, a8]))
what_str = "\n".join(what_str)
what_descr = commands.parameter(description=what_str)

add_description = """
   add item by coords:
   !a empty 3-5 | !a e 3-5
   !a "idle reward" 6-8 | !a i 6-8
   !add "summon stone" 2-1 3-4 8-12
   !a ss 2-1 3-4 8-12
"""

@strict_channels()
@bot.command(aliases=['a'], brief = "add item by coords", description = add_description)
async def add(ctx, what: AliasConverter = what_descr, coords: commands.Greedy[CoordsConverter] = coord_descr):
   for coord in coords:
      ctx.cmd_msg, ctx.cmd_emoji = bot.field.add(what, *coord, bot, ctx.message)


remove_description = """
   if you gave wrong info, you can remove it:
   !remove 2-2
   !r 2-2
   !r 2-2 2-5 6-4 8-9
"""
@strict_channels()
@bot.command(aliases=['r'], brief = "removes your record by coords x-y", description=remove_description)
async def remove(ctx, coords: commands.Greedy[CoordsConverter] = coord_descr):
   for coord in coords:
      ctx.cmd_msg, ctx.cmd_emoji = bot.field.remove(*coord, bot.db, ctx.message)

@strict_channels()
@bot.command(aliases=['s'], brief = "render map as ascii text")
async def show(ctx):
   ctx.cmd_msg, ctx.cmd_emoji = bot.render_ascii.render(bot.field)

@strict_channels()
@bot.command(aliases=['m'], brief = "render map as high rez image")
async def map(ctx):
   image = None
   async with ctx.typing():
      image = bot.render_image.render(bot.field)

   if image:
      with io.BytesIO() as image_binary:
         image.save(image_binary, 'PNG')
         image_binary.seek(0)
         await ctx.message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)