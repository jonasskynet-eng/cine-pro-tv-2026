from pathlib import Path
import sqlite3
import urllib.request
import re

# Buscar no banco todos os links que tenham Discovery
conn = sqlite3.connect(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db')
c = conn.cursor()
c.execute("SELECT id, nome, url, qualidade, status FROM canais WHERE nome LIKE '%Discovery%' OR nome LIKE '%Animal Planet%'")
rows = c.fetchall()
print(f"Total de registros de Discovery no banco: {len(rows)}")

m3u8_links = []
for r in rows:
    url = r[2]
    if '.m3u8' in url:
        m3u8_links.append((r[1], url))

print(f"Total de Discovery com M3U8: {len(m3u8_links)}")
for nome, url in m3u8_links[:20]:
    print(f"- {nome}: {url[:80]}")
