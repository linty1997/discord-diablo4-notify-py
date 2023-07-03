from discord.ext import tasks, commands
import requests
from cog.controller import *
import logging

logger = logging.getLogger('discord')

EVENT_NAMES = {
    'world_boss': '世界王',
    'hell_tide': '地獄浪潮',
    'legions': '軍團'
}


def extract_event_info(res, event):
    if 'event' in res and res['event'] and 'confidence' in res['event'] and res['event']['confidence']['name']:
        event = res['event']['confidence']
        name = max(event.get('name', {}), key=event.get('name', {}).get)
        location = max(event.get('location', {}), key=event.get('location', {}).get)
        times = event.get('time', {})
        if event == 'world_boss' and len(times) < 2:  # 時間需要有兩筆, 增加準確度
            return None
        event_time = max(times, key=times.get)
        return {'name': name, 'location': location, 'event_time': event_time}
    else:
        return None


async def push_worker(bot, url, event):
    try:
        res = requests.get(url).json()
        event_info = extract_event_info(res, event)
        event_name = EVENT_NAMES.get(event)
        if event_info:
            name = event_info['name']
            location = event_info['location']
            event_time = event_info['event_time']
            now = int(datetime.timestamp(datetime.now()))
            if event_time and int(int(event_time) / 1000) > now:
                timestamp = int(int(event_time) / 1000)
                await NotifyController(bot).update_spawn_time(event, str(timestamp))
                logger.info(f"更新{event_name}事件時間: {timestamp}.")
                params = {'event': event, 'timestamp': timestamp}
                if event == 'world_boss':
                    params['boss_name'] = name
                else:
                    params['location'] = location

                if event != 'legions':  # 軍團事件不推播LINE
                    await LineController(bot).push_notify(**params)
                await NotifyController(bot).push_notify(**params)

                logger.info(f"{event_name}事件推播任務完成.")
        else:
            logger.info(f'{event_name}尚無新事件.')
    except Exception as e:
        logger.error(e)


class MyTasks(commands.Cog):
    def __init__(self, bot):
        self.url_world_boss = "https://diablo4.life/api/trackers/worldBoss/list"
        self.url_hell_tide = "https://diablo4.life/api/trackers/helltide/list"
        self.url_legions = "https://diablo4.life/api/trackers/zoneEvent/list"
        self.bot = bot
        self.is_running = False
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(minutes=1.5)
    async def printer(self):
        try:
            logger.info("執行任務排程任務")
            if self.is_running:
                logger.info("已有任務執行中, 跳過.")
                return
            self.is_running = True
            urls = {
                'world_boss': self.url_world_boss,
                'hell_tide': self.url_hell_tide,
                'legions': self.url_legions
            }
            for event, url in urls.items():
                await push_worker(self.bot, url, event)
        except Exception as e:
            logger.error(e)
        finally:
            self.is_running = False

    @printer.before_loop
    async def before_printer(self):
        logger.info('任務等待執行...')
        await self.bot.wait_until_ready()
