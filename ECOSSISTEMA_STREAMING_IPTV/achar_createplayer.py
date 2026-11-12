import urllib.request
import re

url = 'https://cdn.jsdelivr.net/npm/mpegts.js@latest/dist/mpegts.js'
content = urllib.request.urlopen(url).read().decode('utf-8')

idx = content.find('createPlayer')
while idx != -1:
    print('ACHOU createPlayer em:', idx)
    print(content[max(0, idx-50):min(len(content), idx+500)])
    print('='*50)
    idx = content.find('createPlayer', idx+12)
    if idx > 30000:
        break
