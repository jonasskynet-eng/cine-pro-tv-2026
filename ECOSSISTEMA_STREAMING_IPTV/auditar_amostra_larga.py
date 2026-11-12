import urllib.request
import ssl
import re
import time
from concurrent.futures import ThreadPoolExecutor

url = 'https://tecnotv.club/r9jb/lista.m3u'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
    lines = resp.read().decode('utf-8', errors='ignore').splitlines()

items = []
current_name = None
for line in lines:
    line = line.strip()
    if not line:
        continue
    if line.startswith('#EXTINF:'):
        parts = line.split(',')
        current_name = parts[-1].strip() if len(parts) > 1 else 'Canal'
    elif not line.startswith('#') and current_name:
        items.append((current_name, line))
        current_name = None

print(f"Total coletado: {len(items)} canais.")

# Testar uma amostra representativa de 40 canais
amostra = items[::len(items)//40] if len(items) > 40 else items

def testar(item):
    name, u = item
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(r, context=ctx, timeout=4) as res:
            ms = int((time.time() - t0) * 1000)
            return (True, name, res.status, ms, u)
    except Exception as e:
        return (False, name, str(e), 0, u)

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(testar, amostra))

ativos = [r for r in results if r[0]]
inativos = [r for r in results if not r[0]]

print(f"\nResultado da Amostra ({len(results)} canais testados):")
print(f" - Ativos (Online): {len(ativos)} ({len(ativos)/len(results)*100:.1f}%)")
print(f" - Inativos/Offline: {len(inativos)} ({len(inativos)/len(results)*100:.1f}%)")

print("\nCanais Online confirmados:")
for r in ativos[:8]:
    print(f"  ✅ {r[1]} | Status: {r[2]} | {r[3]}ms")

print("\nCanais com falha (amostra):")
for r in inativos[:5]:
    print(f"  ❌ {r[1]} | Motivo: {r[2]}")
