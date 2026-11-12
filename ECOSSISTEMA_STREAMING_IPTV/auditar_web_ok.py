import sqlite3
import urllib.request
import ssl
from concurrent.futures import ThreadPoolExecutor

db = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Adicionar coluna web_ok se não existir
try:
    c.execute('ALTER TABLE canais ADD COLUMN web_ok INTEGER DEFAULT 0')
    conn.commit()
except:
    pass

c.execute('SELECT id, nome, url FROM canais WHERE pais LIKE "%Brasil%"')
rows = c.fetchall()

print(f"Auditando {len(rows)} canais brasileiros para reprodução direta no navegador...")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def testar_url(item):
    cid, name, u = item
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=2.5) as resp:
            cors = resp.headers.get('Access-Control-Allow-Origin', '')
            if cors == '*' or cors:
                return (cid, 1)
    except:
        pass
    return (cid, 0)

with ThreadPoolExecutor(max_workers=30) as executor:
    results = list(executor.map(testar_url, rows))

web_ativos = [r for r in results if r[1] == 1]
print(f"Canais 100% liberados para navegador (CORS OK): {len(web_ativos)}")

# Atualizar no banco
c.executemany('UPDATE canais SET web_ok = ? WHERE id = ?', [(ok, cid) for cid, ok in results])
conn.commit()
conn.close()
print("Banco de dados atualizado com a flag web_ok!")
