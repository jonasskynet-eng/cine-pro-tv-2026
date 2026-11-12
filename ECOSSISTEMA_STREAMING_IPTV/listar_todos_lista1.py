with open(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\analisar_lista1.py', 'r', encoding='utf-8') as f:
    pass

import urllib.request
import ssl

url = 'https://tecnotv.club/r9jb/lista1.m3u'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
    lines = resp.read().decode('utf-8', errors='ignore').splitlines()

print("LISTA COMPLETA DE CANAIS EM LISTA1.M3U:")
for i in range(len(lines)):
    if lines[i].startswith('#EXTINF:'):
        nome = lines[i].split(',')[-1].strip()
        link = lines[i+1].strip() if i+1 < len(lines) else ''
        print(f"• {nome} -> {link[:65]}")
