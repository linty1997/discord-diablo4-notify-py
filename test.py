import requests
from datetime import datetime


def extract_event_info(res):
    if 'event' in res and res['event'] and 'confidence' in res['event'] and res['event']['confidence']['name']:
        event = res['event']['confidence']
        name = max(event.get('name', {}), key=event.get('name', {}).get)
        location = max(event.get('location', {}), key=event.get('location', {}).get)
        event_time = max(event.get('time', {}), key=event.get('time', {}).get)
        return {'name': name, 'location': location, 'event_time': event_time}
    else:
        return None


url = 'https://diablo4.life/api/trackers/helltide/list' #'https://diablo4.life/api/trackers/worldBoss/list'  #

res = requests.get(url).json()
#


#
res = requests.get(url).json()
event_info = extract_event_info(res)
if event_info:
    name = event_info['name']
    location = event_info['location']
    event_time = event_info['event_time']
    now = int(datetime.timestamp(datetime.now()))
    if event_time and int(int(event_time) / 1000) > now:
        timestamp = int(int(event_time) / 1000)

        print(timestamp)
