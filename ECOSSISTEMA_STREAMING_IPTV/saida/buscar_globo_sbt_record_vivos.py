import os
import urllib.request
import ssl
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

dir_proj = r"c:\Users\jonas\Downloads\projeto de estudo"
candidatos = []

for root, dirs, files in os.walk(dir_proj):
    for f in files:
        if f.endswith(('.m3u', '.m3u8', '.txt')):
            full_path = os.path.join(root, f)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    lines = fp.readlines()
                    for i, l in enumerate(lines):
                        if l.startswith('#EXTINF'):
                            l_low = l.lower()
                            if any(k in l_low for k in ['globo', 'sbt', 'bandeirantes', 'record']):
                                if i + 1 < len(lines):
                                    u = lines[i+1].strip()
                                    if u.startswith('http') and ('m3u8' in u or 'live' in u) and not any(b in u for b in ['youtube', 'rtv30t', 'oneplayer']):
                                        nome = l.split(',')[-1].strip()
                                        candidatos.append((nome, u))
            except Exception:
                pass

print(f"Total de candidatos encontrados: {len(candidatos)}")

# Testar em paralelo
def testar(item):
    nome, u = item
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
            if resp.status == 200:
                body = resp.read(128).decode('utf-8', errors='ignore')
                if '#EXTM3U' in body or 'video' in resp.headers.get('Content-Type', ''):
                    return (nome, u, True)
    except Exception:
        pass
    return (nome, u, False)

# Filtrar duplicatas de URL
unicos = {}
for n, u in candidatos:
    if u not in unicos:
        unicos[u] = n

print(f"URLs únicas para testar: {len(unicos)}")

vivos = []
with ThreadPoolExecutor(max_workers=30) as executor:
    futures = [executor.submit(testar, (n, u)) for u, n in unicos.items()]
    for fut in futures:
        n, u, ok = fut.result()
        if ok:
            print(f"  [VIVO] {n} -> {u}")
            vivos.append((n, u))

print(f"\nTotal VIVOS encontrados: {len(vivos)}")
