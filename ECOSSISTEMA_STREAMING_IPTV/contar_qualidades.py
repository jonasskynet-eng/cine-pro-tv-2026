import sqlite3

conn = sqlite3.connect(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db')
c = conn.cursor()
c.execute("SELECT qualidade, COUNT(*) FROM canais WHERE status = 'ATIVO' GROUP BY qualidade")
for r in c.fetchall():
    print(f"Qualidade: {r[0]} -> {r[1]} canais")
