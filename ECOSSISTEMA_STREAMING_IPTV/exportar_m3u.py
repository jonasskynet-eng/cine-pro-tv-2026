import sqlite3

db = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT nome, url, logo, categoria, pais, regiao FROM canais WHERE status = "ATIVO"')
rows = c.fetchall()

m3u_path = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\servico_iptv_comercial.m3u'
with open(m3u_path, 'w', encoding='utf-8') as f:
    f.write('#EXTM3U name="ECOSSISTEMA IPTV E STREAMING LEGAL 2026"\n')
    for r in rows:
        nome, url, logo, cat, pais, regiao = r
        f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{pais} - {regiao}",{nome}\n{url}\n')

print(f"M3U gerado com {len(rows)} canais em {m3u_path}")
conn.close()
