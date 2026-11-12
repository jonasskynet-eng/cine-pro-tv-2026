import re

with open(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\inspecionar_tags.py', 'r', encoding='utf-8') as f:
    pass

import urllib.request
import ssl

url = 'https://tecnotv.club/r9jb/lista.m3u'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
    raw = resp.read().decode('utf-8', errors='ignore')

lines = raw.splitlines()

# Vamos ver as linhas que NÃO deram match no group-title
sem_group = []
for i, line in enumerate(lines):
    if line.startswith('#EXTINF:'):
        if 'group-title' not in line:
            sem_group.append((i, line))

print("Total de EXTINF sem 'group-title':", len(sem_group))
for idx, line in sem_group[:20]:
    print(f"L{idx}: {line}")
