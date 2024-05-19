import discord
from discord import DMChannel
from discord.ext import commands
import io

from ..report import Report
from ..reaction import process_reactions
from ..utils import build_sending_msg_arr_consider_constraint

def init_ctx(ctx):
   if hasattr(ctx, 'report'):
      return
   ctx.report = create_report(getattr(ctx, 'args', None))

def create_report(args = None):
   report = Report()
   if args is not None and len(args) > 1:
      report.log.add({'args': args[1:]})

   return report

async def response_by_report(ctx):
   if not hasattr(ctx, 'report'):
      return
   
   if ctx.report.off is True:
      return
   
   bot = ctx.bot
   r = ctx.report

   # process reactions first, cause they add messages
   if reactions:= r.reaction.get():
      emoji_arr = process_reactions(reactions, ctx.report)
      for emoji in emoji_arr:
         await ctx.message.add_reaction(emoji)

   msg_arr = r.build_msg_arr()
   send_msg_arr = build_sending_msg_arr_consider_constraint(msg_arr)

   for msg in send_msg_arr:
      wrapped_msg = "```ansi\n" + msg + "\n```"
      await ctx.message.channel.send(wrapped_msg)
   
   if image_arr:= r.image.get():
      for image in image_arr:
         with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
            image.close()

   r.dump_to_logger(bot.logger)
   ctx.report = Report()
   
def strict_channels_f(ctx):
   init_ctx(ctx)
   bot = ctx.bot
   if not (
         isinstance(ctx.channel, DMChannel) or
         ctx.channel.id in bot.config.allowed_channel_ids
      ):
      channel_name = getattr(ctx.channel, 'name', type(ctx.channel).__name__)
      raise commands.CommandError(f"Channel {channel_name} not allowed!")
   return True

def strict_users_f(ctx, min_role):
   bot = ctx.bot
   init_ctx(ctx)
   is_role_ok, err_msg = bot.controller.role.user_have_role_greater_or_equal(ctx.message.author, min_role, ctx.report)
   if not is_role_ok:
      raise commands.CommandError(err_msg)
   return True

def strict_channels():
   def predicate(ctx):
      return strict_channels_f(ctx)
   return commands.check(predicate)

def strict_users(min_role):
   def predicate(ctx):
      return strict_users_f(ctx, min_role)
   return commands.check(predicate)

    