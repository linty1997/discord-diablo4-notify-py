import asyncio
import requests
from cog.kv import *
from datetime import datetime, timedelta
from urllib.parse import unquote
import json
from flatten_dict import flatten
import discord
import logging

logger = logging.getLogger('discord')


def notify_embed(event, spawn_time, boss_name=None, location=None):
    if event == 'world_boss':
        event_name = '世界王'
    elif event == 'hell_tide':
        event_name = '地獄浪潮'
    elif event == 'legions':
        event_name = '軍團'
    embed = discord.Embed(title=f"{event_name}",
                          description=f"僅供參考.",
                          colour=0xf5006a,
                          timestamp=datetime.now())

    embed.set_author(name=f"Diablo4 Notify",
                     icon_url="https://media.discordapp.net/attachments/810844791428087828/1115248016694202378/256x256.png")

    if boss_name:
        embed.add_field(name="名稱",
                        value=f"{boss_name}",
                        inline=True)
        embed.add_field(name="刷新時間",
                        value=f"<t:{spawn_time}:R>",
                        inline=True)
    if location:
        event_time_name = "結束時間" if event == 'hell_tide' else "開始時間"
        embed.add_field(name="地點",
                        value=f"{location}",
                        inline=True)
        embed.add_field(name=event_time_name,
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


class NotifyController:
    def __init__(self, interaction):
        self.kv_data = KvData()
        self.kv_guilds_notify_settings = 'guilds_notify_settings'
        self.world_boss_notify_interval = 5  # 通知間隔(時間單位: 小時)
        self.hell_tide_notify_interval = 1  # 通知間隔(時間單位: 小時)
        self.legions_notify_interval = 0.3  # 通知間隔(時間單位: 小時)
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

    async def get_push_time(self, name=None):
        push_data = self.kv_data.get_val('guilds_push_time')
        if name is None:
            return push_data
        data = push_data.get(name, None) if push_data else None
        return data

    async def update_push_time(self, name, _data):
        data = await self.get_push_time()
        if data:
            data[name] = _data
        self.kv_data.set_val({'guilds_push_time': json.dumps(data)})

    async def check_guild_notify_time(self, guilds, event):
        channel_id_data = []
        now = int(datetime.timestamp(datetime.now()))
        guilds_push_time = await self.get_push_time(event)
        if not guilds_push_time:
            guilds_push_time = {}
        cd = self.hell_tide_notify_interval
        if event == 'world_boss':
            cd = self.world_boss_notify_interval
        if event == 'legions':
            cd = self.legions_notify_interval
        for guild_id, events in guilds.items():
            guild_push_time = guilds_push_time.get(str(guild_id), None) if guilds_push_time else None
            channel_id = events.get(event, None) if events else None
            if channel_id is None or channel_id == "":
                continue
            if guild_push_time is None or guild_push_time is not None and now - int(
                    guild_push_time) > cd * 3600:
                channel_id_data.append(channel_id)
                guilds_push_time[str(guild_id)] = str(now)
                logger.info(f"添加至推播列表 - 公會: {guild_id}, 頻道: {channel_id}")
            else:
                continue
        await self.update_push_time(event, guilds_push_time)
        logger.info(f"更新 Discord 推播時間 - {event}")

        return channel_id_data

    async def get_notify_channels(self, event):
        guilds = self.kv_data.get_val(self.kv_guilds_notify_settings)
        channel_id_data = await self.check_guild_notify_time(guilds, event)

        return channel_id_data

    async def push_notify(self, event, timestamp, boss_name=None, location=None):
        channels = await self.get_notify_channels(event)
        embed = notify_embed(event, str(timestamp), boss_name, location)
        for channel_id in channels:
            try:
                try:
                    channel = self.interaction.get_channel(int(channel_id))
                except Exception as e:
                    logger.error(f"interaction.get_channel 獲取頻道失敗: {e}")
                    channel = self.interaction.bot.get_channel(int(channel_id))
                try:
                    msg = await channel.send(embed=embed)
                    try:
                        await msg.publish()
                    except Exception as e:
                        pass
                except Exception as e:
                    logger.error(f"推播失敗, Discord 頻道: {channel_id}.\n原因: {e}")
                else:
                    logger.info(f"成功推播至 Discord 頻道: {channel_id}.")
            except Exception as e:
                logger.error(f"獲取頻道失敗或發生其他異常: channel:{channel_id}, {e}")
            await asyncio.sleep(0.4)


class LineController:
    def __init__(self, interaction):
        self.kv_data = KvData()
        self.kv_line_push_time_name = 'line_push_time'
        self.kv_line_push_data_name = 'line_push_data'
        self.kv_line_data_name = 'line_user_settings'
        self.world_boss_notify_interval = 4  # 通知間隔(時間單位: 小時)
        self.hell_tide_notify_interval = 1  # 通知間隔(時間單位: 小時)
        self.interaction = interaction

    async def get_line_user_settings(self):
        return self.kv_data.get_val(self.kv_line_data_name)

    async def get_line_push_time(self, event):
        data = self.kv_data.get_val(self.kv_line_push_time_name)
        if data:
            return data.get(event, None)
        return False

    async def set_line_push_time(self, timestamp, event):
        data = self.kv_data.get_val(self.kv_line_push_time_name)
        if data:
            data[event] = timestamp
        self.kv_data.set_val({self.kv_line_push_time_name: json.dumps(data)})

    async def set_line_push_data(self, event, event_time, name, location):
        data = self.kv_data.get_val(self.kv_line_push_data_name)
        if data:
            data[event]['event_time'] = event_time
            data[event]['name'] = name if name else ""
            data[event]['location'] = location if location else ""
            data[event]['status'] = False
        self.kv_data.set_val({self.kv_line_push_data_name: json.dumps(data)})

    async def push_notify(self, event, timestamp, boss_name=None, location=None):
        try:
            # line_push_time = int(await self.get_line_push_time(event))
            # cd = self.hell_tide_notify_interval
            # if event == 'world_boss':
            #     cd = self.world_boss_notify_interval
            # if timestamp > line_push_time and (timestamp - line_push_time) > cd * 3600:
            #     settings = await self.get_line_user_settings()
            #     await self.set_line_push_time(timestamp, event)
            #     logger.info(f"更新 Line Notify 推播時間 - {event}: {timestamp}")
            #     for user_id, token in settings.items():
            #         str_time = (datetime.fromtimestamp(timestamp) + timedelta(hours=8)).strftime("%m-%d %H:%M")  # UTC+8
            #         msg = ""
            #         event_name = '世界王' if event == 'world_boss' else '地獄浪潮'
            #         if boss_name:
            #             msg = f"{event_name}\n刷新時間(UTC+8): {str_time}"
            #             msg += f"\n名稱: {boss_name}"
            #         if location:
            #             msg = f"{event_name}\n結束時間(UTC+8): {str_time}"
            #             msg += f"\n地點: {location}"
            #         res = await push_line(token, msg)
            #         logger.info(f"成功發送 Line Notify: {user_id}.") if res == 200 else print(f"Line Notify 發送失敗: {user_id}.")
            #         await asyncio.sleep(0.1)
            await self.set_line_push_data(event, timestamp, boss_name, location)
        except Exception as e:
            logger.error(f"發送 Line Notify 發生錯誤: {e}")


class SettingController:
    def __init__(self, interaction):
        self.kv_data = KvData()
        self.kv_guilds_notify_settings = 'guilds_notify_settings'
        self.kv_line_data_name = 'line_user_settings'
        self.interaction = interaction

    async def get_line_user_settings(self):
        return self.kv_data.get_val(self.kv_line_data_name)

    async def get(self):
        return self.kv_data.get_val(self.kv_guilds_notify_settings)

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

    async def set(self, channel, event):
        guilds = await self.get()
        guild_id = str(channel.guild.id)
        channel_id = str(channel.id)
        if guilds:
            if guild_id not in guilds:
                guilds[guild_id] = {
                    'world_boss': None,
                    'hell_tide': None,
                    'legions': None,
                }
            if event:
                guilds[guild_id][event] = channel_id
            else:
                guilds[guild_id].update({k: channel_id for k in guilds[guild_id]})
            self.kv_data.set_val({self.kv_guilds_notify_settings: json.dumps(guilds)})
        return True

    async def delete_line_user_setting(self, user_id):
        settings = await self.get_line_user_settings()
        if settings and str(user_id) in settings:
            del settings[str(user_id)]
            self.kv_data.set_val({self.kv_line_data_name: json.dumps(settings)})
        return True

    async def delete(self, event):
        guilds = await self.get()
        guild_id = str(self.interaction.guild_id)
        if guilds and guild_id in guilds:
            if event:
                guilds[guild_id][event] = ""
            else:
                guilds[guild_id].update({k: "" for k in guilds[guild_id]})
            self.kv_data.set_val({self.kv_guilds_notify_settings: json.dumps(guilds)})
        return True

    async def test_convert_data(self):  # 上線前記得在撈一次
        res = convert_data(await self.get())
        return res


def convert_data(original_data):
    new_data = {}
    for guild_id, channel_id in original_data.items():
        new_data[guild_id] = {'world_boss': channel_id, 'hell_tide': channel_id, 'legions': ""}
    return json.dumps(new_data)


