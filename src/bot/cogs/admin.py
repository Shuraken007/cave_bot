import discord
from discord.ext import commands
from typing import Literal, Optional

from ...const import UserRole as ur
from ...helpo import help
from ..converter import CoordsConverter
from ..bot_util import strict_channels, strict_users


class AdminCog(commands.Cog, name='Admin', description = "Admin commands - manipulate with other users data"):

    def __init__(self, bot):
        self.bot = bot
    
    @strict_channels()
    @strict_users(ur.admin)
    @commands.command(aliases=['al'], brief = "list user priveleges", description = help['adminlist_description'])
    async def adminlist(self, ctx):
        await self.bot.controller.report_user_roles(self.bot, ctx.report)

    @strict_channels()
    @strict_users(ur.admin)
    @commands.command(aliases=['ba'], brief = "ban user - no interraction with bot", description = help['banadd_description'])
    async def banadd(self, ctx, users: commands.Greedy[discord.User]):
        for user in users:
            ctx.report.set_key(f'{user.name}')
            self.bot.controller.add_user_role(user, ur.banned, ctx)

    @strict_channels()
    @strict_users(ur.admin)
    @commands.command(aliases=['bd'], brief = "delete user ban", description = help['deleteban_description'])
    async def bandelete(self, ctx, users: commands.Greedy[discord.User]):
        for user in users:
            ctx.report.set_key(f'{user.name}')
            self.bot.controller.delete_user_role(user, ctx)

    @strict_channels()
    @strict_users(ur.admin)
    @commands.command(aliases=['du'], brief = "deletes user record by coords x-y", description=help['deleteuser_description'])
    async def deleteuser(self, ctx, users: commands.Greedy[discord.User], coords: commands.Greedy[CoordsConverter] = help['coord_descr']):
        for user in users:
            ctx.report.set_key(f'{user.name}')
            for coord in coords:
                self.bot.controller.delete(coord, user, ctx)

    @strict_channels()
    @strict_users(ur.admin)
    @commands.command(aliases=['dau'], brief = "deletes all user records", description=help['deletealluser_description'])
    async def deletealluser(self, ctx, users: commands.Greedy[discord.User]):
        for user in users:
            ctx.report.set_key(f'{user.name}')
            ctx.report.msg.add(f'Removed coords:')
            self.bot.controller.report(user, 'c', ctx)
            self.bot.controller.deleteall(user, ctx)

    @strict_channels()
    @strict_users(ur.admin)
    @commands.command(aliases=['ru'], brief = "reportes users", description=help['reportusers_description'])
    async def reportuser(self, ctx, users: commands.Greedy[discord.User], c: Optional[Literal['c']] = help['compact_descr'],):
        for user in users:
            ctx.report.set_key(f'{user.name}')
            self.bot.controller.report(user, c, ctx)

    @strict_channels()
    @strict_users(ur.admin)
    @commands.command(aliases=['re'], brief = "reset week", description=help['reset_description'])
    async def reset(self, ctx):
        self.bot.reset(ctx)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))