from discord.ext import commands
import discord
from dotenv import load_dotenv
import os

load_dotenv()

##############################

token = os.getenv('TOKEN')
bot = discord.Bot(debug_guilds=[int(713282267719532615)])


for filename in os.listdir('./commands'):
    if filename.endswith('.py'):
        bot.load_extension(f'commands.{filename[:-3]}')
        print(f"load: {filename}")


@bot.event
async def on_ready():
    print(f"機器人已上線 ID : {bot.user}")
    if os.getenv('CI_TEST'):
        os._exit(0)


@bot.event
async def shutdown():
    print("正在關閉與 Discord 的連結...")


@bot.event
async def close():
    print("中斷連結...")


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

        await interaction.response.send_message(f"An error occurred, please try again.", ephemeral=True)

    except Exception as e:
        pass

    raise event


@bot.event
async def on_resumed():
    print("機器人已恢復.")


@bot.event
async def on_disconnect():
    print("機器人斷開連結.")


bot.run(token)
