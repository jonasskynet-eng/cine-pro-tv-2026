import sqlite3
import urllib.request
import ssl

db = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT id, nome, url FROM canais WHERE status = "ATIVO" LIMIT 60')
rows = c.fetchall()

cors_ok = []
for cid, name, u in rows:
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=3) as r:
            cors = r.headers.get('Access-Control-Allow-Origin')
            if cors == '*' or cors:
                cors_ok.append((name, cors, u))
    except:
        pass

print(f"Total testados: {len(rows)}. Com CORS liberado no navegador: {len(cors_ok)}")
for name, cors, u in cors_ok[:10]:
    print(f" - {name} | CORS: {cors} | URL: {u[:60]}")
conn.close()
