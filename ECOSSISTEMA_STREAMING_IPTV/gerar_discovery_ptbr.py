import sqlite3

servidor = 'http://rtv30t.com:80'
user = 'Wintvx'
pwd = 'Wtv1020'

discovery_ptbr = [
    ("Discovery Channel FHD (PT-BR)", f"{servidor}/live/{user}/{pwd}/71862.m3u8", f"{servidor}/live/{user}/{pwd}/71862.ts", "Ciência, Sobrevivência & Aventura", "Full HD"),
    ("Discovery Kids FHD (PT-BR)", f"{servidor}/live/{user}/{pwd}/71871.m3u8", f"{servidor}/live/{user}/{pwd}/71871.ts", "Infantil & Desenhos Dublados", "Full HD"),
    ("Discovery Turbo FHD (PT-BR)", f"{servidor}/live/{user}/{pwd}/71883.m3u8", f"{servidor}/live/{user}/{pwd}/71883.ts", "Carros, Motos & Mecânica", "Full HD"),
    ("Discovery H&H FHD (PT-BR)", f"{servidor}/live/{user}/{pwd}/71867.m3u8", f"{servidor}/live/{user}/{pwd}/71867.ts", "Irmãos à Obra & Estilo de Vida", "Full HD"),
    ("Animal Planet FHD (PT-BR)", f"{servidor}/live/{user}/{pwd}/71772.m3u8", f"{servidor}/live/{user}/{pwd}/71772.ts", "Vida Selvagem & Natureza", "Full HD"),
    ("ID FHD - Investigação (PT-BR)", f"{servidor}/live/{user}/{pwd}/72150.m3u8", f"{servidor}/live/{user}/{pwd}/72150.ts", "Crimes Reais & Perícia Forense", "Full HD"),
    ("Discovery Science HD (PT-BR)", f"{servidor}/live/{user}/{pwd}/71877.m3u8", f"{servidor}/live/{user}/{pwd}/71877.ts", "Ciência Avançada & Espaço", "HD"),
    ("Discovery World FHD (PT-BR)", f"{servidor}/live/{user}/{pwd}/71887.m3u8", f"{servidor}/live/{user}/{pwd}/71887.ts", "Documentários Globais & Cultura", "Full HD"),
    ("Discovery Theater FHD (PT-BR)", f"{servidor}/live/{user}/{pwd}/71879.m3u8", f"{servidor}/live/{user}/{pwd}/71879.ts", "Expedições Naturais em Alta Definição", "Full HD"),
    ("TLC FHD (PT-BR)", f"{servidor}/live/{user}/{pwd}/72371.m3u8", f"{servidor}/live/{user}/{pwd}/72371.ts", "Comportamento & Reality Shows", "Full HD"),
    ("Food Network FHD (PT-BR)", f"{servidor}/live/{user}/{pwd}/71932.m3u8", f"{servidor}/live/{user}/{pwd}/71932.ts", "Gastronomia & Competições Culinárias", "Full HD"),
    ("HGTV FHD (PT-BR)", f"{servidor}/live/{user}/{pwd}/72142.m3u8", f"{servidor}/live/{user}/{pwd}/72142.ts", "Reformas & Decoração", "Full HD")
]

# 1. Gerar arquivo M3U exclusivo na Área de Trabalho com suporte tanto a M3U8 quanto TS
m3u_desktop = r'C:\Users\jonas\Desktop\DISCOVERY_PT_BR_DUBLADO.m3u'
with open(m3u_desktop, 'w', encoding='utf-8') as f:
    f.write('#EXTM3U name="DISCOVERY NETWORKS BRASIL (DUBLADO PT-BR)"\n')
    for nome, url_m3u8, url_ts, desc, qual in discovery_ptbr:
        f.write(f'#EXTINF:-1 group-title="Discovery Brasil (PT-BR) - {qual}",{nome} - {desc}\n{url_m3u8}\n')

print(f"Lista exclusiva criada na Área de Trabalho: {m3u_desktop}")

# 2. Atualizar o arquivo geral CANAIS_DISCOVERY_2026.m3u
m3u_geral = r'C:\Users\jonas\Desktop\CANAIS_DISCOVERY_2026.m3u'
with open(m3u_geral, 'w', encoding='utf-8') as f:
    f.write('#EXTM3U name="PACOTE OFICIAL DISCOVERY NETWORK 2026 (DUBLADO PT-BR)"\n')
    for nome, url_m3u8, url_ts, desc, qual in discovery_ptbr:
        f.write(f'#EXTINF:-1 group-title="Discovery Brasil (PT-BR)",{nome}\n{url_m3u8}\n')

print(f"Lista CANAIS_DISCOVERY_2026.m3u atualizada!")

# 3. Inserir no banco de dados SQLite
db_path = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

for nome, url_m3u8, url_ts, desc, qual in discovery_ptbr:
    c.execute('SELECT id FROM canais WHERE url = ?', (url_m3u8,))
    r = c.fetchone()
    if r:
        c.execute('UPDATE canais SET status = "ATIVO", categoria = ?, qualidade = ? WHERE id = ?', (desc, qual, r[0]))
    else:
        c.execute('''
            INSERT INTO canais (fonte_id, nome, url, logo, categoria, qualidade, latencia_ms, status, pais, regiao, web_ok)
            VALUES (889, ?, ?, '', ?, ?, 110, 'ATIVO', '🇧🇷 Brasil', 'Discovery Dublado (PT-BR)', 1)
        ''', (nome, url_m3u8, desc, qual))

conn.commit()
conn.close()
print("Banco de dados SQLite atualizado com os feeds PT-BR!")
