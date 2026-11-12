import sqlite3

db_path = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

esportes_oficial = [
    ("CazéTV (1080p)", "http://138.204.86.4:8080/CAZE_TV/playlist.m3u8", "Futebol ao Vivo, Copa & Campeonatos", "1080p"),
    ("ESPN Brasil (1080p)", "http://181.78.197.59:8000/play/a07z/index.m3u8", "Futebol Internacional, Premier League & Linha de Passe", "1080p"),
    ("ESPN 2 HD", "http://46.151.196.223:14438", "Esportes Americanos, Tênis & Futebol", "1080p"),
    ("ESPN 3 (1080p)", "http://181.78.197.59:8000/play/a081/index.m3u8", "Basquete NBA, Motores & Notícias", "1080p"),
    ("ESPN 4 (1080p)", "http://181.78.197.59:8000/play/a07n/index.m3u8", "LaLiga, Serie A Italiana & Documentários", "1080p"),
    ("ESPN 5 HD", "http://46.151.196.223:14456", "Esportes Globais & Variedades", "1080p"),
    ("ESPN 6 HD", "http://hls1.sua.tv:80/live/espnextrafhd/s.m3u8", "Transmissões Exclusivas & Campeonatos", "1080p"),
    ("FOX Sports (1080p)", "https://d1jzu95oc8fgt3.cloudfront.net/FOX_Sports.m3u8", "Futebol, NFL & Automobilismo", "1080p"),
    ("Combate HD", "http://46.151.196.223:14468/", "UFC, MMA, Boxe & Lutas Marciais", "1080p"),
    ("DAZN 3 Esportes", "http://23.237.104.106:8080/DAZN_3/index.m3u8", "Boxe Internacional & Futebol Europeu", "720p"),
    ("FIFA+ Brasil (Oficial)", "https://e3be9ac5.wurl.com/master/f36d25e7e52f1ba8d7e56eb859c63656.m3u8", "Acervo Oficial da Copa do Mundo & Futebol", "1080p"),
    ("Red Bull TV Esportes", "https://rbmn-live.akamaized.net/hls/live/590964/BoRB-AT/master.m3u8", "Esportes Radicais, Rally, Skate & Surfe", "1080p")
]

# Gravar no banco SQLite
for nome, url, desc, qual in esportes_oficial:
    c.execute('SELECT id FROM canais WHERE url = ?', (url,))
    r = c.fetchone()
    if r:
        c.execute('UPDATE canais SET status = "ATIVO", categoria = ?, qualidade = ? WHERE id = ?', (desc, qual, r[0]))
    else:
        c.execute('''
            INSERT INTO canais (fonte_id, nome, url, logo, categoria, qualidade, latencia_ms, status, pais, regiao, web_ok)
            VALUES (777, ?, ?, '', ?, ?, 110, 'ATIVO', '🇧🇷 Brasil', 'Esportes / Futebol', 1)
        ''', (nome, url, desc, qual))

conn.commit()
conn.close()

# Gerar arquivo M3U exclusivo de esportes na Área de Trabalho
m3u_file = r'C:\Users\jonas\Desktop\CANAIS_ESPORTES_2026.m3u'
with open(m3u_file, 'w', encoding='utf-8') as f:
    f.write('#EXTM3U name="PACOTE OFICIAL DE ESPORTES E FUTEBOL 2026"\n')
    for nome, url, desc, qual in esportes_oficial:
        f.write(f'#EXTINF:-1 group-title="Esportes - {nome}",{nome} ({qual}) - {desc}\n{url}\n')

print(f"Lista M3U de esportes criada com sucesso em: {m3u_file}")
