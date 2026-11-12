import sqlite3
import urllib.request
import ssl
from concurrent.futures import ThreadPoolExecutor

db = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute('''
    SELECT id, nome, url, regiao 
    FROM canais 
    WHERE pais LIKE "%Brasil%" 
      AND url LIKE "https://%"
''')
rows = c.fetchall()
conn.close()

print(f"Testando {len(rows)} canais HTTPS do Brasil...")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def testar(item):
    cid, name, u, reg = item
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
            cors = resp.headers.get('Access-Control-Allow-Origin', '')
            if cors == '*' or cors:
                return (True, cid, name, u, reg, cors)
    except:
        pass
    return (False, cid, name, u, reg, '')

with ThreadPoolExecutor(max_workers=25) as ex:
    results = list(ex.map(testar, rows))

https_cors_ok = [r for r in results if r[0]]
print(f"\nCANAIS HTTPS COM CORS '*' COMPROVADOS: {len(https_cors_ok)}")
for item in https_cors_ok[:25]:
    print(f" ✅ [{item[4]}] {item[2]} -> {item[3]}")
