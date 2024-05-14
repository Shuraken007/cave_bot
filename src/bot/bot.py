#!python3
import inspect
import discord
from discord.ext import tasks, commands
import os

from .bot_util import init_ctx, create_report, get_mock_ctx, \
                     strict_channels, strict_users, response_by_report
from ..utils import get_last_monday
from ..model import generate_models, get_table_names
from ..db_init import Db
from ..db_process import DbProcess
from ..view import View
from ..controller import Controller
from ..const import UserRole as ur, CleanMap
from ..report import Report
from .. import parser
from ..logger import Logger
from ..render.ascii import RenderAscii
from ..render.image import RenderImage

async def preprocess(ctx):
   init_ctx(ctx)
   
async def postprocess(ctx):
   await response_by_report(ctx)

class MyBot(commands.Bot):

   def run(self):
      super(MyBot, self).run(self.config.token)

   def init_db(self):
      table_names = get_table_names()
      models = generate_models(table_names)
      self.db = Db(models, self.config.db_connection_str, admin_id = self.config.admin_id)
      self.db_process = DbProcess(self.db)

   def add_not_registered_self_commands(self):
      members = inspect.getmembers(self)
      for _, member in members:
         if isinstance(member, commands.Command):
               if member.parent is None:
                  self.add_command(member)      

   def __init__(self, *args, 
                  config = None, initial_extensions = [], 
               **kwargs):
      
      super(MyBot, self).__init__(*args, **kwargs)
      self.help_command = commands.DefaultHelpCommand(width=1000)
      self.config = config

      self.db = None
      self.db_process = None
      self.init_db()

      self.view = View(self.db_process)
      self.controller = Controller(self.db_process, self.view)
      self.logger = Logger('output')
      self.render_ascii = RenderAscii()
      self.render_image = RenderImage(2000, 'img', 'output', ['font', 'AlegreyaSC-Regular_384.ttf'], self)

      self.initial_extensions = initial_extensions

      self.on_ready = self.event(self.on_ready)
      self.on_message = self.event(self.on_message)
      self._before_invoke = preprocess
      self._after_invoke = postprocess
      self.add_not_registered_self_commands()

   def reinit(self):
      self.init_db()
      self.controller.init_view()
      self.render_image.reset_storage()

   async def on_command_error(self, ctx, error):
      if isinstance(error, (commands.CommandError, commands.BadArgument, commands.CheckFailure, commands.CommandNotFound)):
         await preprocess(ctx)
         if len(str(error)) > 0:
            ctx.report.err.add(str(error))
            ctx.report.log.add({'exception': str(error)})

         await postprocess(ctx)
      else:
         await super().on_command_error(ctx, error)  # вызывает изначальное поведение on_error_message

   # async def loadcog(self):
   #    for cog in os.listdir(".\cogs"):
   #       if cog.endswith(".py"):
   #             try:
   #                cog = f"cogs.{cog.replace('.py', '')}"
   #                await self.load_extension(cog)
   #                print("Loaded:\t", cog)
   #             except Exception as e:
   #                print(f'An error occoured in the main file, {cog} cog, error {e}')

   async def on_ready(self):
      print(f'We have logged in as {self.user}')
      # await self.loadcog()
      for extension in self.initial_extensions:
         await self.load_extension(extension)

      await self.spawn_scan()

   async def spawn_scan(self):
      for channel_id in self.config.scan_allowed_channel_ids:
         channel = self.get_channel(channel_id)
         mock_ctx = get_mock_ctx({"channel": channel, 'message': None, 'bot': self})

         await preprocess(mock_ctx)
         
         scan_cmd = self.get_command('scan')
         await scan_cmd(mock_ctx)

         mock_ctx.report.off = True
         await postprocess(mock_ctx)

   @strict_channels()
   @strict_users(ur.admin)
   @commands.command(hidden=True)
   async def scan(ctx, limit=2000):
      self = ctx.bot
      ctx.report.off = True

      event_start = get_last_monday()
      last_scan = self.db_process.get_last_scan() or event_start
      after = max([event_start, last_scan])

      messages = [message async for message in ctx.channel.history(limit=limit, after=after)]

      last_msg_datetime = None
      for msg in messages:
         if msg.author == self.user:
            continue
         ctx.message = msg
         parser.parse_msg(ctx, self)
         last_msg_datetime = msg.created_at

      if last_msg_datetime:
         self.db_process.set_last_scan(last_msg_datetime)

      ctx.report.off = False
      msg = f'scanned {len(messages)} from {after}'
      print(msg)
      ctx.report.msg.add(msg)


