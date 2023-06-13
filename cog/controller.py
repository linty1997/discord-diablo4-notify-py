import asyncio
import requests
from cog.kv import *
from datetime import datetime, timedelta
from urllib.parse import unquote
import json
from flatten_dict import flatten
import discord


def notify_embed(event, spawn_time, boss_name=None, location=None):
    event_name = 'World Boss' if event == 'world_boss' else 'Hell Tide'
    embed = discord.Embed(title=f"{event}",
                          description=f"for your reference.",
                          colour=0xf5006a,
                          timestamp=datetime.now())

    embed.set_author(name=f"Diablo4 Notify",
                     icon_url="https://media.discordapp.net/attachments/810844791428087828/1115248016694202378/256x256.png")

    if boss_name:
        embed.add_field(name="Boss",
                        value=f"{boss_name}",
                        inline=True)
        embed.add_field(name="Spawn time",
                        value=f"<t:{spawn_time}:R>",
                        inline=True)
    if location:
        embed.add_field(name="Location",
                        value=f"{location}",
                        inline=True)
        embed.add_field(name="END time",
                        value=f"<t:{spawn_time}:R>",
                        inline=True)

    embed.set_footer(text="Good luck! By linty1997",
                     icon_url="https://cdn.discordapp.com/attachments/1090779637463908432/1115249839467409499/discord_1.gif")
    return embed


async def push_line(token, msg):

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code


# class WorldBossController:
#     def __init__(self, interaction):
#         self.kv_data = KvData()
#         self.kv_guilds_data_name = "guilds"
#         self.kv_push_data_name = "push_data"
#         self.guild_notify_interval = 4  # 通知間隔(時間單位: 小時)
#         self.interaction = interaction
#
#     async def update_spawn_time(self, timestamp):
#         self.kv_data.set_val({"web": timestamp})
#
#     async def check_guild_notify_time(self, guilds):
#         channel_id_data = []
#         now = int(datetime.timestamp(datetime.now()))
#         guilds_push_time = self.kv_data.get_val(self.kv_push_data_name)
#         if not guilds_push_time:
#             guilds_push_time = {}
#         for guild_id, channel_id in guilds.items():
#             guild_push_time = guilds_push_time.get(str(guild_id), None) if guilds_push_time else None
#             if guild_push_time is None or guild_push_time is not None and now - int(
#                     guild_push_time) > self.guild_notify_interval * 3600:
#                 channel_id_data.append(channel_id)
#                 guilds_push_time[str(guild_id)] = str(now)
#                 print(f"添加通知 - 公會: {guild_id}")
#         self.kv_data.set_val({self.kv_push_data_name: json.dumps(guilds_push_time)})
#
#         return channel_id_data
#
#     async def get_notify_channels(self):
#         guilds = self.kv_data.get_val(self.kv_guilds_data_name)
#         channel_id_data = await self.check_guild_notify_time(guilds)
#
#         return channel_id_data
#
#     async def push_notify(self, timestamp, boss_name):
#         channels = await self.get_notify_channels()
#         embed = notify_embed("World Boss", timestamp, boss_name)
#         for channel_id in channels:
#             try:
#                 try:
#                     channel = self.interaction.get_channel(int(channel_id))
#                 except Exception as e:
#                     print(e, self.interaction)
#                     channel = self.interaction.bot.get_channel(int(channel_id))
#                 try:
#                     msg = await channel.send(embed=embed)
#                     await msg.publish()
#                 except Exception as e:
#                     print(e)
#                 else:
#                     print(f"send to: {channel_id}.")
#                 await asyncio.sleep(0.1)
#             except Exception as e:
#                 print(e)


