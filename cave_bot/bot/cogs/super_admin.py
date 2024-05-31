import discord
from discord.ext import commands
from typing import Optional
import gc

from ...const import UserRole as ur
from ...helpo import help
from ..bot_util import strict_channels, strict_users
from ...utils import print_memory_tracker

class SuperAdminCog(commands.Cog, name='SuperAdmin', description = "SuperAdmin commands - manipulate with other admins data"):

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

    @strict_channels()
    @strict_users(ur.super_admin)
    @commands.command(aliases=['dm'], brief = "dump memory objects")
    async def dumpmemory(self, ctx):
        print_memory_tracker(ctx)

    @strict_channels()
    @strict_users(ur.super_admin)
    @commands.command(aliases=['gc'], brief = "attempt to run garbage collector manually")
    async def gccollect(self, ctx):
        gc.collect()
        ctx.report.msg.add('collected')

    @strict_channels()
    @strict_users(ur.super_admin)
    @commands.command(brief = "save from memory db to connected db")
    async def save(self, ctx):
        self.bot.db.save_to_load_db()
        ctx.report.msg.add('saved')

    @strict_channels()
    @strict_users(ur.super_admin)
    @commands.command(aliases=['pro'], brief = "profile peformance")
    async def profile(self, ctx):
        if self.bot.is_profile == True:
            ctx.report.msg.add('profiling off')
            self.bot.is_profile = False
            self.bot.pr = None
        else:
            ctx.report.msg.add('profiling on')
            self.bot.is_profile = True
    
    @strict_channels()
    @strict_users(ur.super_admin)
    @commands.command(brief = "test db, better with select")
    async def test(self, ctx):
        with self.bot.db.LoadSession() as s:
            last_scan_record = s.query(self.bot.db.m.LastScan).first()
            ctx.report.msg.add(last_scan_record and str(last_scan_record.last_scan))

    @strict_channels()
    @strict_users(ur.super_admin)
    @commands.command(aliases = ['rwd'], brief = "reset week db")
    async def reset_week_db(self, ctx):
        allowed_partial_table_names_to_reset = ['last_scan', 'cell_', 'user_record_']
        db = self.bot.db
        with db.memory_db.connect() as mdb:
            for table in db.m.Base.metadata.sorted_tables:
                is_reset = False
                for part in allowed_partial_table_names_to_reset:
                    if part in table.name:
                        is_reset = True
                        break
                if not is_reset:
                    continue
                ctx.report.msg.add(f'drop -> {table.name}')
                mdb.execute(table.delete())

            mdb.commit()

        self.bot.reset_view()
        await self.bot.spawn_scan()

async def setup(bot):
    await bot.add_cog(SuperAdminCog(bot))