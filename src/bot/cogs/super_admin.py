import discord
from discord.ext import commands

from ...const import UserRole as ur
from ...helpo import help
from ..bot_util import strict_channels, strict_users

class SuperAdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @strict_channels()
    @strict_users(ur.super_admin)
    @commands.command(aliases=['aa'], brief = "add user with admin role - more commands available", description = help['addadmin_description'])
    async def adminadd(self, ctx, users: commands.Greedy[discord.User]):
        for user in users:
            ctx.report.set_key(f'{user.name}')
            self.bot.controller.add_user_role(user, ur.admin, ctx)

    @strict_channels()
    @strict_users(ur.super_admin)
    @commands.command(aliases=['ad'], brief = "delete user with admin", description = help['deleteadmin_description'])
    async def admindelete(self, ctx, users: commands.Greedy[discord.User]):
        for user in users:
            ctx.report.set_key(f'{user.name}')
            self.bot.controller.delete_user_role(user, ctx)

async def setup(bot):
    await bot.add_cog(SuperAdminCog(bot))