class NotifyController:
    def __init__(self, interaction):
        self.kv_data = KvData()
        self.kv_guilds_data_name = "guilds"
        self.kv_push_data_name = "push_data"
        self.world_boss_notify_interval = 4  # 通知間隔(時間單位: 小時)
        self.hell_tide_notify_interval = 1  # 通知間隔(時間單位: 小時)
        self.interaction = interaction

    async def get_spawn_time(self, name=None):
        spawn_data = self.kv_data.get_val('spawn_data')
        if name is None:
            return spawn_data
        data = spawn_data.get(name, None) if spawn_data else None
        return data

    async def update_spawn_time(self, name, timestamp):
        data = await self.get_spawn_time()
        if data:
            data[name] = timestamp
        self.kv_data.set_val({'spawn_data': json.dumps(data)})

    async def get_pust_time(self, name=None):
        push_data = self.kv_data.get_val('guilds_push_time')
        if name is None:
            return push_data
        data = push_data.get(name, None) if push_data else None
        return data

    async def update_push_time(self, name, _data):
        data = await self.get_pust_time()
        if data:
            data[name] = _data
        self.kv_data.set_val({'guilds_push_time': json.dumps(data)})

    async def check_guild_notify_time(self, guilds, event):
        channel_id_data = []
        now = int(datetime.timestamp(datetime.now()))
        guilds_push_time = await self.get_pust_time(event)
        if not guilds_push_time:
            guilds_push_time = {}
        cd = self.hell_tide_notify_interval
        if event == 'world_boss':
            cd = self.world_boss_notify_interval
        for guild_id, channel_id in guilds.items():
            guild_push_time = guilds_push_time.get(str(guild_id), None) if guilds_push_time else None
            if guild_push_time is None or guild_push_time is not None and now - int(
                    guild_push_time) > cd * 3600:
                channel_id_data.append(channel_id)
                guilds_push_time[str(guild_id)] = str(now)
                print(f"添加通知 - 公會: {guild_id}")
        await self.update_push_time(event, guilds_push_time)

        return channel_id_data

    async def get_notify_channels(self, event):
        guilds = self.kv_data.get_val(self.kv_guilds_data_name)
        channel_id_data = await self.check_guild_notify_time(guilds, event)

        return channel_id_data

    async def push_notify(self, event, timestamp, boss_name=None, location=None):
        channels = await self.get_notify_channels(event)
        embed = notify_embed(event, timestamp, boss_name, location)
        for channel_id in channels:
            try:
                try:
                    channel = self.interaction.get_channel(int(channel_id))
                except Exception as e:
                    print(e, self.interaction)
                    channel = self.interaction.bot.get_channel(int(channel_id))
                try:
                    msg = await channel.send(embed=embed)
                    await msg.publish()
                except Exception as e:
                    print(e)
                else:
                    print(f"send to: {channel_id}.")
                await asyncio.sleep(0.1)
            except Exception as e:
                print(e)


class LineController:
    def __init__(self, interaction):
        self.kv_data = KvData()
        self.kv_line_push_data_name = 'line_push_time'
        self.kv_line_data_name = 'line_user_settings'
        self.world_boss_notify_interval = 4  # 通知間隔(時間單位: 小時)
        self.hell_tide_notify_interval = 1  # 通知間隔(時間單位: 小時)
        self.interaction = interaction

    async def get_line_user_settings(self):
        return self.kv_data.get_val(self.kv_line_data_name)

    async def get_line_push_time(self, event):
        data = self.kv_data.get_val(self.kv_line_push_data_name)
        if data:
            return data.get(event, None)
        return False

    async def set_line_push_time(self, timestamp, event):
        data = self.kv_data.get_val(self.kv_line_push_data_name)
        if data:
            data[event] = timestamp
        self.kv_data.set_val({self.kv_line_push_data_name: json.dumps(data)})

    async def push_notify(self, event, timestamp, boss_name=None, location=None):
        try:
            line_push_time = int(await self.get_line_push_time(event))
            cd = self.hell_tide_notify_interval
            if event == 'world_boss':
                cd = self.world_boss_notify_interval
            if timestamp > line_push_time and timestamp - line_push_time > cd * 3600:
                settings = await self.get_line_user_settings()
                for user_id, token in settings.items():
                    str_time = datetime.fromtimestamp(timestamp).strftime("%m-%d %H:%M")
                    msg = ""
                    if boss_name:
                        msg = f"{event}\nSpawn Time(UTC): {str_time}"
                        msg += f"\nBoss: {boss_name}"
                    if location:
                        msg = f"{event}\nEND Time(UTC): {str_time}"
                        msg += f"\nLocation: {location}"
                    res = await push_line(token, msg)
                    print(f"send to: {user_id}.") if res == 200 else print(f"send to: {user_id} error.")
                    await asyncio.sleep(0.1)
                await self.set_line_push_time(timestamp, event)
        except Exception as e:
            print(e)



class SettingController:
    def __init__(self, interaction):
        self.kv_data = KvData()
        self.kv_guilds_data_name = 'guilds'
        self.kv_line_data_name = 'line_user_settings'
        self.interaction = interaction

    async def get_line_user_settings(self):
        return self.kv_data.get_val(self.kv_line_data_name)

    async def get(self):
        return self.kv_data.get_val(self.kv_guilds_data_name)

    async def get_channel(self):
        guilds = await self.get()
        if guilds and str(self.interaction.guild_id) in guilds:
            return guilds[str(self.interaction.guild_id)]
        return None

    async def set_line_user_setting(self, user_id, token):
        settings = await self.get_line_user_settings()
        if settings:
            settings[str(user_id)] = str(token)
            self.kv_data.set_val({self.kv_line_data_name: json.dumps(settings)})
        return True

    async def set(self, channel):
        guilds = await self.get()
        if guilds:
            guilds[str(channel.guild.id)] = str(channel.id)
            self.kv_data.set_val({self.kv_guilds_data_name: json.dumps(guilds)})
        return True

    async def delete_line_user_setting(self, user_id):
        settings = await self.get_line_user_settings()
        if settings and str(user_id) in settings:
            del settings[str(user_id)]
            self.kv_data.set_val({self.kv_line_data_name: json.dumps(settings)})
        return True

    async def delete(self):
        guilds = await self.get()
        if guilds and str(self.interaction.guild_id) in guilds:
            del guilds[str(self.interaction.guild_id)]
            self.kv_data.set_val({self.kv_guilds_data_name: json.dumps(guilds)})
        return True
