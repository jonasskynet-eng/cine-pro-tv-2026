import sqlite3

db = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("SELECT id, nome FROM canais WHERE LOWER(nome) LIKE '%geo-blocked%'")
rows = c.fetchall()
print(f"Total de canais com geo-blocked encontrados: {len(rows)}")
for r in rows[:10]:
    print(" -", r[1])

c.execute("UPDATE canais SET status = 'INATIVO' WHERE LOWER(nome) LIKE '%geo-blocked%'")
conn.commit()
print("Todos os canais Geo-blocked foram desativados com sucesso!")
conn.close()
