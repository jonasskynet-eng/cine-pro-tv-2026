import sqlite3

conn = sqlite3.connect(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db')
c = conn.cursor()

termos = ['globo', 'sbt', 'cultura', 'record', 'band', 'redetv', 'gazeta', 'tv brasil', 'futura']

for t in termos:
    c.execute(f"SELECT id, nome, url, status, latencia_ms FROM canais WHERE lower(nome) LIKE '%{t}%'")
    res = c.fetchall()
    print(f"\n--- Termo: {t.upper()} (Total encontrados: {len(res)}) ---")
    for r in res[:10]:
        print(f"  ID {r[0]}: {r[1]} | Status: {r[3]} | Latência: {r[4]} | URL: {r[2][:65]}")

conn.close()
