from discord.commands import slash_command, Option, OptionChoice
from discord.ext import commands
import discord
from cog.buttons import InviteView, BindingLineNotifyView
from cog.controller import *


class Setting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # setting notify channel
    @slash_command(description="Setting notify channel.")
    @commands.has_guild_permissions(administrator=True)
    async def set_notify_channel(self, ctx, channel: discord.TextChannel,
                                 event: Option(str, description="Event type.", required=False, choices=[
                                        OptionChoice(name="世界王", value="world_boss"),
                                        OptionChoice(name="地獄浪潮", value="hell_tide"),
                                        OptionChoice(name="軍團", value="legions"),
                                 ])):
        await ctx.defer(ephemeral=True)
        res = await SettingController(ctx).set(channel, event)
        await ctx.send_followup(f"`Done.`", delete_after=5)

    # get notify channel
    @slash_command(description="Get your setting notify channel.")
    async def get_notify_channel(self, ctx):
        await ctx.defer(ephemeral=True)
        channel_data = await SettingController(ctx).get_channel()
        if channel_data:
            world_boss = f"<#{channel_data['world_boss']}>" if channel_data['world_boss'] else "`未設置`"
            hell_tide = f"<#{channel_data['hell_tide']}>" if channel_data['hell_tide'] else "`未設置`"
            legions = f"<#{channel_data['legions']}>" if channel_data['legions'] else "`未設置`"

        msg = f"`世界王:` {world_boss}\n`地獄浪潮:` {hell_tide}\n`軍團:` {legions}"\
            if channel_data else f"`頻道通知:` 未設置"
        await ctx.send_followup(msg, delete_after=10)

    # del notify channel
    @slash_command(description="Del notify channel.")
    @commands.has_guild_permissions(administrator=True)
    async def del_notify_setting(self, ctx,
                                 event: Option(str, description="Event type.", required=False, choices=[
                                     OptionChoice(name="世界王", value="world_boss"),
                                     OptionChoice(name="地獄浪潮", value="hell_tide"),
                                     OptionChoice(name="軍團", value=" legions"),
                                 ])):
        await ctx.defer(ephemeral=True)
        res = await SettingController(ctx).delete(event=event)
        await ctx.send_followup(f"`Done.`", delete_after=5)

    # setting line notify
    @slash_command(description="Setting line notify token.")
    async def set_line_notify(self, ctx):
        await ctx.respond(view=BindingLineNotifyView(ctx.user.id), ephemeral=True)
        # res = await SettingController(ctx).set_line_user_setting(ctx.user.id, token)
        # await ctx.respond(f"`Done.`", delete_after=5, ephemeral=True)

    # del line notify
    @slash_command(description="Del line notify setting.")
    async def del_line_notify(self, ctx):
        res = await SettingController(ctx).delete_line_user_setting(ctx.user.id)
        await ctx.respond(f"`Done.`", delete_after=5, ephemeral=True)


def setup(bot):
    bot.add_cog(Setting(bot))
