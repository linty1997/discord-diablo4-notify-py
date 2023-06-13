from discord.ext import tasks, commands
import requests
from cog.controller import *


class MyTasks(commands.Cog):
    def __init__(self, bot):
        self.url = "https://diablo4.life/api/trackers/worldBoss/list"
        self.url_hell_tide = "https://diablo4.life/api/trackers/helltide/list"
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(minutes=3.0)
    async def printer(self):
        try:
            # 獲取並更新世界首領刷新時間
            res = requests.get(self.url).json()
            if 'event' in res and res['event']:
                evnet = res['event']
                word_boss = evnet['name']
                location = evnet['location']
                event_time = evnet['time']
                now = int(datetime.timestamp(datetime.now()))
                if event_time and int(int(event_time) / 1000) > now:
                    timestamp = int(int(event_time) / 1000)
                    await NotifyController(self.bot).update_spawn_time('world_boss', str(timestamp))
                    print(f"update spawn time: {timestamp}.")
                    # 檢查並推播符合條件之頻道
                    await NotifyController(self.bot).push_notify('world_boss', str(timestamp), boss_name=word_boss)
                    # 推播至 Line
                    await LineController(self.bot).push_notify('world_boss', timestamp,  boss_name=word_boss)
                    print("Done.")

            else:
                print('世界Boss尚無新事件.')
        except Exception as e:
            print(e)

        try:
            # 獲取並更新地獄潮汐刷新時間
            res = requests.get(self.url_hell_tide).json()
            if 'event' in res and res['event']:
                evnet = res['event']
                word_boss = evnet['name']
                location = evnet['location']
                event_time = evnet['time']
                now = int(datetime.timestamp(datetime.now()))
                if event_time and int(int(event_time) / 1000) > now:
                    timestamp = int(int(event_time) / 1000)
                    await NotifyController(self.bot).update_spawn_time('hell_tide', str(timestamp))
                    print(f"update end time: {timestamp}.")
                    # 檢查並推播符合條件之頻道
                    await NotifyController(self.bot).push_notify('hell_tide', str(timestamp), location=location)
                    # 推播至 Line
                    await LineController(self.bot).push_notify('hell_tide', timestamp,  location=location)
                    print("Done.")
            else:
                print('地獄潮汐尚無新事件.')
        except Exception as e:
            print(e)

    @printer.before_loop
    async def before_printer(self):
        print('Tasks waiting...')
        await self.bot.wait_until_ready()
