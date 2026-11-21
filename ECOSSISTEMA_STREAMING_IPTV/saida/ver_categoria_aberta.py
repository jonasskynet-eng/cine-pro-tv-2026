import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}

gists = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_brazil.m3u8"
]

# Vamos buscar todas as ocorrências de TV Aberta no banco de dados local existente:
import sqlite3
conn = sqlite3.connect(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db')
c = conn.cursor()

c.execute("SELECT id, nome, url, latencia_ms FROM canais WHERE categoria LIKE '%Aberta%' OR categoria LIKE '%VIP%'")
rows = c.fetchall()
print(f"Canais na categoria Aberta / VIP no banco: {len(rows)}")
for r in rows[:30]:
    print(r)
conn.close()
