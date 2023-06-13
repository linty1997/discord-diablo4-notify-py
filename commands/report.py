from discord.commands import slash_command, Option, OptionChoice
from discord.ext import commands
from cog.controller import *


class Report(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # report
    # @slash_command(description="Events report.")
    # async def report(self, ctx):
    #     await ctx.respond(ephemeral=True, view=ReportView(), delete_after=15)

    # test
    # @slash_command(description="test.")
    # @commands.is_owner()
    # async def test(self, ctx):
    #     res = await NotifyController(ctx).update_spawn_time('hell_tide', 1620000000)
    #     # res = await WorldBossController(ctx).push_notify(1686224460, 'test')
    #     await ctx.respond('ok')
    #
    # # push notify
    # @slash_command(description=".")
    # @commands.is_owner()
    # async def push(self, ctx, timestamp: int, boss_name: str):
    #     res = await WorldBossController(ctx).push_notify(timestamp, boss_name)
    #     await ctx.respond('ok')


def setup(bot):
    bot.add_cog(Report(bot))
