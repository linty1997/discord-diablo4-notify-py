from discord.commands import slash_command, Option, OptionChoice
from discord.ext import commands
import discord
from cog.buttons import InviteView
from cog.controller import *


class Setting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # setting notify channel
    @slash_command(description="Setting notify channel.")
    async def set_notify_channel(self, ctx, channel: discord.TextChannel):
        res = await SettingController(ctx).set(channel)
        await ctx.respond(f"`Done.`", delete_after=5, ephemeral=True)

    # get notify channel
    @slash_command(description="Get your setting notify channel.")
    async def get_notify_channel(self, ctx):
        channel = await SettingController(ctx).get_channel()
        msg = f"`Channel:` <#{channel}>" if channel else f"`Channel:` None"
        await ctx.respond(msg, delete_after=5, ephemeral=True)

    # del notify channel
    @slash_command(description="Del notify channel.")
    async def del_notify_setting(self, ctx):
        res = await SettingController(ctx).delete()
        await ctx.respond(f"`Done.`", delete_after=5, ephemeral=True)

    # setting line notify
    @slash_command(description="Setting line notify token.")
    async def set_line_notify(self, ctx, token: str):
        res = await SettingController(ctx).set_line_user_setting(ctx.user.id, token)
        await ctx.respond(f"`Done.`", delete_after=5, ephemeral=True)

    # del line notify
    @slash_command(description="Del line notify setting.")
    async def del_line_notify(self, ctx):
        res = await SettingController(ctx).delete_line_user_setting(ctx.user.id)
        await ctx.respond(f"`Done.`", delete_after=5, ephemeral=True)


def setup(bot):
    bot.add_cog(Setting(bot))
