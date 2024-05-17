from discord.ext import commands
from typing import Literal

from ...const import UserRole as ur, map_type_aliases
from ...helpo import help
from ..bot_util import strict_channels, strict_users

class ConfigCog(commands.Cog, name='Config', description = "Config commands - your settings"):

	def __init__(self, bot):
		self.bot = bot

	@strict_channels()
	@strict_users(ur.nobody)
	@commands.group(aliases=['conf', 'co'], brief = "manage your settings")
	async def config(self, ctx):
		if ctx.invoked_subcommand is None:
			self.bot.controller.show_config(ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@config.command(aliases=['r'], brief = "reset config to default")
	async def reset(self, ctx):
		self.bot.controller.reset_config(ctx)
			
	@strict_channels()
	@strict_users(ur.nobody)
	@config.command(aliases=['m'], brief = "select map difficulty")
	async def map(self, ctx, level: Literal['easy', 'normal', 'hard', 'e', 'n', 'h', '20', '25', '30', '1', '2', '3']  = help['map_level_descr']):
		map_type = None
		if map_type := map_type_aliases.get(level):
			self.bot.controller.set_config('map_type', map_type, ctx)
		else:
			ctx.report.err.add(f'something gone wrong, unknown map level "{level}"')

	@strict_channels()
	@strict_users(ur.nobody)
	@config.command(aliases=['d'], brief = "delete config from database")
	async def delete(self, ctx):
		self.bot.controller.delete_config(ctx)

async def setup(bot):
	await bot.add_cog(ConfigCog(bot))