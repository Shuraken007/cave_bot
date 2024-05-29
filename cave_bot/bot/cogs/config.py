import discord
from discord.ext import commands
from typing import Literal, Optional

from ...const import UserRole as ur, map_type_aliases
from ...helpo import help
from ..bot_util import strict_channels, strict_users
from ..converter import ColorConverter, ColorConfigAliasConverter, IconConfigAliasConverter

class ConfigCog(commands.Cog, name='Settings', description = "Config commands - your settings"):

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
	async def map(self, ctx, level: Literal['Normal', 'n', '1', '20', 'easy', 'Hard', 'h', '2', '25', 'normal', 'Nightmare', 'nm', '3', '30', 'hard']  = help['map_level_descr']):
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

	@strict_channels()
	@strict_users(ur.nobody)
	@config.command(aliases=['c'], brief = "change color", description = help['color_descr'])
	async def color(self, ctx, what: ColorConfigAliasConverter = help['color_config_what_descr'], r: Optional[int] = help['r'], g: Optional[int] = help['g'], b: Optional[int] = help['b'], hex: Optional[str] = help['hex'], alpha: Optional[int] = help['alpha']):
		arr = []
		for x in [r, g, b, alpha]:
			if x is None:
				continue
			arr.append(x)
		color = ColorConverter().convert(ctx, arr, hex)
		self.bot.controller.set_config_color(what, color, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@config.command(aliases=['i'], brief = "icon show or not", description = help['icon_descr'])
	async def icon(self, ctx, what: IconConfigAliasConverter = help['icon_config_what_descr'], yes_no: bool = help['yes_no']):
		key = f'{what}_icon'
		self.bot.controller.set_config(key, yes_no, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@config.command(brief = "copy config from another user")
	async def copy(self, ctx, user: discord.User):
		self.bot.controller.copy_config(user, ctx)

async def setup(bot):
	await bot.add_cog(ConfigCog(bot))