import urllib.request

url = 'https://cdn.jsdelivr.net/npm/mpegts.js@latest/dist/mpegts.js'
content = urllib.request.urlopen(url).read().decode('utf-8')

idx = 255445
print(content[idx-2000:idx])
