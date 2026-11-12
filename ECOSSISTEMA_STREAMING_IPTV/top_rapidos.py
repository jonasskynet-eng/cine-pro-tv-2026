import sqlite3

conn = sqlite3.connect(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db')
c = conn.cursor()
c.execute("""
    SELECT id, nome, url, qualidade, latencia_ms 
    FROM canais 
    WHERE status = 'ATIVO' AND cors_star = 1 AND latencia_ms < 150
    ORDER BY latencia_ms ASC
    LIMIT 15
""")
print("Top 15 canais mais rápidos do Brasil (< 150ms):")
for r in c.fetchall():
    print(f"[{r[4]}ms] {r[1]} ({r[3]}) -> {r[2][:60]}")
