import sqlite3

db_path = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

discovery_list = [
    ("Discovery Channel", "http://45.171.64.30:6060/play/a032/index.m3u8", "Documentários & Ciência", "1080p"),
    ("Discovery Kids", "http://181.224.200.5:2277/play/a00o/index.m3u8", "Infantil & Desenhos", "1080p"),
    ("Discovery Turbo", "http://38.134.250.110:8000/play/a01y/index.m3u8", "Automobilismo & Motores", "1080p"),
    ("Discovery Science", "http://45.171.64.30:6060/play/a007/index.m3u8", "Ciência & Tecnologia", "720p"),
    ("Discovery Theater HD", "http://181.224.200.5:2277/play/a0bj/index.m3u8", "Vida Selvagem & Natureza", "1080p"),
    ("Discovery Home & Health", "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/39.m3u8", "Estilo de Vida & Reforma", "1080p"),
    ("Animal Planet HD", "http://190.128.214.97:64333/play/a01n/index.m3u8", "Natureza & Animais", "1080p"),
    ("Investigation Discovery (ID)", "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/41.m3u8", "Crime Real & Perícia", "1080p"),
    ("HGTV (Home & Garden TV)", "http://38.87.224.19:2220/play/a01p/index.m3u8", "Decoração & Imóveis", "1080p"),
    ("Pluto TV Turbo (24h)", "https://jmp2.uk/plu-6014761dfb91870008ea6463.m3u8", "Automobilismo 24h", "HD"),
    ("Pluto TV Investigation (24h)", "https://jmp2.uk/plu-63808dc806aa4700075f319a.m3u8", "Investigação 24h", "HD")
]

# Inserir ou atualizar no banco
for nome, url, cat, qual in discovery_list:
    c.execute('SELECT id FROM canais WHERE url = ?', (url,))
    row = c.fetchone()
    if row:
        c.execute('UPDATE canais SET status = "ATIVO", categoria = ?, qualidade = ? WHERE id = ?', (cat, qual, row[0]))
    else:
        c.execute('''
            INSERT INTO canais (fonte_id, nome, url, logo, categoria, qualidade, latencia_ms, status, pais, regiao, web_ok)
            VALUES (888, ?, ?, '', ?, ?, 150, 'ATIVO', '🇧🇷 Brasil', 'TV a Cabo / Discovery', 1)
        ''', (nome, url, cat, qual))

conn.commit()
conn.close()

# Gerar arquivo M3U exclusivo na Área de Trabalho
m3u_file = r'C:\Users\jonas\Desktop\CANAIS_DISCOVERY_2026.m3u'
with open(m3u_file, 'w', encoding='utf-8') as f:
    f.write('#EXTM3U name="PACOTE DISCOVERY NETWORK 2026"\n')
    for nome, url, cat, qual in discovery_list:
        f.write(f'#EXTINF:-1 group-title="Discovery Networks - {cat}",{nome} ({qual})\n{url}\n')

print(f"Lista M3U criada na Área de Trabalho: {m3u_file}")
