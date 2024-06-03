import discord
from discord.ext import commands
from typing import Literal, Optional

from ...const import UserRole as ur, map_type_aliases
from ...helpo import help
from ..bot_util import strict_channels, strict_users
from ..converter import ColorConverter, ColorConfigAliasConverter, IconConfigAliasConverter

class ColorSchemeCog(commands.Cog, name='ColorScheme', description = "Config commands - your settings"):

	def __init__(self, bot):
		self.bot = bot

	@strict_channels()
	@strict_users(ur.nobody)
	@commands.group(aliases=['sc', 'sch'], brief = "manage color schemes")
	async def scheme(self, ctx):
		if ctx.invoked_subcommand is None:
			ctx.report.msg.add(f'use `!h scheme` to check subcommands')

	@strict_channels()
	@strict_users(ur.nobody)
	@scheme.command(aliases=['s'], brief = "save your current scheme to db", description = help['scheme_save'])
	async def save(self, ctx, name: str):
		self.bot.controller.save_scheme(name, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@scheme.command(aliases=['d'], brief = "delete scheme from db by name", description = help['scheme_delete'])
	async def delete(self, ctx, name: str):
		await self.bot.controller.delete_scheme(name, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@scheme.command(aliases=['se'], brief = "search color_schemes and load what you like, embeds", description = help['scheme_search'])
	async def search(self, ctx, user: Optional[discord.User], name: Optional[str]):
		await self.bot.controller.search_scheme(user, name, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@scheme.command(aliases=['set'], brief = "search color_schemes and load what you like, text table", description = help['scheme_search'])
	async def search_table(self, ctx, user: Optional[discord.User], name: Optional[str]):
		await self.bot.controller.search_as_table_scheme(user, name, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@scheme.command(aliases=['l'], brief = "load/copy scheme to config", description = help['scheme_load'])
	async def load(self, ctx, user: Optional[discord.User], name: Optional[str]):
		await self.bot.controller.load_scheme(user, name, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@scheme.command(aliases=['su', 'sub'], brief = "subscribe to scheme", description = help['scheme_subscribe'])
	async def subscribe(self, ctx, user: Optional[discord.User], name: Optional[str]):
		await self.bot.controller.subscribe_scheme(user, name, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@scheme.command(aliases=['un', 'unsu', 'unsub'], brief = "unsubscribe scheme", description = help['scheme_unsubscribe'])
	async def unsubscribe(self, ctx):
		await self.bot.controller.unsubscribe_scheme(ctx)

async def setup(bot):
	await bot.add_cog(ColorSchemeCog(bot))