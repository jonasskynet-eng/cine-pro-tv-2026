import re

with open(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\analisar_tecnotv.py', 'r', encoding='utf-8') as f:
    pass

# Vamos ler a lista e checar como estão os EXTINF
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

samples = []
for i, line in enumerate(lines):
    if line.startswith('#EXTINF:'):
        # pegar as próximas 1 linhas
        samples.append(line)
        if len(samples) > 40:
            break

print("Exemplos de EXTINF:")
for s in samples[10:30]:
    print(s)
