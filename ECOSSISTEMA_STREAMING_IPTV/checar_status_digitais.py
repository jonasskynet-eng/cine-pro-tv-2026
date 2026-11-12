import sqlite3

conn = sqlite3.connect(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db')
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM canais WHERE status = 'ATIVO' AND qualidade = 'Digital'")
total_digital = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM canais WHERE status = 'ATIVO'")
total_geral = c.fetchone()[0]

print(f"Canais estritamente Digitais: {total_digital}")
print(f"Total geral no banco: {total_geral}")
