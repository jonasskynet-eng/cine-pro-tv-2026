import urllib.request
import ssl
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import time

url = 'https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
except Exception as e:
    print("Erro ao baixar:", e)
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
        group_m = re.search(r'group-title="([^"]+)"', current_info)
        group = group_m.group(1).strip() if group_m else 'Geral'
        country_m = re.search(r'tvg-country="([^"]+)"', current_info)
        country = country_m.group(1).strip() if country_m else 'Desconhecido'
        parts = current_info.split(',')
        name = parts[-1].strip() if len(parts) > 1 else 'Sem Nome'
        channels.append({'name': name, 'group': group, 'country': country, 'url': line})
        current_info = None

print(f"Total de Canais Encontrados: {len(channels)}")

# Analisar Países
countries = Counter([c['country'] for c in channels])
print("\nTop 15 Países:")
for c_code, count in countries.most_common(15):
    print(f" - {c_code}: {count}")

# Analisar Categorias
groups = Counter([c['group'] for c in channels])
print("\nTop 15 Categorias:")
for g, count in groups.most_common(15):
    print(f" - {g}: {count}")

# Canais do Brasil
br_channels = [c for c in channels if c['country'].upper() in ['BR', 'BRA'] or any(k in c['name'].lower() or k in c['group'].lower() for k in ['brasil', 'brazil', 'globo', 'sbt', 'band', 'record', 'cultura'])]
print(f"\nCanais do Brasil encontrados: {len(br_channels)}")
for b in br_channels[:15]:
    print(f"  * {b['name']} [{b['country']}] -> {b['url'][:65]}")

# Testar amostra de canais para status e latência
print("\nTestando amostra de 30 canais para status e CORS...")
amostra = channels[::len(channels)//30] if len(channels) > 30 else channels

def testar(c):
    r = urllib.request.Request(c['url'], headers={'User-Agent': 'Mozilla/5.0'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(r, context=ctx, timeout=3.5) as res:
            ms = int((time.time() - t0) * 1000)
            cors = res.headers.get('Access-Control-Allow-Origin', 'Não')
            return (True, c['name'], res.status, ms, cors)
    except Exception as e:
        return (False, c['name'], str(e), 0, 'Erro')

with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(testar, amostra))

online = [r for r in results if r[0]]
offline = [r for r in results if not r[0]]
cors_ok = [r for r in online if r[4] == '*' or r[4] != 'Não']

print(f"\nResultado da Amostra ({len(results)} testados):")
print(f" - Online: {len(online)} ({len(online)/len(results)*100:.1f}%)")
print(f" - Offline: {len(offline)} ({len(offline)/len(results)*100:.1f}%)")
print(f" - Com CORS Aberto (Tela Web OK): {len(cors_ok)} ({len(cors_ok)/len(results)*100:.1f}%)")

print("\nAmostra de Canais Online:")
for r in online[:8]:
    print(f"  ✅ {r[1]} | HTTP {r[2]} | {r[3]}ms | CORS: {r[4]}")
