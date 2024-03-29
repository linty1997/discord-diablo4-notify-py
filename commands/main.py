from discord.commands import slash_command, Option, OptionChoice
from discord.ext import commands
import discord
from cog.buttons import InviteView


class Main(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ping
    @slash_command(description="Get bot ping.")
    async def ping(self, ctx):
        await ctx.respond(f"`{round(self.bot.latency * 1000)} ms`", ephemeral=True)

    # invite
    @slash_command(description="Get bot invite link.")
    async def invite(self, ctx):
        await ctx.respond(view=InviteView(), ephemeral=True)


def setup(bot):
    bot.add_cog(Main(bot))

