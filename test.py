import requests


url = 'https://diablo4.life/api/trackers/worldBoss/list'

res = requests.get(url).json()
#


#
if 'msg' in res and res['msg']:
    word_boss = res['name']
    location = res['location']
word_boss = res['event']
for i in word_boss:
    if i['reports']['1']:
        word_boss = i
        is_spawn_boss = True
        boss_name = i['name']
        break
for key, val in word_boss['reports'].items():
    if key == '1' and val:
        for timestamp in val.keys():
            if timestamp:
                print(timestamp)
        print('ok')
    print('空空')

print(res)

