from discord.commands import slash_command, Option, OptionChoice
from discord.ext import commands
import discord
from cog.buttons import InviteView
from cog.controller import *


class Setting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # setting notify channel
    @slash_command(description="Get bot ping.")
    async def set_notify_channel(self, ctx, channel: discord.TextChannel):
        res = await SettingController(ctx).set(channel)
        await ctx.respond(f"`Done.`", delete_after=5, ephemeral=True)

    # del notify channel
    @slash_command(description="Get bot ping.")
    async def del_notify_setting(self, ctx):
        res = await SettingController(ctx).delete()
        await ctx.respond(f"`Done.`", delete_after=5, ephemeral=True)

    # get report logs
    @slash_command(description="Get bot ping.")
    async def get_report_logs(self, ctx,
                              time_zone: Option(int, requests=True, description="Time zone."),
                              event: Option(str, required=True, default="word_boss",
                                            description="Event.",
                                            choices=[
                                                OptionChoice("WordBoss", "word_boss"),
                                            ]),
                              ):
        res = await WordBossController(ctx).get_report_logs(event, time_zone)
        description = "User Id: Report Time\n\n"
        for k in res.keys():
            description += f"{k}: {res[k]}\n"
        embed = discord.Embed(title="Show only the first thirty", description=description, colour=0x00b0f4)
        embed.set_author(name="report users",
                         icon_url="https://media.discordapp.net/attachments/810844791428087828/1115248016694202378/256x256.png")
        embed.set_footer(text="Any questions please contact: 小白#0001",
                         icon_url="https://cdn.discordapp.com/attachments/1090779637463908432/1115249839467409499/discord_1.gif")
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Setting(bot))
