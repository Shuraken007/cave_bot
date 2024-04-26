#!python3
import discord
from typing import Literal, Optional
from discord.ext import tasks, commands
from dotenv import load_dotenv
import os
import io
from db import Db, get_last_monday
from field import Field
from parser import Parser
from datetime import datetime, timezone
from const import scan_allowed_channel_ids, allowed_channel_ids, emoji, FieldType, field_aliases
from helpo import help
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
      elif isinstance(error, commands.CommandNotFound):
         await ctx.send(error)
      else:
         await super().on_command_error(ctx, error)  # вызывает изначальное поведение on_error_message

      if hasattr(ctx, 'log') and getattr(ctx, 'log') is not None:
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

@strict_channels()
@bot.command(aliases=['a'], brief = "add item by coords", description = help['add_description'])
async def add(ctx, what: AliasConverter = help['what_descr'], coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
   for coord in coords:
      ctx.cmd_msg, ctx.cmd_emoji = bot.field.add(what, *coord, bot, ctx.message)

@strict_channels()
@bot.command(aliases=['r'], brief = "removes your record by coords x-y", description=help['remove_description'])
async def remove(ctx, coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
   for coord in coords:
      ctx.cmd_msg, ctx.cmd_emoji = bot.field.remove(*coord, bot.db, ctx.message)

@strict_channels()
@bot.command(aliases=['m'], brief = "render map as image or text")
async def map(ctx, me: Optional[Literal['me']] = help['me_descr'], ascii: Optional[Literal['ascii']] = help['ascii']):
   image = None
   if me:
      me = ctx.message.author.id
   async with ctx.typing():
      if ascii:
         ctx.cmd_msg, ctx.cmd_emoji = bot.render_ascii.render(bot.field, me, bot)
      else:
         image = bot.render_image.render(bot.field, me, bot)

   if image:
      with io.BytesIO() as image_binary:
         image.save(image_binary, 'PNG')
         image_binary.seek(0)
         await ctx.message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)