from discord.ext import commands
import discord
from dotenv import load_dotenv
from cog.tasks import MyTasks
import os
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

##############################

token = os.getenv('TEST_TOKEN')
bot = discord.Bot()


for filename in os.listdir('./commands'):
    if filename.endswith('.py'):
        bot.load_extension(f'commands.{filename[:-3]}')
        print(f"load: {filename}")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name=f"👀 {len(bot.guilds)} Servers.",
                                                        type=discord.ActivityType.watching))
    logger.info(f"機器人已上線 ID : {bot.user}")
    # MyTasks(bot)
    if os.getenv('CI_TEST'):
        os._exit(0)


@bot.event
async def on_guild_join(guild):
    await bot.change_presence(activity=discord.Activity(name=f"👀 {len(bot.guilds)} Servers.",
                                                        type=discord.ActivityType.watching))
    logger.info(f"加入伺服器 ID : {guild.id}")


@bot.event
async def shutdown():
    logger.info("正在關閉與 Discord 的連結...")


@bot.event
async def close():
    logger.info("中斷連結...")


@bot.event
async def on_error(event, *args, **kwargs):
    raise event


@bot.event
async def on_application_command_error(ctx, event):
    interaction = ctx.interaction
    try:
        if isinstance(event, discord.ext.commands.CommandOnCooldown):
            await interaction.response.send_message(f"{event}", ephemeral=True)
            return
        if isinstance(event, discord.ext.commands.MissingPermissions):
            await interaction.response.send_message(f"{event}", ephemeral=True)
            return
        if isinstance(event, discord.ext.commands.MissingRole):
            await interaction.response.send_message(f"{event}", ephemeral=True)
            return
        if isinstance(event, AttributeError):
            return
        if isinstance(event, TypeError):
            return

        await interaction.response.send_message(f"發生了不明錯誤, 請再試一次.", ephemeral=True)

    except Exception as e:
        logger.error(e)

    raise event


@bot.event
async def on_resumed():
    logger.info("機器人已恢復.")


@bot.event
async def on_disconnect():
    logger.info("機器人斷開連結.")


bot.run(token)
