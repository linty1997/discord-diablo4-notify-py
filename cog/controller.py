from cog.kv import *
from datetime import datetime, timedelta
from urllib.parse import unquote
import json
from flatten_dict import flatten


def calculate_average_time(*times):
    datetime_format = "%m-%d %H:%M"
    datetime_list = [datetime.strptime(time, datetime_format) for time in times]
    total_time = sum((dt - datetime.min for dt in datetime_list), timedelta())
    average_time = datetime.min + (total_time / len(datetime_list))

    return average_time


class WordBossController:
    def __init__(self, interaction):
        self.kv_data = KvData()
        self.kv_push_data = KvPushData()
        self.kv_guilds = KvGuilds()
        self.min_submit_number = 5  # 最少需要人數 低於無法再次提交
        self.min_notify_number = 8  # 通知需求人數
        self.average_time_difference = 15  # 與平均時間的誤差值
        self.delete_data_time = 3  # 資料保留時間 超過刪除(時間單位: 小時)
        self.interaction = interaction
        self.user_id = interaction.user.id
        self.guilds = interaction.bot.guilds if interaction.bot else interaction.client.guilds

    async def update(self, appearance_time: str, time_zone: str):
        try:
            appearance_datetime = datetime.strptime(appearance_time, "%m-%d %H:%M")
            data = self.kv_data.get_val(time_zone)
            if data:
                time_values = list(flatten(data).values())
                report_average_time = calculate_average_time(*time_values)
                # 與UTC時間的誤差值
                utc_time_difference = abs(report_average_time.replace(year=datetime.utcnow().year) - datetime.utcnow()) > \
                                      timedelta(hours=self.delete_data_time)
                # 與報告時間的誤差值, 刪除用
                report_time_difference_del = abs(report_average_time - appearance_datetime) > \
                                         timedelta(hours=self.delete_data_time)
                # 與報告時間的誤差值, 通知用
                report_time_difference = abs(report_average_time - appearance_datetime) > \
                                         timedelta(minutes=self.average_time_difference)

            else:
                data = {self.user_id: appearance_time}
                self.kv_data.set_val({time_zone: json.dumps(data)})
                return True

            if str(self.user_id) in data.keys() or \
                    not utc_time_difference and report_time_difference:
                return False

            if len(time_values) < self.min_submit_number:
                data[self.user_id] = appearance_time
                self.kv_data.set_val({time_zone: json.dumps(data)})
                return True

            if abs(report_average_time - appearance_datetime) < timedelta(
                    minutes=self.average_time_difference):
                data[self.user_id] = appearance_time
                self.kv_data.set_val({time_zone: json.dumps(data)})
                if len(time_values) >= self.min_notify_number:
                    # 處理通知邏輯
                    time_values.append(appearance_time)
                    average_time = report_average_time
                    guilds = self.kv_guilds.get_keys()
                    channel_ids = [self.kv_guilds.get_val(guild_id) for guild_id in guilds]
                    push_time = datetime.utcnow()
                    for channel_id in channel_ids:
                        channel = self.interaction.client.get_channel(int(channel_id))
                        guild_push_data = self.kv_push_data.get_val(str(channel.guild.id))
                        if guild_push_data:  # 四小時內通知過則不再通知
                            current_time = datetime.strptime(guild_push_data, "%m-%d %H:%M").replace(
                                year=push_time.year)
                            time_difference = abs(push_time - current_time)
                            if time_difference < timedelta(hours=4):
                                continue
                        await channel.send(f'{average_time.strftime("%m-%d %H:%M")} 出現')
                        self.kv_push_data.set_val({channel.guild.id: f'{push_time.strftime("%m-%d %H:%M")}'})

                return True

            # 檢查是否過久, 是則清空資料
            if utc_time_difference and report_time_difference_del:
                self.kv_data.del_key(time_zone)
                data = {self.user_id: appearance_time}
                self.kv_data.set_val({time_zone: json.dumps(data)})
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return False

    async def get_report_logs(self, event, time_zone: int):
        data = self.kv_data.get_val(str(time_zone))
        return data


class SettingController:
    def __init__(self, interaction):
        self.kv_data = KvData()
        self.kv_push_data = KvPushData()
        self.kv_guilds = KvGuilds()
        self.interaction = interaction

    async def set(self, channel):
        self.kv_guilds.set_val({str(channel.guild.id): str(channel.id)})
        return True

    async def delete(self):
        self.kv_guilds.del_key(str(self.interaction.guild.id))
        return True
