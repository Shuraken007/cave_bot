#!python3
import inspect
import discord
from discord.ext import commands, tasks
import os
import traceback

from .bot_util import init_ctx, MyCommandError, \
                     strict_channels, strict_users, response_by_report
from ..utils import get_last_monday, get_week_start_as_str, get_mock_class_with_attr, \
                     profile_start, profile_end
from ..model import generate_models, get_table_names
from ..db_init import Db
from ..db_process import DbProcess
from ..controller import Controller
from ..const import UserRole as ur
from .. import parser
from ..helpo import help
from ..logger import Logger
from ..render.ascii import RenderAscii
from ..render.image import RenderImage

async def preprocess(ctx):
   init_ctx(ctx)
   ctx.bot.reset(ctx)
   if ctx.bot.is_profile:
      profile_start(ctx)
   # ctx.bot.db_process.start_session()

async def postprocess(ctx):
   if ctx.bot.is_profile and ctx.bot.pr:
      profile_end(ctx)

   await response_by_report(ctx)
   # ctx.bot.db_process.end_session()

class MyBot(commands.Bot):

   def run(self):
      super(MyBot, self).run(self.config.token)

   def init_db(self):
      week_postfix, table_names = get_table_names()
      models = generate_models(table_names)
      self.db = Db(models, self.config.db_connection_str, admin_id = self.config.admin_id)
      self.db_process = DbProcess(self.db)
      self.week_postfix = week_postfix

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
      self.help_command = commands.DefaultHelpCommand(
         width=1000, 
         no_category = 'Default',
         command_attrs = {'aliases': ['h']}
      )
      self.config = config

      self.db = None
      self.db_process = None
      self.init_db()

      self.controller = Controller(self.db_process)
      self.logger = Logger('output')
      self.render_ascii = RenderAscii()
      self.render_image = RenderImage(2000, 'img', 'output', ['font', 'AlegreyaSC-Regular_384.ttf'], self)

      self.initial_extensions = initial_extensions

      self.is_profile = False
      self.pr = None

      # this part typically solved with decorators like `@bot.event`
      # but it required MyBot instance, which is bad design
      self.on_ready = self.event(self.on_ready)
      self.on_message = self.event(self.on_message)
      self._before_invoke = preprocess
      self._after_invoke = postprocess
      self.add_not_registered_self_commands()

   def reset_view(self):
      self.controller = Controller(self.db_process)
      self.render_image.reset_storage()

   def reset(self, ctx):
      if self.week_postfix != get_week_start_as_str():
         self.dump_memory_db_to_connection()
         self.db.memory_db.dispose()
         self.init_db()
         self.reset_view()
         ctx.report.set_key('Info')
         ctx.report.msg.add('Restarted, reseted week!!!\n')

   async def on_command_error(self, ctx, error):
      if isinstance(error, (MyCommandError, commands.BadArgument, commands.CheckFailure, commands.CommandNotFound)):
         await preprocess(ctx)
         if len(str(error)) > 0:
            # trace = traceback.TracebackException.from_exception(error)
            # trace_str = ''.join(trace.format())
            # ctx.report.err.add(trace_str)
            ctx.report.err.add(str(error))
            ctx.report.log.add({'exception': str(error)})

         await postprocess(ctx)
      else:
         await super().on_command_error(ctx, error)  # вызывает изначальное поведение on_error_message

   # override for help
   # !h user | !h User
   def get_cog(self, name):
      all_keys = self.cogs.keys()
      for k in all_keys:
         if k.lower() == name.lower():
            return super().get_cog(k)

      return super().get_cog(name)

   async def on_ready(self):
      print(f'We have logged in as {self.user}')
      for extension in self.initial_extensions:
         await self.load_extension(extension)

      await self.spawn_scan()

      if not self.dump_memory_db_to_connection.is_running():
         self.dump_memory_db_to_connection.start()      

   async def on_message(self, message):
      if message.author == self.user:
         return
         
      mock_ctx = get_mock_class_with_attr({"channel": message.channel, 'message': message, 'bot': self})
      await preprocess(mock_ctx)
      
      parser.parse_msg(mock_ctx, self)      
      await postprocess(mock_ctx)

      await self.process_commands(message)

      last_msg_datetime = message.created_at

      if last_msg_datetime:
         self.db_process.set_last_scan(last_msg_datetime)

   # spawn_scan must imitate hard run of command "!scan"
   async def spawn_scan(self):
      for channel_id in self.config.scan_allowed_channel_ids:
         channel = self.get_channel(channel_id)
         if channel is None:
            continue
         mock_ctx = get_mock_class_with_attr({"channel": channel, 'message': None, 'bot': self, })

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
      ctx.report.set_key('Info')
      ctx.report.msg.add(msg)
      print(msg)

   async def get_user_name_by_id(self, user_id):
      user_id = int(user_id)
      
      user = self.get_user(user_id)
      if user is None:
         try:
            user = await self.fetch_user(user_id)
         except:
            pass
      if user is None:
         return f'unknown name ({user_id} id)'
      name = user.global_name
      if name is None:
         name = user.name
      if name is None:
         name = str(user_id)
      return name

   @tasks.loop(minutes=30.0)
   async def dump_memory_db_to_connection(self):
      self.db.save_to_load_db()
      print('dumped')
