import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(r"C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db")

conn = sqlite3.connect(CAMINHO_BANCO)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM canais WHERE status = 'ATIVO'")
total = cur.fetchone()[0]

cur.execute("SELECT categoria, COUNT(*) FROM canais WHERE status = 'ATIVO' GROUP BY categoria ORDER BY COUNT(*) DESC")
categorias = cur.fetchall()

cur.execute("SELECT nome, latencia_ms, qualidade FROM canais WHERE status = 'ATIVO' ORDER BY latencia_ms ASC LIMIT 5")
top5 = cur.fetchall()

print(f"Total de Canais com Bom Sinal no Banco: {total}")
print("\nDivisão por Categoria:")
for cat, count in categorias:
    print(f"  • {cat}: {count} canais")

print("\nTop 5 Canais com Resposta Mais Rápida:")
for n, l, q in top5:
    print(f"  ⚡ {n:<32} | {l:>6} ms | {q}")

conn.close()
