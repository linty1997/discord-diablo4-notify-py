from discord.commands import slash_command, Option, OptionChoice
from discord.ext import commands
from cog.selects import ReportView


class Report(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # report
    @slash_command(description="Events report.")
    async def report(self, ctx):
        await ctx.respond(ephemeral=True, view=ReportView(), delete_after=15)


def setup(bot):
    bot.add_cog(Report(bot))

