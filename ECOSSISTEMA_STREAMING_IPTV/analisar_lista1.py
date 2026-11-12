import urllib.request
import ssl
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

url = 'https://tecnotv.club/r9jb/lista1.m3u'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
except Exception as e:
    print(f"ERRO AO BAIXAR: {e}")
    exit(1)

print(f"STATUS DE DOWNLOAD: Sucesso | Tamanho: {len(content)} bytes")
lines = content.splitlines()
print(f"Total de Linhas: {len(lines)}")

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

print(f"Total de Canais Encontrados: {len(channels)}")

groups = Counter([c['group'] for c in channels])
print("\nTop 20 Grupos/Categorias:")
for g, count in groups.most_common(20):
    print(f" - {g}: {count}")

# Analisar protocolos
protos = Counter([c['url'].split('://')[0].lower() if '://' in c['url'] else 'outro' for c in channels])
print(f"\nProtocolos: {dict(protos)}")

# Analisar domínios
doms = Counter([c['url'].split('://')[1].split('/')[0] if '://' in c['url'] else 'invalido' for c in channels])
print("\nTop 10 Domínios:")
for d, count in doms.most_common(10):
    print(f" - {d}: {count}")

# Verificar menções ao Brasil
br = [c for c in channels if any(k in c['group'].lower() or k in c['name'].lower() for k in ['brasil', 'brazil', 'globo', 'sbt', 'record', 'band'])]
print(f"\nCanais com nome/grupo ligado ao Brasil: {len(br)}")
for b in br[:10]:
    print(f"  * {b['name']} [{b['group']}] -> {b['url'][:60]}")

# Testar amostra de 20 canais em paralelo
print("\nTestando amostra de 20 canais para status online/offline...")
amostra = channels[::len(channels)//20] if len(channels) > 20 else channels

def testar(c):
    r = urllib.request.Request(c['url'], headers={'User-Agent': 'Mozilla/5.0'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(r, context=ctx, timeout=4) as res:
            ms = int((time.time() - t0) * 1000)
            return (True, c['name'], res.status, ms)
    except Exception as e:
        return (False, c['name'], str(e), 0)

with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(testar, amostra))

online = [r for r in results if r[0]]
offline = [r for r in results if not r[0]]

print(f"\nResultado da Amostra ({len(results)} testados):")
print(f" - Online: {len(online)} ({len(online)/len(results)*100:.1f}%)")
print(f" - Offline: {len(offline)} ({len(offline)/len(results)*100:.1f}%)")

print("\nCanais Online da amostra:")
for r in online[:6]:
    print(f"  ✅ {r[1]} | Status: {r[2]} | {r[3]}ms")
