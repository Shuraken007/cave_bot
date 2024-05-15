from discord.ext import commands
from typing import Literal, Optional

from ...const import UserRole as ur, CleanMap
from ...helpo import help
from ..converter import CoordsConverter, AliasConverter
from ... import parser
from ..bot_util import strict_channels, strict_users

class UserCog(commands.Cog, name='User', description = "User commands - manipulate with your own data"):

	def __init__(self, bot):
		self.bot = bot

	@strict_channels()
	@strict_users(ur.nobody)
	@commands.command(aliases=['a'], brief = "add item by coords", description = help['add_description'])
	async def add(self, ctx, what: AliasConverter = help['what_descr'], coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
		for coord in coords:
			ctx.report.set_key(f'{coord}')
			self.bot.controller.add(what, coord, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@commands.command(aliases=['d'], brief = "deletes your record by coords x-y", description=help['delete_description'])
	async def delete(self, ctx, coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
		for coord in coords:
			ctx.report.set_key(f'{coord}')
			self.bot.controller.delete(coord, ctx.message.author, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@commands.command(aliases=['da'], brief = "deletes all your record")
	async def deleteall(self, ctx):
		ctx.report.msg.add(f'Removed coords:')
		self.bot.controller.report(ctx.message.author, 'c', ctx)
		self.bot.controller.deleteall(ctx.message.author, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@commands.command(aliases=['r'], brief = "reportes what you already reported")
	async def report(self, ctx, c: Optional[Literal['c']] = help['compact_descr'],):
		self.bot.controller.report(ctx.message.author, c, ctx)

	@strict_channels()
	@strict_users(ur.nobody)
	@commands.command(aliases=['c'], brief = "show cell by coords - which item which player reportes")
	async def cell(self, ctx, coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
		for coord in coords:
			ctx.report.set_key(f'{coord}')
			await self.bot.controller.report_cell(coord, ctx, self.bot)

	@strict_channels()
	@strict_users(ur.nobody)
	@commands.command(aliases=['m'], brief = "render map as image or text", description = help['map_description'])
	async def map(self, ctx, me: Optional[Literal['me']] = help['me_descr'], ascii: Optional[Literal['ascii']] = help['ascii'], bright: Optional[Literal['b', 'bright']] = help['bright_descr'], clean: Optional[Literal['c', 'clean', 'cc', 'ccc']] = help['clean_descr']):
		if clean is None:
			clean = 'no_clean'
		clean = CleanMap[clean]
		if me:
			me = ctx.message.author.id
		async with ctx.typing():
			if ascii:
				self.bot.render_ascii.render(me, self.bot, ctx)
			else:
				self.bot.render_image.render(me, bright, clean, self.bot, ctx)


async def setup(bot):
	await bot.add_cog(UserCog(bot))