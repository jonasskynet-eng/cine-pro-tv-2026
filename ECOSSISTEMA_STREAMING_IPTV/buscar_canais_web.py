import sqlite3
import urllib.request
import ssl
from concurrent.futures import ThreadPoolExecutor

db = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Buscar canais do Brasil
c.execute('''
    SELECT id, nome, url, regiao 
    FROM canais 
    WHERE pais LIKE "%Brasil%" 
    LIMIT 300
''')
rows = c.fetchall()
conn.close()

print(f"Testando {len(rows)} canais do Brasil para compatibilidade direta com navegador...")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def testar_browser(r):
    cid, name, u, reg = r
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
            cors = resp.headers.get('Access-Control-Allow-Origin', '')
            ctype = resp.headers.get('Content-Type', '')
            if cors == '*' or 'pluto' in u:
                return (True, cid, name, u, reg, cors)
            elif resp.status == 200:
                return (False, cid, name, u, reg, f'Sem CORS (*), CORS={cors}')
    except Exception as e:
        return (False, cid, name, u, reg, str(e))
    return (False, cid, name, u, reg, 'Outro')

with ThreadPoolExecutor(max_workers=20) as ex:
    results = list(ex.map(testar_browser, rows))

compatíveis = [r for r in results if r[0] and r[5] == '*']
print(f"\nCANAIS COM CORS '*' 100% FUNCIONANDO NO NAVEGADOR: {len(compatíveis)}")
for item in compatíveis[:20]:
    print(f" ✅ [{item[4]}] {item[2]} -> {item[3][:70]}")
