#!python3
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
import os
import io
from db import Db, get_last_monday
from field import Field
from parser import Parser
from datetime import datetime, timezone
from const import scan_allowed_channel_ids, allowed_channel_ids, field_aliases
from logger import Logger
from render.ascii import RenderAscii
from render.image import RenderImage
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.db = None
bot.field = None
bot.parser = None
bot.logger = None
bot.render_ascii = None
bot.render_image = None

async def spawn_scan():
   guild = discord.utils.get(bot.guilds, name="MksiDev Games")
   for channel_id in scan_allowed_channel_ids:
      channel = bot.get_channel(channel_id)
      ctx = type('',(object,),{"channel": channel})()
      scan_cmd = bot.get_command('scan')
      await scan_cmd(ctx)

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

@bot.event
async def on_ready():
   print(f'We have logged in as {bot.user}')
   await restart()

@bot.event
async def on_message(message):
   sending_message = bot.parser.parse_msg(message, bot)
   if sending_message:
      await message.channel.send(sending_message)

   await bot.process_commands(message)

@bot.command()
async def scan(ctx, limit=200):
   if ctx.channel.id not in allowed_channel_ids:
      return
   
   event_start = get_last_monday()
   last_scan = bot.db.get_last_scan() or event_start
   after = max([event_start, last_scan])

   messages = [message async for message in ctx.channel.history(limit=limit, after=after)]

   last_msg_datetime = None
   for msg in messages:
      bot.parser.parse_msg(msg, bot)
      last_msg_datetime = msg.created_at

   if last_msg_datetime:
      bot.db.set_last_scan(last_msg_datetime)
   print(f'scanned {len(messages)} from {after}')


@bot.command(aliases=['a'])
async def add(ctx, alias, coords):
   if ctx.channel.id not in allowed_channel_ids:
      return

   report = {'add_request': f'alias: {alias}, coords: {coords}'}
   alias = bot.parser.validate_alias(alias, report)
   x, y = bot.parser.validate_coords(coords, report)

   if not (alias and x and y):
      bot.logger.dump_msg(report, 'log', mode='dump')
      return

   sending_message = bot.field.add(alias, x, y, bot, ctx.message)
   if sending_message:
      await ctx.message.channel.send(sending_message)

@bot.command(aliases=['r'])
async def remove(ctx, coords):
   if ctx.channel.id not in allowed_channel_ids:
      return

   report = {'remove_request': f'coords: {coords}'}
   x, y = bot.parser.validate_coords(coords, report)

   if not (x and y):
      bot.logger.dump_msg(report, 'log', mode='dump')
      return

   sending_message = bot.field.remove(x, y, bot.db, ctx.message)
   if sending_message:
      await ctx.message.channel.send(sending_message)
      
@bot.command(aliases=['s'])
async def show(ctx):
   if ctx.channel.id not in allowed_channel_ids:
      return

   sending_message = bot.render_ascii.render(bot.field)
   if sending_message:
      await ctx.message.channel.send(sending_message)

@bot.command(aliases=['m'])
async def map(ctx):
   if ctx.channel.id not in allowed_channel_ids:
      return

   image = bot.render_image.render(bot.field)
   if image:
      with io.BytesIO() as image_binary:
         image.save(image_binary, 'PNG')
         image_binary.seek(0)
         await ctx.message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)