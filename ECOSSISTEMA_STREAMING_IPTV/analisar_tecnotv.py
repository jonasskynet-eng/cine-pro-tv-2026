import urllib.request
import ssl
import re
from collections import Counter

url = 'https://tecnotv.club/r9jb/lista.m3u'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        raw = resp.read().decode('utf-8', errors='ignore')
except Exception as e:
    print("Erro ao baixar:", e)
    exit(1)

lines = raw.splitlines()

channels = []
current_info = None

for line in lines:
    line = line.strip()
    if not line:
        continue
    if line.startswith('#EXTINF:'):
        current_info = line
    elif not line.startswith('#') and current_info:
        group_match = re.search(r'group-title="([^"]+)"', current_info)
        group = group_match.group(1).strip() if group_match else 'OUTROS'
        name_parts = current_info.split(',')
        name = name_parts[-1].strip() if len(name_parts) > 1 else 'Sem Nome'
        channels.append({'name': name, 'group': group, 'url': line})
        current_info = None

print('TOTAL_CANAIS:', len(channels))
groups = Counter([c['group'] for c in channels])
print('\nGRUPOS_ENCONTRADOS:')
for g, count in groups.most_common(35):
    print(f"{g} | {count}")

# Procurar Brasil
br = [c for c in channels if any(k in c['group'].lower() or k in c['name'].lower() for k in ['brasil', 'brazil', 'globo', 'sbt', 'record', 'band'])]
print('\nCANAIS_RELACIONADOS_BRASIL:', len(br))
for item in br[:15]:
    print(f"- {item['name']} [{item['group']}] -> {item['url'][:70]}")

# Analisar domínios e protocolos
domains = Counter()
protocols = Counter()
for c in channels:
    u = c['url']
    if '://' in u:
        proto = u.split('://')[0].lower()
        protocols[proto] += 1
        dom = u.split('://')[1].split('/')[0]
        domains[dom] += 1

print('\nPROTOCOLOS:')
for p, cnt in protocols.items():
    print(f"{p}: {cnt}")

print('\nTOP_DOMINIOS:')
for d, cnt in domains.most_common(10):
    print(f"{d}: {cnt}")
