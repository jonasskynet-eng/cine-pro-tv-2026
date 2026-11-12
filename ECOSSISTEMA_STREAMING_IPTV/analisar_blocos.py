import urllib.request
import ssl
import re

url = 'https://tecnotv.club/r9jb/lista.m3u'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
    text = resp.read().decode('utf-8', errors='ignore')

lines = text.splitlines()

m3u_indices = [i for i, line in enumerate(lines) if line.strip() == '#EXTM3U']
print(f"Total de blocos #EXTM3U encontrados: {len(m3u_indices)} nas linhas {m3u_indices}")

# Vamos analisar os domínios .br e canais brasileiros
br_lines = []
for i, line in enumerate(lines):
    if '.br' in line.lower() or 'brasil' in line.lower() or 'brazil' in line.lower():
        br_lines.append((i, line))

print(f"\nTotal de linhas com referência ao Brasil / .br: {len(br_lines)}")
for idx, l in br_lines[:20]:
    print(f"L{idx}: {l}")
