import sqlite3
import json

db_path = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

discovery_oficial = [
    ("Discovery Channel", "http://45.171.64.30:6060/play/a032/index.m3u8", "Ciência, Aventura & Sobrevivência (Largados e Pelados, Aeroporto: Área Restrita)", "1080p"),
    ("Discovery Home & Health", "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/39.m3u8", "Estilo de Vida, Reformas & Família (Irmãos à Obra, 90 Dias para Casar)", "1080p"),
    ("Discovery Kids", "http://181.224.200.5:2277/play/a00o/index.m3u8", "Infantil & Pré-escolar (Peppa Pig, O Show da Luna)", "1080p"),
    ("Animal Planet HD", "http://190.128.214.97:64333/play/a01n/index.m3u8", "Vida Selvagem, Animais & Meio Ambiente", "1080p"),
    ("Investigation Discovery (ID)", "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/41.m3u8", "Crimes Reais, Perícia & Mistérios", "1080p"),
    ("Discovery Turbo", "http://38.134.250.110:8000/play/a01y/index.m3u8", "Carros, Motos, Mecânica & Velocidade", "1080p"),
    ("Discovery Science", "http://45.171.64.30:6060/play/a007/index.m3u8", "Ciência Avançada, Espaço & Inovações", "720p"),
    ("TLC (The Learning Channel)", "http://stream.mcquack.net/168/index.m3u8", "Estilo de Vida, Culinária & Curiosidades", "1080p"),
    ("Food Network", "http://168.196.127.137:6001/play/a09v/index.m3u8", "Gastronomia, Competições Culinárias & Grandes Chefs", "1080p"),
    ("HGTV (Home & Garden TV)", "http://38.87.224.19:2220/play/a01p/index.m3u8", "Decoração, Arquitetura & Imóveis", "1080p"),
    ("Discovery Theater HD", "http://181.224.200.5:2277/play/a0bj/index.m3u8", "Documentários Especiais em Alta Definição", "1080p")
]

# Gravar no banco SQLite
for nome, url, desc, qual in discovery_oficial:
    c.execute('SELECT id FROM canais WHERE url = ?', (url,))
    r = c.fetchone()
    if r:
        c.execute('UPDATE canais SET status = "ATIVO", categoria = ?, qualidade = ? WHERE id = ?', (desc, qual, r[0]))
    else:
        c.execute('''
            INSERT INTO canais (fonte_id, nome, url, logo, categoria, qualidade, latencia_ms, status, pais, regiao, web_ok)
            VALUES (888, ?, ?, '', ?, ?, 120, 'ATIVO', '🇧🇷 Brasil', 'Grupo Discovery', 1)
        ''', (nome, url, desc, qual))

conn.commit()
conn.close()

# Gerar arquivo M3U oficial na Área de Trabalho
m3u_file = r'C:\Users\jonas\Desktop\CANAIS_DISCOVERY_2026.m3u'
with open(m3u_file, 'w', encoding='utf-8') as f:
    f.write('#EXTM3U name="PACOTE OFICIAL DISCOVERY NETWORK 2026"\n')
    for nome, url, desc, qual in discovery_oficial:
        f.write(f'#EXTINF:-1 group-title="Discovery Networks - {nome}",{nome} ({qual}) - {desc}\n{url}\n')

print(f"M3U atualizado com os 9 pilares da Discovery + Food Network em {m3u_file}")
