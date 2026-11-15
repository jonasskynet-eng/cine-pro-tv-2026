import sqlite3
import json
import re
import shutil
from pathlib import Path

BASE_DIR = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
SAIDA_DIR = BASE_DIR / "saida"
DB_PATH = SAIDA_DIR / "banco_iptv.db"
DESKTOP_DIR = Path(r"C:\Users\jonas\Desktop\iptv")

SAIDA_DIR.mkdir(parents=True, exist_ok=True)

# 1. Conexão ao banco SQLite
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Garantir desativação de hosts instáveis, links mortos e duplicatas quebradas
c.execute("""
    UPDATE canais 
    SET status = 'INATIVO' 
    WHERE url LIKE '%rtv30t%'
       OR url LIKE '%181.224.200.5%'
       OR url LIKE '%hls1.sua.tv%'
       OR url LIKE '%45.184.109.10%'
       OR url LIKE '%38.134.250.110%'
       OR url LIKE '%45.171.64.30%'
       OR url LIKE '%190.128.214.97%'
       OR url LIKE '%LVW-15748%'
       OR url LIKE '%LVW-10842/LVW10842_513N26MDBL/playlist.m3u8%'
       OR url LIKE '%LVW-10801/LVW10801_Xvg4R0u57n/playlist.m3u8%'
       OR url LIKE '%79.127.238.228%'
       OR url LIKE '%goo.gl%'
       OR url LIKE '%youtube.com%'
       OR url LIKE '%youtu.be%'
       OR LOWER(url) LIKE '%.mpd%'
       OR LOWER(nome) LIKE '%[color%'
       OR nome LIKE '%(Digital HLS)%'
""")

# Desativação definitiva dos 198 canais estrangeiros da Pluto TV (Suécia, Dinamarca, Noruega, Espanha, Itália, França, EUA, etc.)
c.execute("""
    UPDATE canais 
    SET status = 'INATIVO' 
    WHERE (url LIKE '%jmp2.uk%' OR url LIKE '%pluto%' OR nome LIKE '%pluto%')
      AND NOT (id < 600 OR (id BETWEEN 1325 AND 1354))
""")

# Garantir que os 97 canais genuínos da Pluto TV Brasil estejam ATIVOS e sem sufixo '(United States)' incorreto
c.execute("""
    UPDATE canais
    SET status = 'ATIVO',
        nome = REPLACE(REPLACE(nome, ' (United States) BR', ' BR'), ' (United States)', ' BR')
    WHERE (url LIKE '%jmp2.uk%' OR url LIKE '%pluto%')
      AND (id < 600 OR (id BETWEEN 1325 AND 1354))
""")

# Desativação definitiva de canais com termos estrangeiros, trailers, testes, playlists e VODs mortos
termos_lixo_sql = [
    '%romania%', '%france%', '%czech%', '%russia%', '%russian%', '%poland%', '%turkey%', '%türk%',
    '%turkmen%', '%italia%', '%italy%', '%italian%', '%cee%', '%india%', '%hindi%', '%bhojpuri%',
    '%telugu%', '%tamil%', '%asianet%', '%zeetv%', '%b4u%', '%arabic%', '%arabi%', '%germany%',
    '%deutsch%', '%ukraine%', '%netherlands%', '%dutch%', '%sweden%', '%norway%', '%denmark%',
    '%trailer%', '%trailers%', '%not 24/7%', '%google/file%', '%categories/movies.m3u%',
    '%categories/kids.m3u%', '%categories/series.m3u%', '%group-title=%', '%like gecko)%',
    '%viasat kino%', '%city eden kinomistika%', '%filmbox+%', '%chinese%', '%bangla%',
    '%oneplayer.site%', '%fenixhub.online%', '%googleapis.com/drive%', '%googledrive%',
    '%drive.google.com%', '&tv international%', '%colors cineplex%', '%etv cinema%',
    '%star maa movies%', '%zee cinema%', '%cine nanar%', '%artflix movie%', '%4ever drama%',
    '%5 minut tishiny%', '%all weddings we tv%', '%always funny videos%', '%anger management channel%',
    '%animax asia taiwan%', '%antiques roadshow uk%', '%are we there yet?%', '%ava series%',
    '%very local omaha%', '%cafetv24 veneto%'
]
for termo in termos_lixo_sql:
    c.execute("UPDATE canais SET status = 'INATIVO' WHERE LOWER(nome) LIKE ? OR LOWER(url) LIKE ?", (termo, termo))

termos_estrangeiros_br = [
    '%24 hour free movies%', '%24h catalunya%', '%30atv%', '%48 hours%',
    '%5tv corrientes%', '%8 mty%', '%abc 7%', '%abc west%', '%alb uk tv%',
    '%aus abc tv%', '%awe encore%', '%afroland tv%', '%trt %', '%la 2 (canarias)%',
    '%rtve%', '%tve star%', '%scripps news%', '%newsy%', '%las vegas - 13%',
    '%omaha -3news%', '%televisa telenovelas%', '%televisa%', '%bbc drama%',
    '%rt documentary%', '%rt en español%', '%dw %', '%cgtn%', '%bloomberg%'
]
for termo in termos_estrangeiros_br:
    c.execute("UPDATE canais SET status = 'INATIVO' WHERE LOWER(nome) LIKE ? AND pais LIKE '%Brasil%'", (termo,))

# Varredura automática contra canais estrangeiros infiltrados como Brasil (por domínio, país no título ou rede estrangeira)
padrao_url_estrangeira_br = re.compile(
    r"\.(nl|ar|cl|co|pe|mx|es|uy|py|ec|ve|bo|cr|pa|do|gt|hn|sv|ni|cu|pr|de|fr|it|ru|pl|tr|gr|ro|hu|cz|sk|bg|rs|hr|si|ua|by|kz|uz|az|ge|am|il|ae|sa|eg|ma|dz|tn|za|ng|ke|gh|in|pk|bd|lk|np|th|vn|id|my|sg|ph|kr|jp|cn|tw|hk|au|nz|uk)(/|:|$|\?)",
    re.I,
)
padrao_nome_estrangeiro_br = re.compile(
    r"(\|\s*(EUA|USA|ESP|MEX|ARG|COL|CHL|PER|VEN|ECU|URU|PAR|BOL|CRI|PAN|DOM|GTM|HND|SLV|NIC|CUB|PRI|ALE|GER|FRA|ITA|RUS|UK|ING|CAN|JPN|KOR|CHN|IND|M[eé]xico|Costa Rica|espanhol|ingl[eê]s|franc[eê]s))"
    r"|(\b(COSTA RICA:|nieuwsradio|azahares|bibel tv|dasding|dmf|brescia|giornale radio|kronehit|m[aá]s fm|cumbia mix|shockmedia|playoutcenter|usastreams|triple-it|solumedia|tvomix|alsolnet|BRAVO WALT|Beach TV - Panama City|EWTN Espa[nñ]a|FIFA\+ Spain|Kpop Mix|Urban Mix|La 1 Canarias|MyTime Movie Network|Arirang|BR Fernsehen|Balabol|Brat TV|CVN TV|Cadena TV|Canal 4 Posadas|Catamarca|CineLife|Cinepride|Circle|Colosal TV|Dorama|FilmUA|First Channel|Goldmines|INSTITUCIONAL TV|Imperial Television|NHK World|Jenny Live|Lacco Ameno|Lider TV|Master TV|Mir 24|Mireasa|Misiones Cuatro|Muzhskoy|NDR Fernsehen|NTK TV|Nevskiy|OAN Opinion|Palitra|Peques TV|Perviy otdel|Popular TV Cantabria|Power Max Radio|Primocanale|Public Movies|Punjabi Shorts|PursuitUP|Qollasuyo|ROCK FM|RTC Quarta|RTV Diocesana|RTV Drenthe|RTV Maastricht|RTV Noord|RTV Utrecht|RUN:TIME|Radio Alfa|Radio Conexion|Radio Iglesias|Radio NBC Milano|Radio Stereo 5|Radio UP|Retr[oô] TV|Revry|Rossini|Saarland|Shef|Shemaroo|SideWalks|Simon|Skoraya|Smotrim|Star Cinema|Star Family|Studio 100|Studio Pasco|Suriyan|TV BRICS|TV Kujawy|TV\+ Chincha|TVL|TeleTusciaSabina|Telekanal RAI|Teleleonessa|Teleuniverso|Umbria Tv|VR Canal 21|Very Local|Vouli Tileorasi|VoxAfrica|White Channel)\b)",
    re.I,
)
c.execute("SELECT id, nome, url FROM canais WHERE status = 'ATIVO' AND pais LIKE '%Brasil%'")
ids_estrangeiros_br = []
for row_id, row_nome, row_url in c.fetchall():
    url_chk = (row_url or "").replace("jmp2.uk", "")
    if padrao_url_estrangeira_br.search(url_chk) or padrao_nome_estrangeiro_br.search(row_nome or "") or padrao_nome_estrangeiro_br.search(url_chk):
        ids_estrangeiros_br.append((row_id,))
if ids_estrangeiros_br:
    c.executemany("UPDATE canais SET status = 'INATIVO' WHERE id = ?", ids_estrangeiros_br)
    print(f"Expurgo automático de estrangeiros marcados como BR: {len(ids_estrangeiros_br)} removidos")



# Lista Oficial de Canais de TV Aberta do Brasil 100% Verificados e Funcionais
canais_tv_aberta_brasil = [
    {
        "nome": "SBT Nacional HD",
        "url": "https://6836041ea1117.streamlock.net/cverde/cverde/playlist.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/sbt-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "nacional", "comedia"],
        "qualidade": "Digital Leve",
        "latencia": 38,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / Canal Verde",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Cultura SP (Fibra Leve)",
        "url": "http://170.83.16.50/CULTURA/tracks-v1a1/mono.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-cultura-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip", "historia", "infantil"],
        "qualidade": "Fibra Leve",
        "latencia": 35,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "São Paulo / Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Canal Futura (Grupo Globo Fibra)",
        "url": "http://170.83.16.50/FUTURA/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/futura-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip", "historia", "globo"],
        "qualidade": "Fibra Leve",
        "latencia": 37,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / Fundação Roberto Marinho",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "RecordTV Juara HD",
        "url": "https://cdn.live.br1.jmvstream.com/w/LVW-10842/LVW10842_513N26MDBL/chunklist.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/record-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "noticias"],
        "qualidade": "Digital Leve",
        "latencia": 40,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / Centro-Oeste",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Band TV HD (Ao Vivo)",
        "url": "https://video09.logicahost.com.br/tvmodelo/tvmodelo/chunklist_w146878062.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/band-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "esportes", "noticias"],
        "qualidade": "Digital Leve",
        "latencia": 40,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "BandNews TV (Fibra Leve)",
        "url": "http://170.83.16.50/BAND_NEWS/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/band-news-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip", "noticias"],
        "qualidade": "Fibra Leve",
        "latencia": 38,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / Grupo Bandeirantes",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "RedeTV! (Fibra Leve)",
        "url": "http://170.83.16.50/REDE_TV/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/rede-tv-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip", "comedia"],
        "qualidade": "Fibra Leve",
        "latencia": 36,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "São Paulo / Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Brasil (EBC Oficial HD)",
        "url": "https://tvbrasil-stream.ebc.com.br/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-brasil-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "noticias", "historia"],
        "qualidade": "Digital Leve",
        "latencia": 39,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Brasília / Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Gazeta SP (NuvemPlay)",
        "url": "https://tv.nuvemplay.live/hls/40gtv/stream.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-gazeta-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "esportes"],
        "qualidade": "Digital Leve",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "São Paulo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Record News (Fibra Leve)",
        "url": "http://170.83.16.50/RECORD_NEWS/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/record-news-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip", "noticias"],
        "qualidade": "Fibra Leve",
        "latencia": 38,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "BandSports (Fibra Leve)",
        "url": "http://170.83.16.50/BAND_SPORTS/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/band-sports-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["aberta", "vip", "esportes", "combate"],
        "qualidade": "Fibra Leve",
        "latencia": 38,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Cultura SP Oficial (UOL)",
        "url": "https://player-tvcultura.stream.uol.com.br/live/tvcultura.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-cultura-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "historia", "infantil"],
        "qualidade": "Digital Leve",
        "latencia": 45,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "São Paulo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Cultura Fast (FPA)",
        "url": "https://fpa-gateway.tvcultura.com.br:8181/memfs/606caef0-a290-413d-9f1f-8fcdb3a73831.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-cultura-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "historia"],
        "qualidade": "Digital Leve",
        "latencia": 48,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "São Paulo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Cultura SP (WiseStream HD)",
        "url": "https://v-us-01.wisestream.io/memfs/e8740862-7a1f-45f3-acb2-4f357e144059.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-cultura-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "historia"],
        "qualidade": "Digital Leve",
        "latencia": 46,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "São Paulo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "SBT Interior HD",
        "url": "https://cdn.jmvstream.com/w/LVW-10801/LVW10801_Xvg4R0u57n/chunklist.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/sbt-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "nacional"],
        "qualidade": "Digital Leve",
        "latencia": 42,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Interior SP",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Rede Brasil HD",
        "url": "https://redebrasil.nuvemplay.live/hls/stream.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/rede-cnt-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "filmes", "comedia"],
        "qualidade": "Digital Leve",
        "latencia": 45,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Aparecida (Fibra Leve)",
        "url": "http://170.83.16.50/TV_APARECIDA/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-aparecida-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip"],
        "qualidade": "Fibra Leve",
        "latencia": 41,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Canção Nova (Fibra Leve)",
        "url": "http://170.83.16.50/CANCAO_NOVA/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/cancao-nova-tv-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip"],
        "qualidade": "Fibra Leve",
        "latencia": 41,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Senado (Fibra Leve)",
        "url": "http://170.83.16.50/TV_SENADO/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-senado-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip", "noticias"],
        "qualidade": "Fibra Leve",
        "latencia": 42,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Brasília / Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Justiça (Fibra Leve)",
        "url": "http://170.83.16.50/TV_JUSTICA/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-senado-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip", "noticias"],
        "qualidade": "Fibra Leve",
        "latencia": 43,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Brasília / Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Terra Viva (Fibra Leve)",
        "url": "http://170.83.16.50/TERRA_VIVA/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/terraviva-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip", "noticias"],
        "qualidade": "Fibra Leve",
        "latencia": 43,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Canal do Boi (Fibra Leve)",
        "url": "http://170.83.16.50/CANAL_DO_BOI/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/terraviva-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "vip"],
        "qualidade": "Fibra Leve",
        "latencia": 43,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Record News Samsung TV Plus",
        "url": "https://rnw-rn-samsungtvplus.otteravision.com/rnw/rn/rnw_rn.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/record-news-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "noticias"],
        "qualidade": "Digital Leve",
        "latencia": 47,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Gazeta SP (Servidor 186)",
        "url": "http://186.219.52.187/gazeta/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-gazeta-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta"],
        "qualidade": "Digital Leve",
        "latencia": 48,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "São Paulo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Cultura SP (Servidor 186)",
        "url": "http://186.219.52.187/cultura/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-cultura-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "historia"],
        "qualidade": "Digital Leve",
        "latencia": 48,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "São Paulo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV A Crítica HD",
        "url": "https://cdn.live.br1.jmvstream.com/w/LVW-20715/LVW20715_50E3x2MCm2/playlist.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-a-critica-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "entretenimento"],
        "qualidade": "Digital Leve",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Manaus / Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Câmara HD",
        "url": "http://170.83.49.66:8083/TVCAMARAHD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-camara-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "noticias"],
        "qualidade": "Fibra Leve",
        "latencia": 42,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Brasília / Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Canal Rural HD",
        "url": "http://170.83.49.66:8083/CANALRURALHD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/canal-rural-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "noticias"],
        "qualidade": "Fibra Leve",
        "latencia": 43,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Rede CNT HD",
        "url": "http://170.83.49.66:8083/REDECNTHD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/rede-cnt-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta"],
        "qualidade": "Fibra Leve",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "SESC TV HD",
        "url": "http://170.83.49.66:8083/SESCTVHD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/sesc-tv-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "historia", "shows"],
        "qualidade": "Fibra Leve",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
        "status": "ATIVO",
        "cors_star": 1
    }
]

# Lista dos 21 Canais VIP na Fibra Brasileira (170.83.16.50)
canais_vip_fibra = [
    {
        "nome": "Discovery Kids (Digital Leve)",
        "url": "http://170.83.16.50/DISCOVERY_KIDS/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-kids-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "infantil"],
        "qualidade": "Digital",
        "latencia": 45,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Channel (Digital Leve)",
        "url": "http://170.83.16.50/DISCOVERY_CHANNEL/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-channel-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "historia"],
        "qualidade": "Digital",
        "latencia": 45,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Turbo (Digital Leve)",
        "url": "http://170.83.16.50/DISCOVERY_TURBO/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-turbo-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "esportes"],
        "qualidade": "Digital",
        "latencia": 48,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Home & Health (Digital Leve)",
        "url": "http://170.83.16.50/DISCOVERY_HOME_HEALTH/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-home-and-health-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "aberta"],
        "qualidade": "Digital",
        "latencia": 46,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Science (Digital Leve)",
        "url": "http://170.83.16.50/DISCOVERY_SCIENCE/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-science-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "historia"],
        "qualidade": "Digital",
        "latencia": 47,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery World (Digital Leve)",
        "url": "http://170.83.16.50/DISCOVERY_WORLD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-world-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "historia"],
        "qualidade": "Digital",
        "latencia": 49,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Theater (Digital Leve)",
        "url": "http://170.83.16.50/DISCOVERY_THEATER/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-theater-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "historia"],
        "qualidade": "Digital",
        "latencia": 47,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Investigation Discovery (Digital Leve)",
        "url": "http://170.83.16.50/DISCOVERY_ID/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/investigation-discovery-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "filmes"],
        "qualidade": "Digital",
        "latencia": 46,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Animal Planet (Digital Leve)",
        "url": "http://170.83.16.50/ANIMAL_PLANET/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/animal-planet-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "historia"],
        "qualidade": "Digital",
        "latencia": 48,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TLC (Digital Leve)",
        "url": "http://170.83.16.50/TLC/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tlc-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "aberta"],
        "qualidade": "Digital",
        "latencia": 46,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "HGTV (Digital Leve)",
        "url": "http://170.83.16.50/HGTV/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/hgtv-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "aberta"],
        "qualidade": "Digital",
        "latencia": 47,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "History Channel (Digital Leve)",
        "url": "http://170.83.16.50/HISTORY/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/history-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "historia"],
        "qualidade": "Digital",
        "latencia": 46,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Cartoon Network (Digital Leve)",
        "url": "http://170.83.16.50/CARTOON/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/cartoon-network-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "infantil", "comedia"],
        "qualidade": "Digital",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TNT (Digital Leve)",
        "url": "http://170.83.16.50/TNT/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tnt-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "filmes"],
        "qualidade": "Digital",
        "latencia": 45,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Space (Digital Leve)",
        "url": "http://170.83.16.50/SPACE/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/space-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "filmes", "combate"],
        "qualidade": "Digital",
        "latencia": 45,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "AXN (Digital Leve)",
        "url": "http://170.83.16.50/AXN/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/axn-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "filmes", "combate"],
        "qualidade": "Digital",
        "latencia": 46,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Sony Channel (Digital Leve)",
        "url": "http://170.83.16.50/SONY_CHANNEL/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/sony-channel-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "filmes", "comedia"],
        "qualidade": "Digital",
        "latencia": 47,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "ESPN (Digital Leve)",
        "url": "http://170.83.16.50/ESPN/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/espn-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "esportes", "combate"],
        "qualidade": "Digital",
        "latencia": 45,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "BandSports (Digital Leve)",
        "url": "http://170.83.16.50/BAND_SPORTS/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/bandsports-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "esportes", "combate"],
        "qualidade": "Digital",
        "latencia": 46,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "CNN Brasil (Digital Leve)",
        "url": "http://170.83.16.50/CNN_BRASIL/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/cnn-brasil.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "noticias"],
        "qualidade": "Digital",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Lifetime (Digital Leve)",
        "url": "http://170.83.16.50/LIFETIME/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/lifetime-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "filmes"],
        "qualidade": "Digital",
        "latencia": 48,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Sony Movies (Digital Leve)",
        "url": "http://170.83.16.50/SONY_MOVIES/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/sony-movies-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "filmes"],
        "qualidade": "Digital",
        "latencia": 45,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "AMC Brasil HD",
        "url": "http://170.83.49.66:8083/AMCHD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/amc-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "filmes", "series"],
        "qualidade": "Digital",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TV Rá Tim Bum HD",
        "url": "http://170.83.49.66:8083/TVRATIMBUMHD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-ra-tim-bum-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "infantil"],
        "qualidade": "Digital",
        "latencia": 43,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Fish TV (Fibra Leve)",
        "url": "http://170.83.16.50/FISH_TV/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/fish-tv-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "esportes"],
        "qualidade": "Digital",
        "latencia": 45,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "WooHoo (Fibra Leve)",
        "url": "http://170.83.16.50/WOOHOO/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/woohoo-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "esportes", "entretenimento"],
        "qualidade": "Digital",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Travel Box Brazil HD",
        "url": "http://170.83.49.66:8083/TRAVELBOXHD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/travel-box-brazil-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "entretenimento", "historia"],
        "qualidade": "Digital",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Box Kids TV HD",
        "url": "http://170.83.49.66:8083/BOXKIDSHD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/box-kids-tv-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "infantil"],
        "qualidade": "Digital",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Music Box Brazil HD",
        "url": "http://170.83.49.66:8083/MUSICBOXBRASILHD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/music-box-brazil-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "shows", "musica"],
        "qualidade": "Digital",
        "latencia": 44,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Jovem Pan News HD",
        "url": "http://170.83.49.66:8083/JOVEMPANNEWSHD/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/jovem-pan-news-br.png",
        "categoria": "⭐ VIP Fibra",
        "tags": ["vip", "noticias"],
        "qualidade": "Digital",
        "latencia": 42,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    }
]


# Inserir ou atualizar os canais de TV Aberta no banco de dados
for ab in canais_tv_aberta_brasil:
    c.execute("""
        INSERT INTO canais (nome, url, logo, categoria, qualidade, latencia_ms, status, pais, regiao, web_ok, cors_star)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
        ON CONFLICT(url) DO UPDATE SET
            nome=excluded.nome,
            logo=excluded.logo,
            categoria=excluded.categoria,
            pais=excluded.pais,
            regiao=excluded.regiao,
            status='ATIVO',
            latencia_ms=excluded.latencia_ms,
            web_ok=1,
            cors_star=1
    """, (ab["nome"], ab["url"], ab["logo"], ab["categoria"], ab["qualidade"], ab["latencia"], ab["status"], ab["pais"], ab["regiao"]))

# Inserir ou atualizar os canais VIP no banco de dados
for vip in canais_vip_fibra:
    c.execute("""
        INSERT INTO canais (nome, url, logo, categoria, qualidade, latencia_ms, status, pais, regiao, web_ok, cors_star)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
        ON CONFLICT(url) DO UPDATE SET
            nome=excluded.nome,
            logo=excluded.logo,
            categoria=excluded.categoria,
            pais=excluded.pais,
            regiao=excluded.regiao,
            status='ATIVO',
            latencia_ms=excluded.latencia_ms,
            web_ok=1,
            cors_star=1
    """, (vip["nome"], vip["url"], vip["logo"], vip["categoria"], vip["qualidade"], vip["latencia"], vip["status"], vip["pais"], vip["regiao"]))

# Lista Oficial das Principais Rádios FM do Brasil (Extraídas do radiosaovivo.net)
radios_brasil_oficiais = [
    {"nome": "Rádio Mix FM 106.3 SP", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/MIXFM_SAOPAULOAAC_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/mix-fm.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "89 A Rádio Rock 89.1 SP", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO_89FM_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/89-a-rock.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Alpha FM 101.7 SP", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO_ALPHAFMAAC_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/alpha-sp.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Rádio Antena 1 94.7 SP", "url": "https://antenaone.crossradio.com.br/stream/1/", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/antena.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Band FM 96.1 SP", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/BANDFM_SPAAC_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/band.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "BandNews FM 96.9 SP", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/BANDNEWSFM_SPAAC_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/news-sp.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Kiss FM 92.5 SP", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO_KISSFM_ADP_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/kiss.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Energia 97 FM SP", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/ENERGIA_97_FM_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/energia.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Rádio Disney 91.3 SP", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/DISNEY_BRA_SP_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/disney.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Metropolitana FM 98.5 SP", "url": "https://ice.fabricahost.com.br/metropolitana985sp", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/metropolitana-online.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Dumont FM 104.3 SP", "url": "https://8402.brasilstream.com.br/stream?origem=radioaovivo", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/dumont-sp.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "NovaBrasil FM 89.7 SP", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/NOVABRASIL_SPAAC_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/novabrasil.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "CBN FM 90.5 SP", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/CBN_SPAAC_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/cbn.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Top FM 104.1 SP", "url": "https://ice.fabricahost.com.br/topfm1041sp", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/top-fm.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Saudade FM 99.7 Santos", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/SAUDADE_FMAAC_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/saudade.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "Santos / Litoral SP"},
    {"nome": "Feliz FM 92.9 SP", "url": "https://streaming.fox.srv.br:8140/stream/1/", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/feliz.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "São Paulo"},
    {"nome": "Alvorada FM 94.9 BH", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO_ALVORADAAAC_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/alvorada-bh.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "Belo Horizonte / MG"},
    {"nome": "Clube FM 105.5 Brasília", "url": "https://8157.brasilstream.com.br/stream?origem=radiosaovivo", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/clube-brasilia.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "Brasília / DF"},
    {"nome": "Melodia FM 97.5 RJ", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/MELODIAFMAAC_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/melodia-rj.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "Rio de Janeiro"},
    {"nome": "Rádio 93 FM RJ", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/FM93_SC", "logo": "https://cdn.instant.audio/images/logos/radiosaovivo-net/93-fm.png", "categoria": "📻 Rádios & Música", "qualidade": "Áudio HD", "latencia": 25, "pais": "🇧🇷 Brasil", "regiao": "Rio de Janeiro"}
]

for rad in radios_brasil_oficiais:
    c.execute("""
        INSERT INTO canais (nome, url, logo, categoria, qualidade, latencia_ms, status, pais, regiao, web_ok, cors_star)
        VALUES (?, ?, ?, ?, ?, ?, 'ATIVO', ?, ?, 1, 1)
        ON CONFLICT(url) DO UPDATE SET
            nome=excluded.nome,
            logo=excluded.logo,
            categoria=excluded.categoria,
            pais=excluded.pais,
            regiao=excluded.regiao,
            status='ATIVO',
            latencia_ms=excluded.latencia_ms,
            web_ok=1,
            cors_star=1
    """, (rad["nome"], rad["url"], rad["logo"], rad["categoria"], rad["qualidade"], rad["latencia"], rad["pais"], rad["regiao"]))

conn.commit()

# Buscar TODOS os canais ATIVOS do banco com prioridade total para os VIPs da Fibra Brasileira
c.execute("""
    SELECT 
        id, nome, url, logo, categoria, qualidade, latencia_ms, pais, regiao, cors_star
    FROM canais
    WHERE status = 'ATIVO'
      AND url NOT LIKE '%rtv30t%'
      AND url NOT LIKE '%181.224.200.5%'
      AND url NOT LIKE '%hls1.sua.tv%'
      AND url NOT LIKE '%45.184.109.10%'
      AND url NOT LIKE '%38.134.250.110%'
      AND url NOT LIKE '%45.171.64.30%'
      AND url NOT LIKE '%190.128.214.97%'
      AND nome NOT LIKE '%(Digital HLS)%'
    ORDER BY 
        CASE 
            WHEN nome LIKE '%SBT Nacional HD%' THEN 1
            WHEN nome LIKE '%TV Cultura SP (Fibra Leve)%' THEN 2
            WHEN nome LIKE '%Canal Futura (Grupo Globo Fibra)%' THEN 3
            WHEN nome LIKE '%RecordTV Juara HD%' THEN 4
            WHEN nome LIKE '%Band TV HD (Ao Vivo)%' THEN 5
            WHEN nome LIKE '%BandNews TV (Fibra Leve)%' THEN 6
            WHEN nome LIKE '%RedeTV! (Fibra Leve)%' THEN 7
            WHEN nome LIKE '%TV Brasil (EBC Oficial HD)%' THEN 8
            WHEN nome LIKE '%TV Gazeta SP (NuvemPlay)%' THEN 9
            WHEN nome LIKE '%Record News (Fibra Leve)%' THEN 10
            WHEN nome LIKE '%BandSports (Fibra Leve)%' THEN 11
            WHEN nome LIKE '%TV Cultura SP Oficial (UOL)%' THEN 12
            WHEN nome LIKE '%TV Cultura Fast (FPA)%' THEN 13
            WHEN nome LIKE '%TV Cultura SP (WiseStream HD)%' THEN 14
            WHEN nome LIKE '%SBT Interior HD%' THEN 15
            WHEN nome LIKE '%Rede Brasil HD%' THEN 16
            WHEN nome LIKE '%TV Aparecida (Fibra Leve)%' THEN 17
            WHEN nome LIKE '%Canção Nova (Fibra Leve)%' THEN 18
            WHEN nome LIKE '%TV Senado (Fibra Leve)%' THEN 19
            WHEN nome LIKE '%TV Justiça (Fibra Leve)%' THEN 20
            WHEN nome LIKE '%Terra Viva (Fibra Leve)%' THEN 21
            WHEN nome LIKE '%Canal do Boi (Fibra Leve)%' THEN 22
            WHEN nome LIKE '%TV A Crítica HD%' THEN 23
            WHEN nome LIKE '%TV Câmara HD%' THEN 24
            WHEN nome LIKE '%Canal Rural HD%' THEN 25
            WHEN nome LIKE '%Rede CNT HD%' THEN 26
            WHEN nome LIKE '%SESC TV HD%' THEN 27
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Kids%' THEN 28
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Channel%' THEN 29
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Turbo%' THEN 30
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Home & Health%' THEN 31
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Science%' THEN 32
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery World%' THEN 33
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Theater%' THEN 34
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Investigation Discovery%' THEN 35
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Animal Planet%' THEN 36
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%TLC%' THEN 37
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%HGTV%' THEN 38
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%History Channel%' THEN 39
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Cartoon Network%' THEN 40
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%TNT%' THEN 41
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Space%' THEN 42
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%AXN%' THEN 43
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Sony Channel%' THEN 44
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Sony Movies%' THEN 45
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%ESPN%' THEN 46
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%CNN Brasil%' THEN 47
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Lifetime%' THEN 48
            WHEN url LIKE '%170.83.16.50%' THEN 49
            WHEN url LIKE '%170.83.49.66%' THEN 50
            WHEN categoria LIKE '%Rádios%' AND (url LIKE '%streamtheworld%' OR url LIKE '%crossradio%' OR url LIKE '%brasilstream%' OR url LIKE '%fabricahost%' OR url LIKE '%fox.srv.br%') THEN 51
            WHEN pais LIKE '%Brasil%' THEN 55
            WHEN pais LIKE '%Portugal%' THEN 60
            WHEN pais LIKE '%América Latina%' THEN 70
            ELSE 80
        END,
        nome ASC
""")

rows = c.fetchall()
conn.close()

# Normalizar dados e aplicar o sistema de Tags Ricas (História, Combate, Comédia, Shows)
canais_estruturados = []
contagem_paises = {"BR": 0, "PT": 0, "LATAM": 0, "GLOBAL": 0}
contagem_tags = {
    "aberta": 0,
    "series": 0,
    "comedia": 0,
    "shows": 0,
    "historia": 0,
    "combate": 0,
    "entretenimento": 0,
    "filmes": 0,
    "esportes": 0,
    "infantil": 0,
    "vip": 0,
    "noticias": 0,
    "musica": 0
}

numero_global = 1

for r in rows:
    c_id, nome, url, logo, cat_db, qual, lat, pais_db, reg, cors_star = r
    
    # 1. Normalizar País
    p_str = pais_db or "🇧🇷 Brasil"
    if "Brasil" in p_str:
        p_cod = "BR"
        p_label = "🇧🇷 Brasil"
    elif "Portugal" in p_str or "Lusófono" in p_str:
        p_cod = "PT"
        p_label = "🇵🇹 Portugal"
    elif "América Latina" in p_str:
        p_cod = "LATAM"
        p_label = "🌎 América Latina"
    else:
        p_cod = "GLOBAL"
        p_label = "🌐 Internacional"

    contagem_paises[p_cod] = contagem_paises.get(p_cod, 0) + 1

    # 2. Sistema de Tags Multigênero (Permite que um canal apareça em História, Combate, Comédia ou Shows)
    nome_lower = nome.lower()
    cat_lower = (cat_db or "").lower()
    tags = []

    # Tag ABERTA (TV Aberta Brasil Nacional e Regional: SBT, Globo, Cultura, Record, Band, RedeTV!, TV Brasil, Gazeta, etc.)
    if any(k in nome_lower for k in [
        "sbt", "cultura", "futura", "globo", "record", "band ", "bandeirantes", 
        "redetv", "gazeta", "tv brasil", "ebc", "aparecida", "cancao nova", "canção nova", "senado", "justica", "justiça", 
        "camara", "câmara", "terra viva", "canal do boi", "rede brasil", "cnt", "tv escola", "ideal tv", "tv a crítica", "tv a critica", "sesc tv", "canal rural"
    ]) or cat_db == "📺 TV Aberta Brasil":
        tags.append("aberta")
        contagem_tags["aberta"] += 1

    # Tag VIP (Fibra Óptica Dedicada)
    if "170.83.16.50" in url or "vip" in cat_lower:
        tags.append("vip")
        contagem_tags["vip"] += 1

    # Tag INFANTIL (Desenhos, Animações, Kids, Animes Clássicos)
    eh_infantil = any(k in nome_lower for k in [
        "kid", "kids", "infantil", "desenho", "desenhos", "cartoon", "cartoonito", "baby",
        "animac", "nickelodeon", "nick", "disney", "gloob", "turma da monica", "peppa",
        "patrulha canina", "smurfs", "tartarugas ninja", "bob esponja", "avatar: a lenda",
        "oggy", "anime", "naruto", "one piece", "tokusato", "babyfirst", "kuriakos kids",
        "reino infantil"
    ]) or "desenho" in cat_lower or "infantil" in cat_lower
    if eh_infantil:
        tags.append("infantil")
        contagem_tags["infantil"] += 1

    # Tag SÉRIES (Séries 24h, Maratonas, Sitcoms, Novelas, Dramas)
    tem_nome_serie = any(k in nome_lower for k in [
        "serie", "series", "maratona", "sitcom", "novela", "novelas", "dorama", "k-drama",
        "csi", "ncis", "macgyver", "trek", "jornada nas estrelas", "star trek", "jeannie",
        "feiticeira", "chaves", "chapolin", "dexter", "sherlock", "house", "charmed",
        "smallville", "numbers", "kenan", "kel", "icarly", "zoey", "drake", "josh",
        "supernatural", "sobrenatural", "walking dead", "colombo", "schitt", "arnold",
        "detetives medicos", "soap"
    ])
    if tem_nome_serie or ("séries" in cat_lower and not any(k in nome_lower for k in ["cine", "filme", "movie", "telecine", "megapix", "hbo", "paramount", "tnt", "space", "axn"])):
        tags.append("series")
        contagem_tags["series"] += 1

    # Tag FILMES (Cinema, Filmes Clássicos, Telecine, HBO, Megapix, Ação, Drama)
    tem_nome_filme = any(k in nome_lower for k in [
        "filme", "filmes", "movie", "movies", "cine", "cinema", "telecine", "megapix",
        "hbo", "max", "paramount", "adrenalina pura", "netmovies", "tnt", "space",
        "axn", "sony channel", "sony", "lifetime", "warner", "universal", "cinemax",
        "canal brasil", "terror", "suspense", "bang bang", "ficcao cientifica"
    ])
    if (tem_nome_filme or "filme" in cat_lower) and not tem_nome_serie:
        tags.append("filmes")
        contagem_tags["filmes"] += 1
    elif tem_nome_filme:
        tags.append("filmes")
        contagem_tags["filmes"] += 1

    # Tag MÚSICA & RÁDIOS (Clipes, Rádios FM/AM, Áudio e Vídeo)
    if any(k in nome_lower for k in [
        "radio", "rádio", " fm", "fm ", "fm", "music", "musica", "música", "som",
        "hit", "hits", "antena 1", "jovem pan fm", "mix fm", "alpha fm", "kiss fm",
        "metropolitana", "band fm", "nativa", "cbn", "bandnews fm", "clip", "clips",
        "videoclipe", "stingray", "loupe", "karaoke"
    ]) or "música" in cat_lower or "musica" in cat_lower:
        tags.append("musica")
        contagem_tags["musica"] += 1

    # Tag SHOWS (Música Ao Vivo, Festivais, Shows Musicais, Palco, Hits)
    if any(k in nome_lower for k in [
        "show", "shows", "live", "festival", "palco", "rock", "pop", "metal", 
        "sertanejo", "pagode", "mpb", "mtv", "multishow", "trace", "kiss", "club",
        "concert", "acustico", "lollapalooza", "rock in rio", "tomorrowland", "billboard",
        "hits ao vivo", "top 40"
    ]) or "shows" in cat_lower:
        tags.append("shows")
        contagem_tags["shows"] += 1

    # Tag COMÉDIA (Humor, South Park, Sitcom, Pegadinhas, Standup)
    if any(k in nome_lower for k in [
        "comedia", "comedy", "south park", "humor", "risos", "stand-up", "sitcom", 
        "toon", "fun", "chaves", "chapolin", "porta dos fundos", "failarmy", "prank",
        "pegadinhas", "whindersson", "tata werneck", "pipocando", "caceta", "zorra",
        "panico", "comedy central", "stand up", "chupim", "pretinho basico", "porta tv", "portatv"
    ]):
        tags.append("comedia")
        contagem_tags["comedia"] += 1

    # Tag HISTÓRIA (História, Documentários, Ciência, Planeta, Descobertas)
    if any(k in nome_lower for k in [
        "historia", "history", "discovery", "science", "world", "theater", "investigation", 
        "investigacao", "animal planet", "doc", "documentario", "geography", "national", "bio", "curta",
        "planeta", "selvagem", "wild", "nature", "natureza", "biologia", "astronomia", "cosmos",
        "espaco", "nasa", "arqueologia", "egito", "guerra", "dw", "arte", "smithsonian",
        "animais", "aliens", "misterios", "vida real"
    ]) or "document" in cat_lower or "história" in cat_lower:
        tags.append("historia")
        contagem_tags["historia"] += 1

    # Tag COMBATE (Lutas, Boxe, UFC, Artes Marciais, MMA)
    if any(k in nome_lower for k in [
        "combate", "luta", "fight", "mma", "ufc", "boxe", "boxing", "wrestling", "wwe",
        "action", "kickboxing", "jiu", "judo", "muay thai", "bellator", "one championship", "filmes de luta"
    ]):
        tags.append("combate")
        contagem_tags["combate"] += 1

    # Tag ENTRETENIMENTO (Variedades, Reality Shows, Lifestyle, Festivais)
    if any(k in nome_lower for k in [
        "entretenimento", "reality", "catfish", "dating", "shore", 
        "are you the one", "masterchef", "gshow", "canal viva", "lifestyle", "bake off",
        "cozinha", "culinaria", "chef", "moda", "decoracao", "famosos", "celebridades",
        "fofoca", "talk show", "entrevista", "game show", "quiz", "talent", "the voice",
        "idol", "got talent", "shark tank", "drag", "rupaul", "survivor", "soltos",
        "de ferias", "fazenda", "bbb", "kfood", "tastemade", "viagens"
    ]) or "entretenimento" in cat_lower:
        tags.append("entretenimento")
        contagem_tags["entretenimento"] += 1

    # Tag ESPORTES (Futebol, Vôlei, Basquete, F1, Ligas)
    if any(k in nome_lower for k in [
        "esporte", "esportes", "sport", "sports", "futebol", "fut ", "espn", "sportv",
        "fox sports", "band sports", "bandsports", "premiere", "tnt sports", "dazn",
        "nba", "nfl", "formula 1", "f1", "nascar", "motogp", "corrida", "automobilismo", "turbo"
    ]) or "esportes" in cat_lower:
        tags.append("esportes")
        contagem_tags["esportes"] += 1

    # Tag NOTÍCIAS (Jornalismo 24h, Noticiários Globais e Locais)
    if any(k in nome_lower for k in [
        "noticia", "noticias", "news", "jornal", "cnn", "globonews", "bandnews",
        "jovem pan news", "record news", "bloomberg", "reuters", "al jazeera",
        "euronews", "bbc", "climatempo", "canal uol", "uol noticias", "bm&c"
    ]) or "notícias" in cat_lower:
        tags.append("noticias")
        contagem_tags["noticias"] += 1

    # Categoria primária visual rigorosamente separada
    if cat_db == "📺 TV Aberta Brasil" and not any(k in nome_lower for k in ["news", "bandnews", "record news", "jovem pan news"]):
        cat_final = "📺 TV Aberta"
    elif "infantil" in tags:
        cat_final = "🧸 Infantil & Desenhos"
    elif tem_nome_serie or ("series" in tags and not "filmes" in tags):
        cat_final = "🍿 Séries & Maratona"
    elif "filmes" in tags:
        cat_final = "🎬 Filmes & Cinema"
    elif "musica" in tags and not any(k in nome_lower for k in ["mtv", "show", "live"]):
        cat_final = "📻 Rádios & Música"
    elif "shows" in tags:
        cat_final = "🎸 Shows & Música"
    elif "comedia" in tags:
        cat_final = "😂 Comédia & Humor"
    elif "combate" in tags:
        cat_final = "🥊 Combate & Lutas"
    elif "esportes" in tags:
        cat_final = "⚽ Esportes & Ação"
    elif "historia" in tags:
        cat_final = "📜 História & Documentários"
    elif "noticias" in tags:
        cat_final = "📰 Notícias"
    elif "entretenimento" in tags:
        cat_final = "🎭 Entretenimento & Reality"
    elif "aberta" in tags:
        cat_final = "📺 TV Aberta"
    elif "vip" in tags:
        cat_final = "⭐ VIP Fibra"
    else:
        cat_final = "📺 TV Aberta"

    canais_estruturados.append({
        "id": c_id,
        "numero": numero_global,
        "numero_str": f"{numero_global:03d}",
        "nome": nome,
        "url": url,
        "logo": logo or "",
        "categoria": cat_final,
        "tags": tags,
        "qualidade": "Digital",
        "latencia": lat or 45,
        "pais": p_label,
        "pais_codigo": p_cod,
        "regiao": reg or "Nacional",
        "cors": bool(cors_star) or ("170.83.16.50" in url)
    })
    numero_global += 1

total_canais = len(canais_estruturados)
print(f"Total de canais estruturados: {total_canais}")
print(f"Contagem por País: {contagem_paises}")
print(f"Contagem por Tags: {contagem_tags}")

# Gravar JSON limpo
json_path = SAIDA_DIR / "canais_leves.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(canais_estruturados, f, ensure_ascii=False, indent=2)

# Playlists Desktop M3U dedicadas para os gostos do Jonas
def gerar_m3u(caminho, lista, titulo):
    linhas = [f"#EXTM3U\n"]
    for ch in lista:
        linhas.append(f'#EXTINF:-1 tvg-id="{ch["numero_str"]}" tvg-name="{ch["nome"]}" tvg-logo="{ch["logo"]}" group-title="{ch["categoria"]}",{ch["numero_str"]} - {ch["nome"]}\n{ch["url"]}\n')
    caminho.write_text("".join(linhas), encoding="utf-8")

gerar_m3u(DESKTOP_DIR / "CANAIS_TV_ABERTA_BRASIL.m3u", [c for c in canais_estruturados if "aberta" in c["tags"]], "Canais TV Aberta Brasil")
gerar_m3u(DESKTOP_DIR / "CANAIS_SERIES_E_MARATONAS.m3u", [c for c in canais_estruturados if "series" in c["tags"]], "Canais de Séries e Maratonas")
gerar_m3u(DESKTOP_DIR / "CANAIS_DOCUMENTARIOS_E_HISTORIA.m3u", [c for c in canais_estruturados if "historia" in c["tags"]], "Canais de Documentários e História")
gerar_m3u(DESKTOP_DIR / "DISCOVERY_PT_BR_DUBLADO.m3u", [c for c in canais_estruturados if "vip" in c["tags"]], "VIP Fibra Discovery")
gerar_m3u(DESKTOP_DIR / "CANAIS_DIGITAIS_LEVES.m3u", canais_estruturados, "Central Completa Digital")
gerar_m3u(DESKTOP_DIR / "CANAIS_HISTORIA.m3u", [c for c in canais_estruturados if "historia" in c["tags"]], "Canais de História")
gerar_m3u(DESKTOP_DIR / "CANAIS_COMBATE_E_LUTAS.m3u", [c for c in canais_estruturados if "combate" in c["tags"]], "Canais de Combate e Lutas")
gerar_m3u(DESKTOP_DIR / "CANAIS_COMEDIA.m3u", [c for c in canais_estruturados if "comedia" in c["tags"]], "Canais de Comédia")
gerar_m3u(DESKTOP_DIR / "CANAIS_SHOWS_E_MUSICA.m3u", [c for c in canais_estruturados if "shows" in c["tags"] or "musica" in c["tags"]], "Canais de Shows e Música")
gerar_m3u(DESKTOP_DIR / "CANAIS_ENTRETENIMENTO.m3u", [c for c in canais_estruturados if "entretenimento" in c["tags"]], "Canais de Entretenimento")

# Gerar HTML Player Profissional
json_canais_str = json.dumps(canais_estruturados, ensure_ascii=False)

html_code = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#060913">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="manifest" href="/manifest.json">
    <title>CENTRAL DE TV DIGITAL PRO - Cinema Studio 2026</title>
    <script>
        // Se aberto direto pelo arquivo no Desktop, redireciona para o servidor acelerado local
        if (window.location.protocol === 'file:') {{
            window.location.replace('http://localhost:8080/index.html');
        }}
    </script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        :root {{
            --bg-base: #060913;
            --bg-surface: #0c1322;
            --bg-card: #151f32;
            --bg-card-hover: #1e2c46;
            --primary: #3b82f6;
            --emerald: #10b981;
            --emerald-glow: rgba(16, 185, 129, 0.4);
            --amber: #f59e0b;
            --rose: #f43f5e;
            --cyan: #06b6d4;
            --purple: #a855f7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #1e293b;
            --border-hover: #334155;
            --accent-gradient: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }}
        body {{
            background: var(--bg-base);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        /* MODO CINEMA / TELA 100% LIMPA (SÓ O CANAL FUNCIONANDO) */
        body.cinema-mode header,
        body.cinema-mode .sidebar-channels,
        body.cinema-mode .player-info-dock {{
            display: none !important;
        }}
        body.cinema-mode .player-viewport {{
            padding: 0;
        }}
        
        /* CABEÇALHO PROFISSIONAL COM GLASSMORPHISM */
        header {{
            background: rgba(12, 19, 34, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
            padding: 10px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            z-index: 30;
            transition: opacity 0.3s;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .brand-badge {{
            width: 40px;
            height: 40px;
            background: var(--accent-gradient);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            box-shadow: 0 4px 18px var(--emerald-glow);
        }}
        .brand-meta h1 {{
            font-size: 16px;
            font-weight: 800;
            letter-spacing: -0.4px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .brand-meta h1 span.pro-tag {{
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--emerald);
            color: #6ee7b7;
            font-size: 10px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        }}
        .brand-meta p {{
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 1px;
        }}
        .status-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--emerald);
            box-shadow: 0 0 8px var(--emerald);
        }}

        /* BUSCA RÁPIDA */
        .search-wrapper {{
            flex: 1;
            max-width: 460px;
            position: relative;
        }}
        .search-input {{
            width: 100%;
            background: rgba(21, 31, 50, 0.8);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 9px 16px 9px 40px;
            color: #fff;
            font-size: 13px;
            outline: none;
            transition: all 0.2s;
        }}
        .search-input:focus {{
            border-color: var(--emerald);
            background: rgba(30, 44, 70, 0.9);
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
        }}
        .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            font-size: 14px;
        }}
        .search-count {{
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 11px;
            color: var(--text-muted);
            background: #0f172a;
            padding: 2px 7px;
            border-radius: 4px;
            border: 1px solid var(--border);
        }}

        /* AÇÕES SUPERIORES */
        .header-controls {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .btn-ui {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 9px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 7px;
            transition: all 0.2s;
        }}
        .btn-ui:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
            transform: translateY(-1px);
        }}
        .btn-ui.active {{
            background: rgba(16, 185, 129, 0.2);
            border-color: var(--emerald);
            color: #6ee7b7;
        }}

        /* LAYOUT PRINCIPAL */
        .main-stage {{
            flex: 1;
            display: flex;
            overflow: hidden;
            position: relative;
        }}

        /* VIEWPORT DO REPRODUTOR (DISPLAY CINEMA COM ENQUADRAMENTO PADRONIZADO) */
        .player-viewport {{
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #000;
            position: relative;
            padding: 10px 16px 12px 16px;
            transition: padding 0.3s;
            overflow: hidden;
        }}

        /* ÁREA CENTRALIZADA QUE PRESERVA O TAMANHO PADRÃO SEMPRE */
        .screen-stage-wrapper {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 0;
            width: 100%;
            position: relative;
            overflow: hidden;
        }}

        /* TELA PADRONIZADA COM ASPECT-RATIO 16:9 FIXO */
        .screen-container {{
            width: 100%;
            height: 100%;
            max-width: min(100%, calc((100vh - 190px) * (16 / 9)));
            max-height: calc(100vh - 190px);
            aspect-ratio: 16 / 9;
            position: relative;
            background: #020617;
            border-radius: 14px;
            overflow: hidden;
            border: 2px solid rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 14px 45px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(16, 185, 129, 0.15);
            transition: all 0.25s ease;
        }}
        .screen-container::before {{
            content: '';
            position: absolute;
            inset: 0;
            box-shadow: inset 0 0 100px rgba(16, 185, 129, 0.06);
            pointer-events: none;
            z-index: 2;
        }}

        /* VÍDEO COM CONTROLE DE ENQUADRAMENTO */
        video {{
            width: 100%;
            height: 100%;
            background: #000;
            display: block;
            cursor: pointer;
            transition: object-fit 0.2s ease;
        }}
        /* MODOS DE ENQUADRAMENTO DA TELA */
        video.fit-contain {{
            object-fit: contain; /* Padrão 16:9 Cinema Original */
        }}
        video.fit-cover {{
            object-fit: cover; /* Preencher Tela Total (Sem Bordas Pretas) */
        }}
        video.fit-fill {{
            object-fit: fill; /* Esticar 100% */
        }}

        /* BADGE INDICADOR DE PADRÃO 16:9 FIXO (OCULTO PARA NÃO POLUIR A TELA DO CANAL) */
        .screen-standard-tag {{
            display: none !important;
        }}

        /* OVERLAY DE CLIQUE DE REPRODUÇÃO */
        .click-overlay {{
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at center, rgba(12, 19, 34, 0.85) 0%, rgba(6, 9, 19, 0.95) 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 20;
            transition: opacity 0.35s ease;
        }}
        .click-overlay.hidden {{
            opacity: 0;
            pointer-events: none;
        }}
        .pulse-play-circle {{
            width: 90px;
            height: 90px;
            border-radius: 50%;
            background: var(--accent-gradient);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 38px;
            color: #fff;
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            animation: pulse-ring 2s infinite;
            margin-bottom: 20px;
            transition: transform 0.2s;
        }}
        .click-overlay:hover .pulse-play-circle {{
            transform: scale(1.08);
        }}
        @keyframes pulse-ring {{
            0% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            }}
            70% {{
                transform: scale(1.05);
                box-shadow: 0 0 0 28px rgba(16, 185, 129, 0);
            }}
            100% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
            }}
        }}
        .click-overlay h2 {{
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.3px;
            color: #fff;
            margin-bottom: 8px;
        }}
        .click-overlay p {{
            font-size: 13px;
            color: var(--text-muted);
        }}

        /* AVISO DE ÁUDIO MUTADO (CHROME AUTOPLAY) */
        .audio-pill {{
            position: absolute;
            top: 24px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #10b981, #059669);
            color: #fff;
            padding: 9px 22px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 700;
            display: none;
            align-items: center;
            gap: 9px;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            z-index: 22;
            animation: float-pill 1.5s infinite alternate ease-in-out;
        }}
        @keyframes float-pill {{
            from {{ transform: translate(-50%, 0); }}
            to {{ transform: translate(-50%, -7px); }}
        }}

        /* HUD NOTIFICAÇÃO FLUTUANTE */
        .hud-toast {{
            position: absolute;
            top: 24px;
            right: 24px;
            background: rgba(12, 19, 34, 0.9);
            border: 1px solid var(--border);
            backdrop-filter: blur(12px);
            padding: 9px 16px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 600;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
            opacity: 0;
            transform: translateY(-8px);
            transition: all 0.3s;
            pointer-events: none;
            z-index: 25;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }}
        .hud-toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}

        /* PAINEL INFERIOR MINIMALISTA DE INFORMAÇÕES E SETINHAS DE CANAL */
        .player-info-dock {{
            margin-top: 8px;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 8px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            flex-shrink: 0;
        }}
        .channel-zapper-pill {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(9, 14, 26, 0.85);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 4px 6px;
            min-width: 0;
            flex: 1;
            max-width: 560px;
        }}
        .zapper-arrow-btn {{
            width: 40px;
            height: 40px;
            border-radius: 9px;
            background: rgba(16, 185, 129, 0.14);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #6ee7b7;
            font-size: 16px;
            font-weight: 900;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            flex-shrink: 0;
            transition: all 0.15s ease;
        }}
        .zapper-arrow-btn:hover {{
            background: #10b981;
            color: #060913;
            transform: scale(1.05);
            box-shadow: 0 0 14px rgba(16, 185, 129, 0.45);
        }}
        .zapper-arrow-btn:active {{
            transform: scale(0.94);
        }}
        .cur-channel-box {{
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
            flex: 1;
            cursor: pointer;
            padding: 2px 6px;
            border-radius: 8px;
            transition: background 0.15s;
        }}
        .cur-channel-box:hover {{
            background: rgba(255, 255, 255, 0.04);
        }}
        .cur-ch-num {{
            font-size: 17px;
            font-weight: 900;
            font-family: monospace;
            background: #0f172a;
            border: 1px solid var(--border);
            color: var(--emerald);
            padding: 5px 10px;
            border-radius: 8px;
            letter-spacing: -0.5px;
        }}
        .cur-ch-logo {{
            width: 42px;
            height: 42px;
            background: var(--bg-card);
            border-radius: 10px;
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            flex-shrink: 0;
        }}
        .cur-ch-logo img {{
            max-width: 36px;
            max-height: 36px;
            object-fit: contain;
        }}
        .cur-ch-meta {{
            overflow: hidden;
        }}
        .cur-ch-meta h2 {{
            font-size: 14px;
            font-weight: 800;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .badge-pill {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 5px;
            text-transform: uppercase;
        }}
        
        /* LED DE STATUS DO SINAL (VERDE / AMARELO PULSANTE) */
        .signal-led {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
            margin-right: 6px;
            vertical-align: middle;
        }}
        .signal-led.led-green {{
            background: #10b981;
            box-shadow: 0 0 8px #10b981;
            animation: pulse-signal-green 1.8s infinite ease-in-out;
        }}
        .signal-led.led-amber {{
            background: #f59e0b;
            box-shadow: 0 0 7px #f59e0b;
            animation: pulse-signal-amber 2.4s infinite ease-in-out;
        }}
        @keyframes pulse-signal-green {{
            0%, 100% {{ opacity: 1; transform: scale(1); box-shadow: 0 0 8px #10b981; }}
            50% {{ opacity: 0.55; transform: scale(0.85); box-shadow: 0 0 3px #10b981; }}
        }}
        @keyframes pulse-signal-amber {{
            0%, 100% {{ opacity: 1; transform: scale(1); box-shadow: 0 0 7px #f59e0b; }}
            50% {{ opacity: 0.6; transform: scale(0.88); box-shadow: 0 0 2px #f59e0b; }}
        }}

        /* MICRO-BADGE DE LATÊNCIA */
        .lat-pill {{
            font-size: 9px;
            font-weight: 800;
            font-family: monospace;
            padding: 1px 5px;
            border-radius: 4px;
            margin-left: 6px;
            display: inline-block;
            vertical-align: middle;
        }}
        .lat-pill.lat-fast {{
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.35);
            color: #6ee7b7;
        }}
        .lat-pill.lat-norm {{
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: #fcd34d;
        }}
        .badge-amber {{
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.4);
            color: #fcd34d;
        }}

        .badge-digital {{
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #6ee7b7;
        }}
        .badge-pais {{
            background: #1e293b;
            color: #cbd5e1;
            font-size: 11px;
            padding: 2px 8px;
        }}
        .cur-ch-meta p {{
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* GUIA DE PROGRAMAÇÃO EPG */
        .epg-timeline {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 7px 14px;
            border-radius: 10px;
        }}
        .epg-clock {{
            font-size: 11px;
            font-weight: 800;
            color: var(--emerald);
            background: rgba(16, 185, 129, 0.1);
            padding: 3px 7px;
            border-radius: 6px;
        }}
        .epg-desc {{
            font-size: 11px;
            font-weight: 600;
            color: #fff;
            white-space: nowrap;
        }}

        /* CONTROLES RÁPIDOS */
        .player-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .icon-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .icon-btn:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
            color: var(--emerald);
        }}
        .icon-btn-text {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            height: 36px;
            padding: 0 12px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 700;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .icon-btn-text:hover {{
            background: var(--bg-card-hover);
            border-color: var(--emerald);
            color: #6ee7b7;
        }}

        /* LATERAL DIREITA DE CANAIS (COM GAVETA RECOLHÍVEL E FILTRO COM SETINHA) */
        .sidebar-channels {{
            width: 420px;
            min-width: 320px;
            background: var(--bg-surface);
            border-left: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: width 0.25s ease, min-width 0.25s ease, opacity 0.2s ease;
        }}
        body.channels-minimized .sidebar-channels {{
            width: 0 !important;
            min-width: 0 !important;
            border-left: none !important;
            opacity: 0;
            pointer-events: none;
        }}
        .btn-drawer-toggle {{
            background: rgba(16, 185, 129, 0.14);
            border-color: rgba(16, 185, 129, 0.45);
            color: #6ee7b7;
        }}
        .btn-drawer-toggle:hover {{
            background: rgba(16, 185, 129, 0.26);
        }}
        .btn-drawer-toggle.open {{
            background: rgba(16, 185, 129, 0.28);
            border-color: var(--emerald);
            color: #fff;
        }}
        .collapsed-channels-bar {{
            display: none;
            margin-top: 8px;
            background: linear-gradient(90deg, rgba(12, 19, 34, 0.96), rgba(16, 185, 129, 0.14));
            border: 1px solid rgba(16, 185, 129, 0.35);
            border-radius: 10px;
            padding: 8px 14px;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            cursor: pointer;
            font-size: 12.5px;
            color: #e2e8f0;
            flex-shrink: 0;
            transition: all 0.2s ease;
        }}
        .collapsed-channels-bar:hover {{
            border-color: var(--emerald);
            background: linear-gradient(90deg, rgba(16, 185, 129, 0.2), rgba(6, 182, 212, 0.16));
        }}
        body.channels-minimized .collapsed-channels-bar {{
            display: flex;
        }}
        .collapsed-bar-arrow {{
            font-size: 11px;
            font-weight: 800;
            color: #6ee7b7;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.35);
            padding: 3px 10px;
            border-radius: 999px;
            white-space: nowrap;
        }}
        .sidebar-top-actions {{
            display: flex;
            flex-direction: row;
            align-items: center;
            gap: 6px;
            padding: 8px 10px;
            background: #090e1a;
            border-bottom: 1px solid var(--border);
            flex-shrink: 0;
        }}
        .btn-minimize-sidebar,
        .btn-toggle-filters {{
            flex: 1;
            min-width: 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
            padding: 7px 9px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 800;
            cursor: pointer;
            white-space: nowrap;
            overflow: hidden;
            transition: all 0.15s;
        }}
        .mobile-search-box {{
            padding: 8px 10px 4px;
            background: #090e1a;
        }}
        .mobile-search-input {{
            width: 100%;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 7px 10px;
            color: #fff;
            font-size: 12px;
            outline: none;
        }}
        .mobile-search-input:focus {{
            border-color: var(--emerald);
        }}
        .btn-minimize-sidebar {{
            background: rgba(16, 185, 129, 0.14);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #6ee7b7;
        }}
        .btn-minimize-sidebar:hover {{
            background: rgba(16, 185, 129, 0.26);
        }}
        .btn-toggle-filters {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
        }}
        .btn-toggle-filters:hover {{
            border-color: var(--emerald);
            color: #6ee7b7;
        }}
        .sidebar-total-pill {{
            background: #0f172a;
            border: 1px solid rgba(16, 185, 129, 0.35);
            color: #6ee7b7;
            padding: 1px 8px;
            border-radius: 999px;
            font-size: 10.5px;
        }}
        .sidebar-filters-box {{
            display: none;
            flex-direction: column;
            border-bottom: 1px solid var(--border);
        }}
        .sidebar-filters-box.open {{
            display: flex;
        }}

        /* ABAS DE PAÍSES COM CONTAGEM (100% VISÍVEIS SEM CORTES) */
        .country-tabs {{
            display: flex;
            background: #090e1a;
            border-bottom: 1px solid var(--border);
            padding: 8px 10px;
            gap: 5px;
            flex-wrap: wrap;
        }}
        .country-tab-btn {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 5px 9px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s;
        }}
        .country-tab-btn:hover {{
            color: #fff;
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--border-hover);
        }}
        .country-tab-btn.active {{
            background: rgba(16, 185, 129, 0.2);
            border-color: var(--emerald);
            color: #6ee7b7;
        }}
        .tab-count {{
            background: #0f172a;
            border: 1px solid var(--border);
            font-size: 10px;
            padding: 1px 5px;
            border-radius: 10px;
            color: inherit;
        }}

        /* PILULAS DE CATEGORIAS: GRADE INTELIGENTE 100% VISÍVEL (ZERO CORTES) */
        .category-pills {{
            display: flex;
            flex-wrap: wrap;
            padding: 8px 10px;
            gap: 5px;
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border);
            max-height: 125px;
            overflow-y: auto;
        }}
        .category-pills::-webkit-scrollbar {{
            width: 6px;
        }}
        .category-pills::-webkit-scrollbar-track {{
            background: #090e1a;
        }}
        .category-pills::-webkit-scrollbar-thumb {{
            background: #10b981;
            border-radius: 3px;
        }}
        .cat-pill {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 5px 9px;
            border-radius: 14px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
        }}
        .cat-pill:hover {{
            background: var(--bg-card-hover);
            color: #fff;
            border-color: var(--border-hover);
        }}
        .cat-pill.active {{
            background: rgba(16, 185, 129, 0.25);
            border-color: var(--emerald);
            color: #6ee7b7;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
        }}
        .cat-pill.pill-series.active {{
            background: rgba(239, 68, 68, 0.25);
            border-color: #ef4444;
            color: #fca5a5;
            box-shadow: 0 0 12px rgba(239, 68, 68, 0.35);
        }}
        .cat-pill.pill-entretenimento.active {{
            background: rgba(99, 102, 241, 0.25);
            border-color: #6366f1;
            color: #a5b4fc;
            box-shadow: 0 0 12px rgba(99, 102, 241, 0.35);
        }}
        .cat-pill.pill-aberta.active {{
            background: rgba(16, 185, 129, 0.25);
            border-color: var(--emerald);
            color: #6ee7b7;
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.35);
        }}
        .cat-pill.pill-historia.active {{
            background: rgba(245, 158, 11, 0.2);
            border-color: var(--amber);
            color: #fcd34d;
        }}
        .cat-pill.pill-combate.active {{
            background: rgba(244, 63, 94, 0.2);
            border-color: var(--rose);
            color: #fda4af;
        }}
        .cat-pill.pill-comedia.active {{
            background: rgba(6, 182, 212, 0.2);
            border-color: var(--cyan);
            color: #67e8f9;
        }}
        .cat-pill.pill-shows.active {{
            background: rgba(168, 85, 247, 0.2);
            border-color: var(--purple);
            color: #d8b4fe;
        }}
        .cat-pill.pill-filmes.active {{
            background: rgba(225, 29, 72, 0.25);
            border-color: #f43f5e;
            color: #fda4af;
            box-shadow: 0 0 12px rgba(244, 63, 94, 0.35);
        }}
        .cat-pill.pill-infantil.active {{
            background: rgba(234, 179, 8, 0.25);
            border-color: #eab308;
            color: #fef08a;
            box-shadow: 0 0 12px rgba(234, 179, 8, 0.35);
        }}
        .cat-pill.pill-musica.active {{
            background: rgba(139, 92, 246, 0.25);
            border-color: #8b5cf6;
            color: #c4b5fd;
            box-shadow: 0 0 12px rgba(139, 92, 246, 0.35);
        }}
        .cat-pill.pill-vip.active {{
            background: rgba(245, 158, 11, 0.25);
            border-color: #f59e0b;
            color: #fde68a;
            box-shadow: 0 0 12px rgba(245, 158, 11, 0.35);
        }}
        .cat-pill.pill-esportes.active {{
            background: rgba(34, 197, 94, 0.25);
            border-color: #22c55e;
            color: #86efac;
            box-shadow: 0 0 12px rgba(34, 197, 94, 0.35);
        }}
        .cat-pill.pill-noticias.active {{
            background: rgba(59, 130, 246, 0.25);
            border-color: #3b82f6;
            color: #93c5fd;
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.35);
        }}

        /* LISTA ULTRA-LEVE DE CANAIS */
        .channel-list {{
            flex: 1;
            overflow-y: auto;
            padding: 8px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .channel-list::-webkit-scrollbar {{
            width: 8px;
        }}
        .channel-list::-webkit-scrollbar-track {{
            background: #090e1a;
            border-radius: 4px;
        }}
        .channel-list::-webkit-scrollbar-thumb {{
            background: #10b981;
            border-radius: 4px;
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
        }}
        .channel-list::-webkit-scrollbar-thumb:hover {{
            background: #34d399;
            box-shadow: 0 0 12px rgba(52, 211, 153, 0.7);
        }}

        .channel-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 9px 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .channel-card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
            transform: translateX(2px);
        }}
        .channel-card.active {{
            background: rgba(16, 185, 129, 0.12);
            border-color: var(--emerald);
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.2);
        }}
        .channel-card-left {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex: 1;
            overflow: hidden;
        }}
        .ch-num-badge {{
            font-size: 11px;
            font-weight: 800;
            font-family: monospace;
            color: var(--text-muted);
            background: #090e1a;
            padding: 3px 6px;
            border-radius: 5px;
            border: 1px solid var(--border);
            flex-shrink: 0;
        }}
        .channel-card.active .ch-num-badge {{
            color: var(--emerald);
            border-color: var(--emerald);
        }}
        .ch-card-logo {{
            width: 32px;
            height: 32px;
            background: #090e1a;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .ch-card-logo img {{
            max-width: 26px;
            max-height: 26px;
            object-fit: contain;
        }}
        .ch-card-info {{
            flex: 1;
            overflow: hidden;
        }}
        .ch-card-name {{
            font-size: 13px;
            font-weight: 700;
            color: #fff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .channel-card.active .ch-card-name {{
            color: var(--emerald);
        }}
        .ch-card-sub {{
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* EQUALIZADOR ANIMADO PARA O CANAL EM REPRODUÇÃO */
        .equalizer {{
            display: none;
            align-items: flex-end;
            gap: 2px;
            height: 14px;
            margin-right: 6px;
        }}
        .channel-card.active .equalizer {{
            display: flex;
        }}
        .eq-bar {{
            width: 3px;
            background: var(--emerald);
            border-radius: 2px;
            animation: bounce-eq 0.8s infinite ease-in-out alternate;
        }}
        .eq-bar:nth-child(1) {{ height: 6px; animation-delay: 0.1s; }}
        .eq-bar:nth-child(2) {{ height: 14px; animation-delay: 0.3s; }}
        .eq-bar:nth-child(3) {{ height: 9px; animation-delay: 0.2s; }}
        @keyframes bounce-eq {{
            from {{ height: 3px; }}
            to {{ height: 14px; }}
        }}

        .fav-star-btn {{
            background: transparent;
            border: none;
            color: #475569;
            font-size: 15px;
            cursor: pointer;
            padding: 4px;
            transition: color 0.2s;
        }}
        .fav-star-btn:hover,
        .fav-star-btn.starred {{
            color: var(--amber);
        }}

        /* RENDERIZADOR PROGRESSIVO: BOTÃO CARREGAR MAIS */
        .load-more-box {{
            padding: 12px;
            text-align: center;
        }}
        .btn-load-more {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-load-more:hover {{
            background: var(--bg-card-hover);
            border-color: var(--emerald);
            color: #6ee7b7;
        }}

        /* MODAL DE ATALHOS */
        .modal-shade {{
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 50;
        }}
        .modal-shade.open {{
            display: flex;
        }}
        .modal-panel {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            width: 90%;
            max-width: 520px;
            padding: 24px;
            box-shadow: 0 25px 60px rgba(0,0,0,0.6);
        }}
        .modal-title-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }}
        .modal-title-bar h3 {{
            font-size: 17px;
            font-weight: 800;
            color: #fff;
        }}
        .modal-dismiss {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 22px;
            cursor: pointer;
        }}
        .keys-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}
        .key-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--bg-card);
            padding: 9px 14px;
            border-radius: 8px;
            border: 1px solid var(--border);
        }}
        .key-badge {{
            background: #090e1a;
            border: 1px solid #334155;
            color: var(--emerald);
            font-weight: 800;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 5px;
            font-family: monospace;
        }}
        .key-label {{
            font-size: 12px;
            color: var(--text-main);
        }}

        /* LOGO DO TOPO CINE PRO TV */
        .brand-logo-svg {{
            display: flex;
            align-items: center;
        }}
        .brand-substatus {{
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 2px;
        }}

        /* BOTÃO FLUTUANTE EXPANDIR TELA TODA */
        .btn-floating-expand {{
            position: absolute;
            top: 14px;
            right: 14px;
            background: rgba(12, 19, 34, 0.88);
            border: 1.5px solid rgba(16, 185, 129, 0.65);
            color: #ffffff;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 11.5px;
            font-weight: 800;
            letter-spacing: 0.6px;
            z-index: 25;
            cursor: pointer;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.7), 0 0 16px rgba(16, 185, 129, 0.25);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .btn-floating-expand:hover {{
            background: #10b981;
            color: #060913;
            border-color: #34d399;
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.65);
            transform: translateY(-1px) scale(1.03);
        }}
        .btn-floating-expand .expand-icon {{
            font-size: 15px;
        }}

        /* TELA CHEIA VERDADEIRA PARA O SCREEN-CONTAINER */
        .screen-container:fullscreen {{
            width: 100vw !important;
            height: 100vh !important;
            max-width: 100vw !important;
            max-height: 100vh !important;
            border-radius: 0 !important;
            border: none !important;
            background: #000 !important;
        }}
        .screen-container:-webkit-full-screen {{
            width: 100vw !important;
            height: 100vh !important;
            max-width: 100vw !important;
            max-height: 100vh !important;
            border-radius: 0 !important;
            border: none !important;
            background: #000 !important;
        }}
        body.video-fullscreen-mode header,
        body.video-fullscreen-mode .sidebar-channels,
        body.video-fullscreen-mode .player-info-dock,
        body.cinema-mode header,
        body.cinema-mode .sidebar-channels,
        body.cinema-mode .player-info-dock {{
            display: none !important;
        }}
        body.video-fullscreen-mode .main-stage,
        body.video-fullscreen-mode .player-viewport,
        body.video-fullscreen-mode .screen-stage-wrapper,
        body.video-fullscreen-mode .screen-container,
        body.cinema-mode .main-stage,
        body.cinema-mode .player-viewport,
        body.cinema-mode .screen-stage-wrapper,
        body.cinema-mode .screen-container {{
            position: fixed !important;
            inset: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            max-width: 100vw !important;
            max-height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            aspect-ratio: unset !important;
            border-radius: 0 !important;
            border: none !important;
            background: #000 !important;
            z-index: 9999 !important;
        }}
        body.mouse-idle .btn-floating-expand {{
            opacity: 0 !important;
            pointer-events: none !important;
        }}
        body.video-fullscreen-mode.mouse-idle video,
        body.cinema-mode.mouse-idle video {{
            cursor: none !important;
        }}

        /* CARD DO GUIA DE PROGRAMAÇÃO EPG NO DOCK */
        .epg-dock-card {{
            display: flex;
            flex-direction: column;
            gap: 5px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 8px 14px;
            border-radius: 10px;
            min-width: 320px;
            max-width: 440px;
            flex: 1;
        }}
        .epg-top-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            overflow: hidden;
        }}
        .epg-live-badge {{
            font-size: 9.5px;
            font-weight: 900;
            color: #f43f5e;
            background: rgba(244, 63, 94, 0.15);
            border: 1px solid rgba(244, 63, 94, 0.35);
            padding: 2px 6px;
            border-radius: 5px;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
        }}
        .live-pulse-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #f43f5e;
            box-shadow: 0 0 6px #f43f5e;
            animation: pulse-ring 1.5s infinite;
        }}
        .epg-clock {{
            font-size: 11px;
            font-weight: 800;
            color: var(--emerald);
            background: rgba(16, 185, 129, 0.1);
            padding: 2px 6px;
            border-radius: 5px;
            white-space: nowrap;
        }}
        .epg-title {{
            font-size: 11.5px;
            font-weight: 700;
            color: #fff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .epg-progress-track {{
            width: 100%;
            height: 4px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 2px;
            overflow: hidden;
        }}
        .epg-progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #06b6d4 100%);
            border-radius: 2px;
            transition: width 0.5s ease;
        }}
        .epg-bottom-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            font-size: 10.5px;
            overflow: hidden;
        }}
        .epg-next-tag {{
            color: var(--amber);
            font-weight: 800;
            white-space: nowrap;
        }}
        .epg-next-title {{
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
        }}
        .btn-epg-guide {{
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.35);
            color: #6ee7b7;
            font-size: 10px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.15s;
        }}
        .btn-epg-guide:hover {{
            background: #10b981;
            color: #060913;
        }}

        /* MODAL EPG GRADE COMPLETA */
        .epg-modal-panel {{
            max-width: 600px;
            width: 92%;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
        }}
        .epg-modal-header-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .epg-modal-logo {{
            width: 44px;
            height: 44px;
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}
        .epg-modal-logo img {{
            max-width: 85%;
            max-height: 85%;
            object-fit: contain;
        }}
        .epg-schedule-list {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            overflow-y: auto;
            margin-top: 14px;
            padding-right: 4px;
        }}
        .epg-item {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: border-color 0.2s;
        }}
        .epg-item.current {{
            border-color: var(--emerald);
            background: rgba(16, 185, 129, 0.08);
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.15);
        }}
        .epg-item-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .epg-item-time {{
            font-size: 11.5px;
            font-weight: 800;
            font-family: monospace;
            color: var(--emerald);
        }}
        .epg-item-badge {{
            font-size: 10px;
            font-weight: 800;
            padding: 2px 7px;
            border-radius: 4px;
        }}
        .badge-live {{
            background: rgba(244, 63, 94, 0.2);
            color: #fda4af;
            border: 1px solid rgba(244, 63, 94, 0.4);
        }}
        .badge-upcoming {{
            background: rgba(148, 163, 184, 0.15);
            color: #94a3b8;
            border: 1px solid rgba(148, 163, 184, 0.3);
        }}
        .epg-item-title {{
            font-size: 13.5px;
            font-weight: 800;
            color: #fff;
        }}
        .epg-item-desc {{
            font-size: 11.5px;
            color: var(--text-muted);
            line-height: 1.4;
        }}

        /* RESPONSIVIDADE DEDICADA: CELULAR EM PÉ (RETRATO) */
        @media (max-width: 900px) and (orientation: portrait) {{
            body {{
                height: 100vh;
                height: 100dvh;
            }}
            header {{
                height: 44px;
                min-height: 44px;
                padding: 4px 10px;
                gap: 8px;
            }}
            .brand-logo-svg svg {{
                width: 132px;
                height: 26px;
            }}
            .brand-substatus,
            .search-wrapper,
            .header-controls button:not(#btnQrRemote),
            .btn-floating-expand {{
                display: none !important;
            }}
            #btnQrRemote {{
                padding: 5px 10px;
                font-size: 11px;
                white-space: nowrap;
            }}
            .main-stage {{
                flex-direction: column !important;
                justify-content: flex-start !important;
            }}
            .player-viewport {{
                flex: none !important;
                width: 100% !important;
                height: auto !important;
                padding: 6px 8px !important;
                justify-content: flex-start !important;
            }}
            body.channels-minimized .player-viewport {{
                flex: none !important;
                justify-content: flex-start !important;
                padding: 6px 8px 10px !important;
            }}
            .screen-stage-wrapper {{
                flex: none !important;
                width: 100% !important;
                height: auto !important;
            }}
            .screen-container {{
                width: 100% !important;
                max-width: 100% !important;
                height: auto !important;
                aspect-ratio: 16 / 9 !important;
                max-height: none !important;
                border-radius: 10px !important;
                border-width: 1px !important;
            }}
            .pulse-play-circle {{
                width: 52px;
                height: 52px;
                font-size: 22px;
                margin-bottom: 8px;
            }}
            .click-overlay h2 {{
                font-size: 14px;
                margin-bottom: 4px;
                text-align: center;
                padding: 0 10px;
            }}
            .click-overlay p {{
                font-size: 11px;
                text-align: center;
                padding: 0 14px;
            }}
            .audio-pill {{
                top: 8px;
                padding: 5px 12px;
                font-size: 11px;
                white-space: nowrap;
                max-width: 94%;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .hud-toast {{
                top: 8px;
                right: 8px;
                left: 8px;
                padding: 6px 10px;
                font-size: 11px;
                justify-content: center;
            }}
            .player-info-dock {{
                margin-top: 6px;
                padding: 6px 8px;
                gap: 6px;
                flex-wrap: wrap;
                border-radius: 10px;
            }}
            .channel-zapper-pill {{
                width: 100%;
                max-width: 100%;
                padding: 3px 4px;
                gap: 6px;
            }}
            .zapper-arrow-btn {{
                width: 38px;
                height: 36px;
                font-size: 14px;
            }}
            .player-actions {{
                width: 100%;
                display: grid;
                grid-template-columns: auto 1fr auto;
                gap: 6px;
            }}
            .icon-btn-text {{
                justify-content: center;
                height: 34px;
                padding: 0 10px;
                font-size: 11px;
                white-space: nowrap;
            }}
            .cur-ch-num {{
                font-size: 11.5px;
                padding: 3px 6px;
            }}
            .cur-ch-logo {{
                width: 28px;
                height: 28px;
            }}
            .cur-ch-meta h2 {{
                font-size: 12px;
            }}
            .collapsed-channels-bar {{
                margin-top: 6px;
                padding: 9px 12px;
                font-size: 11.5px;
            }}
            .sidebar-channels {{
                width: 100% !important;
                min-width: 100% !important;
                flex: 1 !important;
                min-height: 0 !important;
                border-left: none !important;
                border-top: 1px solid var(--border);
            }}
            .sidebar-top-actions {{
                padding: 6px 8px;
                gap: 6px;
            }}
            .btn-minimize-sidebar,
            .btn-toggle-filters {{
                padding: 6px 8px;
                font-size: 11px;
            }}
            .category-pills {{
                max-height: 105px;
            }}
            body.channels-minimized .sidebar-channels {{
                display: none !important;
            }}
        }}

        /* RESPONSIVIDADE DEDICADA: CELULAR DEITADO (PAISAGEM / LANDSCAPE) */
        @media (max-height: 560px) and (orientation: landscape) {{
            body {{
                height: 100vh;
                height: 100dvh;
            }}
            header,
            .collapsed-channels-bar,
            .btn-floating-expand {{
                display: none !important;
            }}
            .main-stage {{
                flex-direction: row !important;
                width: 100% !important;
                height: 100dvh !important;
            }}
            .player-viewport {{
                flex: 1 !important;
                min-width: 0 !important;
                width: auto !important;
                height: 100dvh !important;
                padding: 4px 6px !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: space-between !important;
                gap: 4px !important;
            }}
            .screen-stage-wrapper {{
                flex: 1 !important;
                min-height: 0 !important;
                width: 100% !important;
                height: auto !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }}
            .screen-container {{
                width: 100% !important;
                height: calc(100dvh - 50px) !important;
                max-width: 100% !important;
                max-height: calc(100dvh - 50px) !important;
                aspect-ratio: unset !important;
                border-radius: 8px !important;
                border-width: 1px !important;
            }}
            .pulse-play-circle {{
                width: 52px;
                height: 52px;
                font-size: 22px;
                margin-bottom: 6px;
            }}
            .click-overlay h2 {{
                font-size: 14px;
                margin-bottom: 3px;
                text-align: center;
                padding: 0 12px;
            }}
            .click-overlay p {{
                font-size: 11px;
                text-align: center;
                padding: 0 14px;
            }}
            .audio-pill {{
                top: 8px;
                padding: 4px 12px;
                font-size: 11px;
                white-space: nowrap;
                max-width: 92%;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .hud-toast {{
                top: 8px;
                right: 10px;
                padding: 5px 10px;
                font-size: 11px;
            }}
            .player-info-dock {{
                margin-top: 0 !important;
                height: 40px !important;
                min-height: 40px !important;
                padding: 3px 6px !important;
                gap: 6px !important;
                flex-wrap: nowrap !important;
                border-radius: 8px !important;
            }}
            .channel-zapper-pill {{
                flex: 1 !important;
                min-width: 0 !important;
                max-width: none !important;
                padding: 2px 4px !important;
                gap: 6px !important;
            }}
            .zapper-arrow-btn {{
                width: 32px !important;
                height: 30px !important;
                font-size: 13px !important;
                border-radius: 6px !important;
            }}
            .cur-channel-box {{
                padding: 0 4px !important;
                gap: 6px !important;
            }}
            .cur-ch-num {{
                font-size: 11px !important;
                padding: 2px 5px !important;
            }}
            .cur-ch-logo {{
                width: 24px !important;
                height: 24px !important;
                border-radius: 6px !important;
            }}
            .cur-ch-meta h2 {{
                font-size: 12px !important;
            }}
            .player-actions {{
                width: auto !important;
                display: flex !important;
                align-items: center !important;
                gap: 4px !important;
                flex-shrink: 0 !important;
            }}
            .icon-btn-text {{
                height: 32px !important;
                padding: 0 8px !important;
                font-size: 11px !important;
                gap: 4px !important;
                white-space: nowrap !important;
            }}
            body:not(.channels-minimized) .sidebar-channels {{
                width: 46vw !important;
                min-width: 260px !important;
                max-width: 360px !important;
                height: 100dvh !important;
                border-left: 1px solid var(--border) !important;
                border-top: none !important;
                flex: none !important;
            }}
            body.channels-minimized .sidebar-channels {{
                width: 0 !important;
                min-width: 0 !important;
                display: none !important;
            }}
            .sidebar-top-actions {{
                padding: 6px 8px;
                gap: 5px;
            }}
            .btn-minimize-sidebar,
            .btn-toggle-filters {{
                padding: 5px 8px;
                font-size: 10.5px;
            }}
            .category-pills {{
                max-height: 92px;
            }}
            .channel-card {{
                padding: 6px 8px;
            }}
        }}

    </style>
</head>
<body class="channels-minimized">

    <!-- CABEÇALHO PROFISSIONAL COM GLASSMORPHISM -->
    <header>
        <div class="brand">
            <div class="brand-logo-svg" title="CINE PRO TV - Central Digital 2026">
                <svg viewBox="0 0 460 88" width="220" height="42">
                    <defs>
                        <linearGradient id="tvGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#10b981"/>
                            <stop offset="50%" stop-color="#06b6d4"/>
                            <stop offset="100%" stop-color="#3b82f6"/>
                        </linearGradient>
                        <linearGradient id="panelGlow" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stop-color="#1e293b"/>
                            <stop offset="100%" stop-color="#090e1a"/>
                        </linearGradient>
                    </defs>
                    <g transform="translate(6, 6)">
                        <rect x="0" y="0" width="76" height="76" rx="20" fill="url(#panelGlow)" stroke="url(#tvGlow)" stroke-width="2.5"/>
                        <path d="M16 24 C 24 20, 52 20, 60 24 C 64 36, 64 48, 60 60 C 52 64, 24 64, 16 60 C 12 48, 12 36, 16 24 Z" fill="rgba(16,185,129,0.15)" stroke="url(#tvGlow)" stroke-width="2"/>
                        <polygon points="34,32 50,42 34,52" fill="url(#tvGlow)"/>
                        <circle cx="58" cy="18" r="3.5" fill="#10b981"/>
                    </g>
                    <text x="96" y="40" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="900" fill="#ffffff" letter-spacing="1">CINE<tspan fill="#10b981">PRO</tspan> <tspan fill="#06b6d4">TV</tspan></text>
                    <rect x="96" y="47" width="210" height="2" rx="1" fill="url(#tvGlow)"/>
                    <text x="96" y="66" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="800" fill="#94a3b8" letter-spacing="2">CENTRAL DIGITAL • 2026</text>
                    <g transform="translate(365, 22)">
                        <rect x="0" y="0" width="80" height="24" rx="6" fill="rgba(16,185,129,0.15)" stroke="#10b981" stroke-width="1.2"/>
                        <text x="40" y="16" font-family="monospace" font-size="10.5" font-weight="900" fill="#6ee7b7" text-anchor="middle">ULTRA HD</text>
                    </g>
                </svg>
            </div>
            <div class="brand-substatus">
                <span class="status-dot"></span>
                <span>Fibra Leve • Zero Travamento • <b id="totalCanaisBadge">{total_canais}</b> Canais</span>
            </div>
        </div>

        <div class="search-wrapper">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" class="search-input" placeholder="Buscar por número (#001), nome, história, combate, comédia, shows...">
            <span class="search-count" id="searchCountBadge">{total_canais}</span>
        </div>

        <div class="header-controls">
            <button id="btnQrRemote" class="btn-ui" style="background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.4); color: #6ee7b7;" title="Controlar pelo Celular">
                📱 Controle Celular
            </button>
            <button id="btnAspectHeader" class="btn-ui" title="Ajuste de Proporção / Enquadramento de Tela (Atalho: Tecla A)">
                📐 <span id="aspectHeaderLabel">16:9 Cinema</span>
            </button>
            <button id="btnFavFilter" class="btn-ui">⭐ Favoritos</button>
            <button id="btnCinemaMode" class="btn-ui" title="Atalho: Tecla C">🎬 Modo Cinema</button>
            <button id="btnKeyHelp" class="btn-ui" title="Atalho: Tecla H">⌨️ Atalhos</button>
        </div>
    </header>

    <div class="main-stage">
        <!-- TELA DO REPRODUTOR (DISPLAY CINEMA STUDIO COM ENQUADRAMENTO PADRONIZADO) -->
        <div class="player-viewport">
            <div class="screen-stage-wrapper">
                <div class="screen-container" id="screenBox">
                    <video id="videoElement" class="fit-contain" autoplay playsinline></video>

                    <!-- BADGE INDICADOR DE TAMANHO PADRÃO 16:9 -->
                    <div class="screen-standard-tag" id="screenStandardBadge">
                        <span class="tag-dot"></span>
                        <span id="screenStandardTagText">PADRÃO 16:9 • CINEMA</span>
                    </div>

                    <!-- BOTÃO PROEMINENTE DE EXPANDIR NA TELA TODA -->
                    <button type="button" id="btnFloatingFullscreen" class="btn-floating-expand" onclick="alternarTelaCheia(event)" title="Expandir Tela Toda (Atalho: Tecla F ou 2 Cliques no Vídeo)">
                        <span class="expand-icon">⛶</span>
                        <span id="btnFloatingFullscreenText">EXPANDIR TELA TODA</span>
                    </button>

                    <!-- OVERLAY INICIAL PARA LIBERAR REPRODUÇÃO IMEDIATA -->
                    <div id="playClickOverlay" class="click-overlay">
                        <div class="pulse-play-circle">▶</div>
                        <h2>CLIQUE PARA ASSISTIR AO VIVO</h2>
                        <p>Sinal instantâneo em fibra óptica brasileira • Qualidade Digital Leve</p>
                    </div>

                    <!-- ALERTA DE SOM DESATIVADO (CHROME AUTOPLAY) -->
                    <div id="audioUnmutePill" class="audio-pill">
                        🔊 Transmissão ao vivo iniciada sem som. Clique aqui para ativar o áudio!
                    </div>

                    <!-- NOTIFICAÇÃO FLUTUANTE HUD -->
                    <div id="hudNotice" class="hud-toast">⚡ Sintonizando canal...</div>
                </div>
            </div>

            <!-- DOCK INFERIOR MINIMALISTA: SETINHAS DE CANAL + AÇÕES ESSENCIAIS -->
            <div class="player-info-dock">
                <div class="channel-zapper-pill">
                    <button type="button" class="zapper-arrow-btn" id="btnZapPrev" title="Canal Anterior (Seta Cima / P)">◀</button>
                    <div class="cur-channel-box" onclick="alternarGavetaCanais(event)" title="Clique para abrir ou minimizar a lista de canais">
                        <div class="cur-ch-num" id="dockChNum">#001</div>
                        <div class="cur-ch-logo" id="dockLogo">⚡</div>
                        <div class="cur-ch-meta">
                            <h2>
                                <span id="dockName">SBT Nacional HD</span>
                            </h2>
                        </div>
                    </div>
                    <button type="button" class="zapper-arrow-btn" id="btnZapNext" title="Próximo Canal (Seta Baixo / N)">▶</button>
                </div>

                <div class="player-actions">
                    <button type="button" class="icon-btn-text" id="epgDockCard" onclick="abrirModalEpg(event)" title="Ver guia de programação do canal">
                        <span>📅</span> <span>Guia</span>
                    </button>
                    <button type="button" class="icon-btn-text btn-drawer-toggle" id="btnToggleChannelsDrawer" onclick="alternarGavetaCanais(event)" title="Mostrar ou minimizar todos os canais">
                        <span>📋</span> <span id="drawerToggleText">Todos os Canais</span> <span id="drawerToggleArrow">▼</span>
                    </button>
                    <button type="button" class="icon-btn-text" id="btnFull" onclick="alternarTelaCheia(event)" title="Expandir Tela Toda (Atalho: Tecla F ou 2 Cliques no Vídeo)">
                        <span>⛶</span> <span id="fullDockLabel">Tela Toda</span>
                    </button>
                </div>
            </div>

            <!-- BARRA COMPACTA QUANDO OS CANAIS ESTÃO MINIMIZADOS -->
            <div id="collapsedChannelsBar" class="collapsed-channels-bar" onclick="alternarGavetaCanais(event)" title="Clique para abrir a lista completa de canais">
                <span>📋 <strong>Ver Todos os Canais</strong> (<span id="collapsedTotalCount">{total_canais}</span> disponíveis)</span>
                <span class="collapsed-bar-arrow">Abrir Lista ▼</span>
            </div>
        </div>

        <!-- BARRA LATERAL RECOLHÍVEL (MINIMIZADA POR PADRÃO COM SETINHA) -->
        <div class="sidebar-channels">
            <div class="sidebar-top-actions">
                <button type="button" id="btnMinimizeSidebar" class="btn-minimize-sidebar" onclick="alternarGavetaCanais(event)">
                    <span>▲ Minimizar</span>
                    <span class="sidebar-total-pill" id="sidebarTotalPill">{total_canais}</span>
                </button>
                <button type="button" id="btnToggleFilters" class="btn-toggle-filters" onclick="alternarPainelFiltros(event)">
                    <span>🎛️ Categorias</span>
                    <span id="filtersToggleArrow">▼</span>
                </button>
            </div>

            <div id="sidebarFiltersBox" class="sidebar-filters-box">
                <div class="mobile-search-box">
                    <input type="text" id="mobileSearchInput" class="mobile-search-input" placeholder="🔍 Buscar canal por nome ou número (#001)...">
                </div>
                <!-- ABAS DE PAÍSES COM CONTAGEM -->
                <div class="country-tabs">
                    <button class="country-tab-btn active" data-country="ALL">
                        ⚡ Todos <span class="tab-count">{total_canais}</span>
                    </button>
                    <button class="country-tab-btn" data-country="BR">
                        🇧🇷 Brasil <span class="tab-count">{contagem_paises['BR']}</span>
                    </button>
                    <button class="country-tab-btn" data-country="PT">
                        🇵🇹 Portugal <span class="tab-count">{contagem_paises['PT']}</span>
                    </button>
                    <button class="country-tab-btn" data-country="LATAM">
                        🌎 Am. Latina <span class="tab-count">{contagem_paises['LATAM']}</span>
                    </button>
                    <button class="country-tab-btn" data-country="GLOBAL">
                        🌐 Global <span class="tab-count">{contagem_paises['GLOBAL']}</span>
                    </button>
                </div>

                <!-- FILTROS DE CATEGORIA COM OS 4 GÊNEROS FAVORITOS DO JONAS EM DESTAQUE -->
                <div class="category-pills">
                    <button class="cat-pill active" data-cat="all">Todos</button>
                    <button class="cat-pill pill-aberta" data-cat="aberta">📺 TV Aberta ({contagem_tags['aberta']})</button>
                    <button class="cat-pill pill-filmes" data-cat="filmes">🎬 Filmes ({contagem_tags['filmes']})</button>
                    <button class="cat-pill pill-series" data-cat="series">🍿 Séries ({contagem_tags['series']})</button>
                    <button class="cat-pill pill-infantil" data-cat="infantil">🧸 Desenhos & Kids ({contagem_tags['infantil']})</button>
                    <button class="cat-pill pill-musica" data-cat="musica">📻 Rádios & Música ({contagem_tags['musica']})</button>
                    <button class="cat-pill pill-vip" data-cat="vip">⭐ VIP Fibra ({contagem_tags['vip']})</button>
                    <button class="cat-pill pill-esportes" data-cat="esportes">⚽ Esportes ({contagem_tags['esportes']})</button>
                    <button class="cat-pill pill-shows" data-cat="shows">🎸 Shows ({contagem_tags['shows']})</button>
                    <button class="cat-pill pill-historia" data-cat="historia">📜 Documentários ({contagem_tags['historia']})</button>
                    <button class="cat-pill pill-comedia" data-cat="comedia">😂 Comédia ({contagem_tags['comedia']})</button>
                    <button class="cat-pill pill-combate" data-cat="combate">🥊 Combate ({contagem_tags['combate']})</button>
                    <button class="cat-pill pill-entretenimento" data-cat="entretenimento">🎭 Reality ({contagem_tags['entretenimento']})</button>
                    <button class="cat-pill pill-noticias" data-cat="noticias">📰 Notícias ({contagem_tags['noticias']})</button>
                </div>
            </div>

            <!-- LISTA ULTRA-LEVE DE CANAIS COM RENDERIZAÇÃO PROGRESSIVA -->
            <div class="channel-list" id="channelListBody">
                <!-- Inserido progressivamente via JS para zero travamento -->
            </div>
        </div>
    </div>

    <!-- MODAL DE GRADE COMPLETA DE PROGRAMAÇÃO (EPG) -->
    <div id="epgModal" class="modal-shade">
        <div class="modal-panel epg-modal-panel">
            <div class="modal-title-bar">
                <div class="epg-modal-header-left">
                    <div class="epg-modal-logo" id="epgModalLogo">⚡</div>
                    <div>
                        <h3 id="epgModalChName">Grade de Programação (EPG)</h3>
                        <p id="epgModalChCategory" style="font-size:11px; color:var(--text-muted);">Sinal Digital em Fibra Óptica</p>
                    </div>
                </div>
                <button class="modal-dismiss" id="epgModalDismiss">✕</button>
            </div>
            <div class="epg-schedule-list" id="epgScheduleList">
                <!-- Inserido dinamicamente via JS -->
            </div>
        </div>
    </div>

    <!-- MODAL DE ATALHOS -->
    <div id="shortcutsModal" class="modal-shade">
        <div class="modal-panel">
            <div class="modal-title-bar">
                <h3>⌨️ Controle Remoto pelo Teclado</h3>
                <button class="modal-dismiss" id="modalDismiss">&times;</button>
            </div>
            <div class="keys-grid">
                <div class="key-row">
                    <span class="key-label">Play / Pausa</span>
                    <span class="key-badge">Espaço / Clique</span>
                </div>
                <div class="key-row">
                    <span class="key-label">Enquadramento de Tela</span>
                    <span class="key-badge">Tecla A</span>
                </div>
                <div class="key-row">
                    <span class="key-label">Próximo Canal</span>
                    <span class="key-badge">Seta Baixo / N</span>
                </div>
                <div class="key-row">
                    <span class="key-label">Canal Anterior</span>
                    <span class="key-badge">Seta Cima / P</span>
                </div>
                <div class="key-row">
                    <span class="key-label">Ajustar Volume</span>
                    <span class="key-badge">Setas ◄ ►</span>
                </div>
                <div class="key-row">
                    <span class="key-label">Mudo / Som</span>
                    <span class="key-badge">M</span>
                </div>
                <div class="key-row">
                    <span class="key-label">Tela Cheia</span>
                    <span class="key-badge">F</span>
                </div>
                <div class="key-row">
                    <span class="key-label">Modo Cinema</span>
                    <span class="key-badge">C</span>
                </div>
                <div class="key-row">
                    <span class="key-label">Sintonizar Canal por Número</span>
                    <span class="key-badge">0 a 9 (+ Enter)</span>
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL DO CONTROLE REMOTO POR CELULAR COM QR CODE -->
    <div id="remoteModal" class="modal-shade">
        <div class="modal-panel" style="text-align: center; max-width: 440px;">
            <div class="modal-title-bar">
                <h3>📱 Controle Remoto no Celular</h3>
                <button class="modal-dismiss" id="remoteModalDismiss">&times;</button>
            </div>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
                Aponte a câmera do seu celular para o QR Code abaixo para controlar a TV pelo Wi-Fi:
            </p>
            <div id="qrcodeBox" style="background: #fff; padding: 14px; border-radius: 14px; display: inline-block; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 16px;">
                <div id="qrcodeContainer"></div>
            </div>
            <div style="background: var(--bg-card); border: 1px solid var(--border); padding: 10px 14px; border-radius: 10px; margin-bottom: 14px; font-family: monospace; font-size: 13px; color: #6ee7b7; word-break: break-all;" id="remoteUrlDisplay">
                Carregando link...
            </div>
            <button class="btn-ui" id="btnCopiarLinkRemote" style="width: 100%; justify-content: center; padding: 10px; font-size: 13px; background: rgba(16, 185, 129, 0.2); border-color: var(--emerald); color: #6ee7b7; cursor: pointer;">
                📋 Copiar Link do Controle
            </button>
        </div>
    </div>

    <script>
        const TODOS_CANAIS = {json_canais_str};
        let hls = null;
        let canalAtualIndex = 0;
        let tentativasErro = 0;
        let favoritos = JSON.parse(localStorage.getItem('iptv_favoritos_pro') || '[]');
        let apenasFavoritos = false;
        let paisFiltro = 'ALL';
        let catFiltro = 'all';

        // Modos de Enquadramento da Tela (Padrão 16:9 sempre uniforme)
        const MODOS_ENQUADRAMENTO = [
            {{ id: 'fit-contain', nome: '16:9 Cinema', desc: 'Proporção 16:9 Cinema padrão' }},
            {{ id: 'fit-cover',   nome: 'Preencher Tela', desc: 'Preenchimento total sem bordas pretas' }},
            {{ id: 'fit-fill',    nome: 'Esticar 100%', desc: 'Esticado aos 4 cantos da tela' }}
        ];
        let enquadramentoIndex = parseInt(localStorage.getItem('iptv_enquadramento_idx') || '0');
        if (isNaN(enquadramentoIndex) || enquadramentoIndex < 0 || enquadramentoIndex >= MODOS_ENQUADRAMENTO.length) {{
            enquadramentoIndex = 0;
        }}

        // Renderização Progressiva (para consumo zero de memória e fluidez 60 FPS)
        let canaisFiltradosCache = [];
        let canaisRenderizadosQtd = 0;
        const LOTE_RENDER = 50;

        const video = document.getElementById('videoElement');
        const playOverlay = document.getElementById('playClickOverlay');
        const unmutePill = document.getElementById('audioUnmutePill');
        const hudToast = document.getElementById('hudNotice');
        const listBody = document.getElementById('channelListBody');
        const searchInput = document.getElementById('searchInput');
        const searchCountBadge = document.getElementById('searchCountBadge');

        function obterBadgeSvgCliente(nome) {{
            const limpo = nome.replace(/\\(.*?\\)|\\[.*?\\]|\\bHD\\b|\\bSD\\b|\\b4K\\b|\\bFHD\\b|\\bDigital\\b|\\bLeve\\b|\\bFibra\\b/gi, '').trim();
            const palavras = limpo.split(/\\s+/).filter(p => !['de','da','do','das','dos','e','the','a','tv'].includes(p.toLowerCase()));
            let iniciais = 'TV';
            if (palavras.length >= 3) iniciais = (palavras[0][0] + palavras[1][0] + palavras[2][0]).toUpperCase();
            else if (palavras.length === 2) iniciais = (palavras[0].slice(0, 2) + palavras[1][0]).toUpperCase();
            else if (palavras.length === 1 && palavras[0].length >= 3) iniciais = palavras[0].slice(0, 3).toUpperCase();
            else if (palavras.length === 1) iniciais = palavras[0].toUpperCase();

            let hash = 0;
            for (let i = 0; i < nome.length; i++) hash = nome.charCodeAt(i) + ((hash << 5) - hash);
            const gradientes = [
                ['#1e3a8a', '#3b82f6'], ['#065f46', '#10b981'], ['#7c2d12', '#f97316'],
                ['#581c87', '#a855f7'], ['#831843', '#ec4899'], ['#164e63', '#06b6d4'],
                ['#881337', '#f43f5e'], ['#1e293b', '#475569'], ['#713f12', '#eab308']
            ];
            const [c1, c2] = gradientes[Math.abs(hash) % gradientes.length];
            return `<div style="width:100%;height:100%;border-radius:8px;background:linear-gradient(135deg, ${{c1}}, ${{c2}});display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900;font-size:11px;letter-spacing:0.5px;box-shadow:inset 0 0 0 1px rgba(255,255,255,0.2);">${{iniciais}}</div>`;
        }}

        function aplicarEnquadramento(idx, notificar = true) {{
            enquadramentoIndex = idx % MODOS_ENQUADRAMENTO.length;
            const modo = MODOS_ENQUADRAMENTO[enquadramentoIndex];
            video.className = modo.id;
            localStorage.setItem('iptv_enquadramento_idx', enquadramentoIndex);

            const lblDock = document.getElementById('aspectDockLabel');
            const lblHeader = document.getElementById('aspectHeaderLabel');
            if (lblDock) lblDock.textContent = modo.nome;
            if (lblHeader) lblHeader.textContent = modo.nome;

            const stdTag = document.getElementById('screenStandardTagText');
            if (stdTag) stdTag.textContent = `PADRÃO 16:9 • ${{modo.nome.toUpperCase()}}`;

            if (notificar) {{
                mostrarHUD(`📐 Enquadramento: ${{modo.nome}} (${{modo.desc}})`);
            }}
        }}

        function alternarEnquadramento() {{
            aplicarEnquadramento((enquadramentoIndex + 1) % MODOS_ENQUADRAMENTO.length, true);
        }}

        function mostrarHUD(texto) {{
            hudToast.textContent = texto;
            hudToast.classList.add('show');
            clearTimeout(window.hudTimer);
            window.hudTimer = setTimeout(() => hudToast.classList.remove('show'), 2400);
        }}

        function obterEpgDinamico(canalObj) {{
            const c = typeof canalObj === 'object' && canalObj !== null ? canalObj : {{ nome: String(canalObj || 'Canal Ao Vivo'), categoria: '' }};
            const nomeLimpo = (c.nome || 'Canal').replace('(Digital Leve)', '').replace('(Fibra Leve)', '').trim();
            const cat = (c.categoria || '').toLowerCase();
            const agora = new Date();
            const h = agora.getHours();
            const min = agora.getMinutes();
            const formatHora = (hora, m) => `${{String((hora + 24) % 24).padStart(2, '0')}}:${{String(m).padStart(2, '0')}}`;

            const inicioBloco = h;
            const fimBloco = h + 1;
            const progresso = Math.max(6, Math.min(96, Math.round((min / 60) * 100)));

            let grade = [
                `Edição Especial • ${{nomeLimpo}}`,
                `Destaque da Programação • ${{nomeLimpo}}`,
                `Sessão Principal • ${{nomeLimpo}}`,
                `Maratona Ao Vivo • ${{nomeLimpo}}`
            ];
            if (cat.includes('esporte')) {{
                grade = [`Arena Ao Vivo • ${{nomeLimpo}}`, `Debate Esportivo`, `Gols & Melhores Momentos`, `Transmissão Especial`];
            }} else if (cat.includes('jornalismo') || cat.includes('not')) {{
                grade = [`Jornal Ao Vivo • ${{nomeLimpo}}`, `Análise & Bastidores`, `Plantão de Notícias`, `Resumo do Dia`];
            }} else if (cat.includes('filme') || cat.includes('cine')) {{
                grade = [`Sessão Cinema • ${{nomeLimpo}}`, `Superestreia HD`, `Clássicos da Tela`, `Cine Especial`];
            }} else if (cat.includes('infantil') || cat.includes('kids') || cat.includes('desenho') || cat.includes('anime')) {{
                grade = [`Festival Animado • ${{nomeLimpo}}`, `Maratona Kids`, `Aventura & Diversão`, `Clube da Animação`];
            }} else if (cat.includes('comédia') || cat.includes('comedia') || cat.includes('humor') || cat.includes('série') || cat.includes('serie')) {{
                grade = [`Maratona de Episódios • ${{nomeLimpo}}`, `Sessão Comédia & Séries`, `Episódios Favoritos`, `Especial Fim de Noite`];
            }}

            const idxProg = h % grade.length;
            const idxProx = (h + 1) % grade.length;
            const idxDepois = (h + 2) % grade.length;

            return {{
                faixa: `${{formatHora(inicioBloco, 0)}} - ${{formatHora(fimBloco, 0)}}`,
                titulo: grade[idxProg],
                progresso: progresso,
                proximaFaixa: `${{formatHora(fimBloco, 0)}} - ${{formatHora(fimBloco + 1, 0)}}`,
                proximoTitulo: grade[idxProx],
                depoisFaixa: `${{formatHora(fimBloco + 1, 0)}} - ${{formatHora(fimBloco + 2, 0)}}`,
                depoisTitulo: grade[idxDepois]
            }};
        }}

        const EH_AMBIENTE_LOCAL = ['localhost', '127.0.0.1'].includes(window.location.hostname) ||
            /^(192\\.168\\.|10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.)/.test(window.location.hostname) ||
            window.location.protocol === 'file:';

        let LOCAL_PROXY_ATIVO = false;
        if (!EH_AMBIENTE_LOCAL) {{
            fetch('http://localhost:8080/api/ip_local', {{ mode: 'cors' }})
                .then(r => {{
                    if (r.ok) {{
                        LOCAL_PROXY_ATIVO = true;
                        aplicarFiltros(true);
                    }}
                }})
                .catch(() => {{}});
        }}

        const MAPA_FALLBACK_HTTPS_NUVEM = {{
            'http://170.83.16.50/CULTURA/tracks-v1a1/mono.m3u8': 'https://player-tvcultura.stream.uol.com.br/live/tvcultura.m3u8',
            'http://170.83.16.50/REDE_TV/index.m3u8': 'https://cdn.live.br1.jmvstream.com/webtv/AVJ-15235/playlist/playlist.m3u8',
            'http://170.83.16.50/RECORD_NEWS/index.m3u8': 'https://rnw-rn-samsungtvplus.otteravision.com/rnw/rn/rnw_rn.m3u8',
            'http://170.83.16.50/TV_APARECIDA/index.m3u8': 'https://cdn.jmvstream.com/w/LVW-9716/LVW9716_HbtQtezcaw/master.m3u8'
        }};

        function sintonizar(idx) {{
            if (idx < 0) idx = TODOS_CANAIS.length - 1;
            if (idx >= TODOS_CANAIS.length) idx = 0;
            canalAtualIndex = idx;
            tentativasErro = 0;
            clearTimeout(window.autoZapTimer);
            clearTimeout(window.stallCheckTimer);

            const c = TODOS_CANAIS[idx];
            document.getElementById('dockChNum').textContent = `#${{c.numero_str}}`;
            document.getElementById('dockName').textContent = c.nome;

            const logoBox = document.getElementById('dockLogo');
            const safeName = c.nome.replace(/'/g, "\\'");
            if (c.logo) {{
                logoBox.innerHTML = `<img src="${{c.logo}}" alt="${{c.nome}}" onerror="this.outerHTML=obterBadgeSvgCliente('${{safeName}}')">`;
            }} else {{
                logoBox.innerHTML = obterBadgeSvgCliente(c.nome);
            }}

            const epg = obterEpgDinamico(c);
            const epgTimeEl = document.getElementById('epgTimeBadge');
            const epgProgEl = document.getElementById('epgProgBadge');
            const epgNext = document.getElementById('epgNextBadge');
            if (epgTimeEl) epgTimeEl.textContent = epg.faixa;
            if (epgProgEl) epgProgEl.textContent = epg.titulo;
            if (epgNext) epgNext.textContent = `${{epg.proximaFaixa.split(' - ')[0]}} • ${{epg.proximoTitulo}}`;

            mostrarHUD(`⚡ Sintonizando CH #${{c.numero_str}}: ${{c.nome}}`);

            // Notificar status atual e EPG apenas quando rodando conectado ao servidor local
            if (EH_AMBIENTE_LOCAL) {{
                const epgAtualStr = `${{epg.faixa}} • ${{epg.titulo}}`;
                const epgProxStr = `A seguir (${{epg.proximaFaixa.split(' - ')[0]}}): ${{epg.proximoTitulo}}`;
                fetch(`/api/status_tv?canal_numero=${{c.numero}}&canal_nome=${{encodeURIComponent(c.nome)}}&epg_atual=${{encodeURIComponent(epgAtualStr)}}&epg_proximo=${{encodeURIComponent(epgProxStr)}}`).catch(() => {{}});
            }}

            if (hls) {{
                hls.destroy();
                hls = null;
            }}
            video.onerror = null;

            // Roteamento híbrido inteligente: Local (proxy Python 8080) vs Nuvem (HTTPS direto / fallback CORS)
            let urlBase = c.url;
            if (!EH_AMBIENTE_LOCAL && !LOCAL_PROXY_ATIVO && MAPA_FALLBACK_HTTPS_NUVEM[c.url]) {{
                urlBase = MAPA_FALLBACK_HTTPS_NUVEM[c.url];
            }}

            let streamUrl = urlBase;
            if (EH_AMBIENTE_LOCAL) {{
                const PROXY_ORIGIN = window.location.protocol.startsWith('http') ? window.location.origin : 'http://localhost:8080';
                if (urlBase.includes('170.83.16.50')) {{
                    // Fibra nativa direta com CORS *
                    streamUrl = urlBase;
                }} else {{
                    streamUrl = PROXY_ORIGIN + '/proxy?url=' + encodeURIComponent(urlBase);
                }}
            }} else if (LOCAL_PROXY_ATIVO) {{
                if (urlBase.includes('170.83.16.50')) {{
                    streamUrl = urlBase;
                }} else {{
                    streamUrl = 'http://localhost:8080/proxy?url=' + encodeURIComponent(urlBase);
                }}
            }} else {{
                // Modo Nuvem Puro (Netlify/HTTPS): usa stream HTTPS direto sem depender de /proxy
                if (window.location.protocol === 'https:' && urlBase.startsWith('http://')) {{
                    mostrarHUD('⚠️ Canal HTTP local indisponível na nuvem sem servidor ativo. Pulando para próximo canal HTTPS...');
                    clearTimeout(window.autoZapTimer);
                    window.autoZapTimer = setTimeout(() => navegarCanal(1), 2200);
                    destacarCanalAtivo();
                    return;
                }}
                streamUrl = urlBase;
            }}

            const ehRadioDireta = !urlBase.includes('.m3u8') && (
                (c.categoria && c.categoria.includes('Rádios')) ||
                /streamtheworld|crossradio|brasilstream|fabricahost|fox\\.srv\\.br/i.test(urlBase)
            );

            if (ehRadioDireta) {{
                video.src = urlBase;
                playOverlay.classList.add('hidden');
                tentativasErro = 0;
                const playRadio = video.play();
                if (playRadio !== undefined) {{
                    playRadio.catch(() => {{
                        video.muted = true;
                        video.play().then(() => {{
                            unmutePill.style.display = 'flex';
                        }}).catch(() => {{}});
                    }});
                }}
                video.onerror = () => {{
                    mostrarHUD('⚠️ Rádio temporariamente indisponível. Pulando...');
                    clearTimeout(window.autoZapTimer);
                    window.autoZapTimer = setTimeout(() => navegarCanal(1), 2500);
                }};
                destacarCanalAtivo();
                return;
            }}

            if (Hls.isSupported()) {{
                hls = new Hls({{
                    enableWorker: true,
                    lowLatencyMode: true,
                    backBufferLength: 30,
                    maxBufferLength: 30,
                    maxMaxBufferLength: 60,
                    liveSyncDurationCount: 3,
                    fragLoadingMaxRetry: 4,
                    manifestLoadingMaxRetry: 4
                }});

                hls.loadSource(streamUrl);
                hls.attachMedia(video);

                hls.on(Hls.Events.MANIFEST_PARSED, function () {{
                    playOverlay.classList.add('hidden');
                    tentativasErro = 0;
                    clearTimeout(window.autoZapTimer);
                    clearTimeout(window.stallCheckTimer);

                    const playPromise = video.play();
                    if (playPromise !== undefined) {{
                        playPromise.then(() => {{
                            // Se após 3.5s continuar em 0:00 sem avançar, avança para a ponta do buffer ao vivo
                            window.stallCheckTimer = setTimeout(() => {{
                                if (video.currentTime === 0 && !video.paused && video.buffered && video.buffered.length > 0) {{
                                    try {{
                                        video.currentTime = Math.max(0, video.buffered.end(video.buffered.length - 1) - 1);
                                    }} catch(e) {{}}
                                }}
                            }}, 3500);
                        }}).catch(() => {{
                            video.muted = true;
                            video.play().then(() => {{
                                unmutePill.style.display = 'flex';
                            }});
                        }});
                    }}
                }});

                hls.on(Hls.Events.ERROR, function (event, data) {{
                    if (data.fatal) {{
                        switch (data.type) {{
                            case Hls.ErrorTypes.NETWORK_ERROR:
                                tentativasErro++;
                                if (tentativasErro >= 2) {{
                                    mostrarHUD('⚠️ Sinal com instabilidade de rede. Avançando para o próximo canal em 2s...');
                                    clearTimeout(window.autoZapTimer);
                                    window.autoZapTimer = setTimeout(() => {{
                                        navegarCanal(1);
                                    }}, 2000);
                                }} else {{
                                    mostrarHUD('⚠️ Reconectando sinal ao vivo...');
                                    hls.startLoad();
                                }}
                                break;
                            case Hls.ErrorTypes.MEDIA_ERROR:
                                mostrarHUD('🔧 Recuperando decodificador de vídeo...');
                                hls.recoverMediaError();
                                break;
                            default:
                                mostrarHUD('⚠️ Canal indisponível. Mudando para o próximo canal...');
                                clearTimeout(window.autoZapTimer);
                                window.autoZapTimer = setTimeout(() => {{
                                    navegarCanal(1);
                                }}, 2000);
                                break;
                        }}
                    }}
                }});
            }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                video.src = streamUrl;
                video.play().catch(() => {{
                    video.muted = true;
                    video.play();
                }});
            }}

            destacarCanalAtivo();
        }}

        function destacarCanalAtivo() {{
            document.querySelectorAll('.channel-card').forEach(card => {{
                const cardIdx = parseInt(card.getAttribute('data-idx'));
                card.classList.toggle('active', cardIdx === canalAtualIndex);
            }});
            const activeCard = document.querySelector(`.channel-card[data-idx="${{canalAtualIndex}}"]`);
            if (activeCard) {{
                activeCard.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}
        }}

        function alternarFavorito(id, event) {{
            if (event) event.stopPropagation();
            const idx = favoritos.indexOf(id);
            if (idx > -1) {{
                favoritos.splice(idx, 1);
                mostrarHUD('⭐ Removido dos favoritos');
            }} else {{
                favoritos.push(id);
                mostrarHUD('⭐ Adicionado aos favoritos');
            }}
            localStorage.setItem('iptv_favoritos_pro', JSON.stringify(favoritos));
            aplicarFiltros(false);
        }}

        function aplicarFiltros(resetScroll = true) {{
            const mobileSearchInput = document.getElementById('mobileSearchInput');
            const termoRaw = (searchInput && searchInput.value ? searchInput.value : (mobileSearchInput ? mobileSearchInput.value : ''));
            const termo = termoRaw.toLowerCase().trim();

            canaisFiltradosCache = TODOS_CANAIS.filter(c => {{
                // Em nuvem HTTPS sem proxy local, exibe apenas canais e rádios compatíveis
                if (!ehCanalDisponivelAgora(c)) return false;

                // Filtro de Favoritos
                if (apenasFavoritos && !favoritos.includes(c.id)) return false;

                // Filtro de País
                if (paisFiltro !== 'ALL' && c.pais_codigo !== paisFiltro) return false;

                // Filtro de Categoria Multigênero (Tags)
                if (catFiltro !== 'all') {{
                    if (c.tags && !c.tags.includes(catFiltro)) return false;
                }}

                // Filtro de Busca (por número #001, nome, categoria ou país)
                if (termo) {{
                    const bateNome = c.nome.toLowerCase().includes(termo);
                    const bateNum = c.numero_str.includes(termo) || (`#${{c.numero_str}}`).includes(termo);
                    const bateCat = c.categoria.toLowerCase().includes(termo);
                    const batePais = c.pais.toLowerCase().includes(termo);
                    const bateTags = c.tags ? c.tags.some(t => t.includes(termo)) : false;
                    return bateNome || bateNum || bateCat || batePais || bateTags;
                }}
                return true;
            }});

            searchCountBadge.textContent = `${{canaisFiltradosCache.length}} canais`;
            const collapsedCountEl = document.getElementById('collapsedTotalCount');
            const sidebarPillEl = document.getElementById('sidebarTotalPill');
            if (collapsedCountEl) collapsedCountEl.textContent = canaisFiltradosCache.length;
            if (sidebarPillEl) sidebarPillEl.textContent = canaisFiltradosCache.length;

            if (resetScroll) {{
                listBody.innerHTML = '';
                canaisRenderizadosQtd = 0;
            }}

            if (canaisFiltradosCache.length === 0) {{
                listBody.innerHTML = '<div style="padding:30px; text-align:center; color:#64748b; font-size:13px;">Nenhum canal encontrado para este filtro.</div>';
                return;
            }}

            renderizarMaisCanais();
        }}

        function renderizarMaisCanais() {{
            const proximoLote = canaisFiltradosCache.slice(canaisRenderizadosQtd, canaisRenderizadosQtd + LOTE_RENDER);
            if (proximoLote.length === 0) return;

            const fragment = document.createDocumentFragment();

            proximoLote.forEach(c => {{
                const realIndex = TODOS_CANAIS.findIndex(x => x.id === c.id);
                const isSelected = realIndex === canalAtualIndex;
                const isFav = favoritos.includes(c.id);

                const card = document.createElement('div');
                card.className = `channel-card ${{isSelected ? 'active' : ''}}`;
                card.setAttribute('data-idx', realIndex);
                card.onclick = () => {{
                    sintonizar(realIndex);
                    if ((window.innerWidth <= 950 || window.innerHeight <= 560) && !document.body.classList.contains('channels-minimized')) {{
                        alternarGavetaCanais(null, false);
                    }}
                }};

                const safeName = c.nome.replace(/'/g, "\\'");
                const logoHtml = c.logo ? `<img src="${{c.logo}}" alt="${{c.nome}}" onerror="this.outerHTML=obterBadgeSvgCliente('${{safeName}}')">` : obterBadgeSvgCliente(c.nome);

                card.innerHTML = `
                    <div class="channel-card-left">
                        <span class="ch-num-badge">#${{c.numero_str}}</span>
                        <div class="ch-card-logo">${{logoHtml}}</div>
                        <div class="ch-card-info">
                            <div class="ch-card-name">${{c.nome}}</div>
                            <div class="ch-card-sub">
                                <span>${{c.pais}}</span> • <span>${{c.categoria}}</span>
                            </div>
                        </div>
                    </div>
                    <div class="equalizer">
                        <div class="eq-bar"></div>
                        <div class="eq-bar"></div>
                        <div class="eq-bar"></div>
                    </div>
                    <button class="fav-star-btn ${{isFav ? 'starred' : ''}}" onclick="alternarFavorito(${{c.id}}, event)">
                        ${{isFav ? '★' : '☆'}}
                    </button>
                `;
                fragment.appendChild(card);
            }});

            listBody.appendChild(fragment);
            canaisRenderizadosQtd += proximoLote.length;

            const boxAntigo = document.getElementById('loadMoreBox');
            if (boxAntigo) boxAntigo.remove();

            if (canaisRenderizadosQtd < canaisFiltradosCache.length) {{
                const loadBox = document.createElement('div');
                loadBox.id = 'loadMoreBox';
                loadBox.className = 'load-more-box';
                loadBox.innerHTML = `<button class="btn-load-more" onclick="renderizarMaisCanais()">Mostrar mais canais (${{canaisFiltradosCache.length - canaisRenderizadosQtd}} restantes)</button>`;
                listBody.appendChild(loadBox);
            }}
        }}

        // ROLAGEM INFINITA INTELIGENTE
        listBody.addEventListener('scroll', () => {{
            if (listBody.scrollTop + listBody.clientHeight >= listBody.scrollHeight - 100) {{
                renderizarMaisCanais();
            }}
        }});

        // EVENTOS DE REPRODUÇÃO
        playOverlay.addEventListener('click', () => {{
            playOverlay.classList.add('hidden');
            video.muted = false;
            video.play().then(() => {{
                unmutePill.style.display = 'none';
            }}).catch(() => {{
                video.muted = true;
                video.play();
            }});
        }});

        unmutePill.addEventListener('click', () => {{
            video.muted = false;
            unmutePill.style.display = 'none';
            mostrarHUD('🔊 Áudio ativado com sucesso!');
        }});

        // CLIQUE NO PRÓPRIO VÍDEO PARA PAUSAR / DESMUTAR
        video.addEventListener('click', (e) => {{
            e.stopPropagation();
            if (video.muted && unmutePill.style.display !== 'none') {{
                video.muted = false;
                unmutePill.style.display = 'none';
                mostrarHUD('🔊 Áudio ativado!');
                return;
            }}
            if (video.paused) {{
                video.play();
                mostrarHUD('▶ Reproduzindo');
            }} else {{
                video.pause();
                mostrarHUD('⏸ Pausado');
            }}
        }});

        // AÇÕES DO DOCK E CONTROLE DA GAVETA DE CANAIS
        function alternarGavetaCanais(ev, forcarAbrir = null) {{
            if (ev && ev.stopPropagation) ev.stopPropagation();
            const atualmenteMinimizado = document.body.classList.contains('channels-minimized');
            const novoMinimizado = forcarAbrir === true ? false : (forcarAbrir === false ? true : !atualmenteMinimizado);
            document.body.classList.toggle('channels-minimized', novoMinimizado);

            const btnDrawer = document.getElementById('btnToggleChannelsDrawer');
            const drawerArrow = document.getElementById('drawerToggleArrow');
            const drawerText = document.getElementById('drawerToggleText');
            if (btnDrawer) btnDrawer.classList.toggle('open', !novoMinimizado);
            if (drawerArrow) drawerArrow.textContent = novoMinimizado ? '▼' : '▲';
            if (drawerText) drawerText.textContent = novoMinimizado ? 'Todos os Canais' : 'Minimizar';
            mostrarHUD(novoMinimizado ? '🔽 Lista de canais minimizada' : '📋 Todos os canais exibidos');
        }}
        window.alternarGavetaCanais = alternarGavetaCanais;

        function alternarPainelFiltros(ev) {{
            if (ev && ev.stopPropagation) ev.stopPropagation();
            const box = document.getElementById('sidebarFiltersBox');
            const arrow = document.getElementById('filtersToggleArrow');
            if (!box) return;
            const aberto = box.classList.toggle('open');
            if (arrow) arrow.textContent = aberto ? '▲' : '▼';
        }}
        window.alternarPainelFiltros = alternarPainelFiltros;

        function ehCanalDisponivelAgora(c) {{
            if (!c) return false;
            if (!EH_AMBIENTE_LOCAL && !LOCAL_PROXY_ATIVO && window.location.protocol === 'https:') {{
                const urlResolvida = MAPA_FALLBACK_HTTPS_NUVEM[c.url] || c.url;
                if (urlResolvida.startsWith('http://')) return false;
            }}
            return true;
        }}

        function navegarCanal(direcao = 1) {{
            const listaBase = (canaisFiltradosCache && canaisFiltradosCache.length > 0) ? canaisFiltradosCache : TODOS_CANAIS;
            if (!listaBase || listaBase.length === 0) return;

            const canalAtualObj = TODOS_CANAIS[canalAtualIndex];
            let pos = listaBase.findIndex(item => item.id === (canalAtualObj && canalAtualObj.id));
            if (pos === -1) pos = direcao > 0 ? -1 : 0;

            for (let passo = 1; passo <= listaBase.length; passo++) {{
                const candidatoPos = (pos + direcao * passo + listaBase.length * 4) % listaBase.length;
                const candidato = listaBase[candidatoPos];
                if (ehCanalDisponivelAgora(candidato)) {{
                    const realIdx = TODOS_CANAIS.findIndex(x => x.id === candidato.id);
                    if (realIdx !== -1) {{
                        if (realIdx >= canaisRenderizadosQtd) {{
                            canaisRenderizadosQtd = Math.min(TODOS_CANAIS.length, realIdx + 20);
                            renderizarMaisCanais();
                        }}
                        sintonizar(realIdx);
                        return;
                    }}
                }}
            }}
            sintonizar(canalAtualIndex + direcao);
        }}
        window.navegarCanal = navegarCanal;

        const btnPrev = document.getElementById('btnZapPrev');
        if (btnPrev) btnPrev.addEventListener('click', (e) => {{ e.stopPropagation(); navegarCanal(-1); }});
        const btnNext = document.getElementById('btnZapNext');
        if (btnNext) btnNext.addEventListener('click', (e) => {{ e.stopPropagation(); navegarCanal(1); }});
        
        const btnPipEl = document.getElementById('btnPip');
        if (btnPipEl) {{
            btnPipEl.addEventListener('click', async () => {{
                try {{
                    if (document.pictureInPictureElement) {{
                        await document.exitPictureInPicture();
                    }} else if (document.pictureInPictureEnabled) {{
                        await video.requestPictureInPicture();
                    }}
                }} catch (err) {{
                    mostrarHUD('⚠️ PiP não suportado neste navegador');
                }}
            }});
        }}

        function atualizarBotoesFullscreen() {{
            const emFull = !!(document.fullscreenElement || document.webkitFullscreenElement || document.body.classList.contains('video-fullscreen-mode') || document.body.classList.contains('cinema-mode'));
            const txtFloat = document.getElementById('btnFloatingFullscreenText');
            if (txtFloat) txtFloat.textContent = emFull ? '📋 MOSTRAR CANAIS (ESC)' : 'EXPANDIR TELA TODA';
            const txtDock = document.getElementById('fullDockLabel');
            if (txtDock) txtDock.textContent = emFull ? 'Mostrar Canais' : 'Tela Toda';
        }}

        function alternarTelaCheia(ev) {{
            if (ev && ev.stopPropagation) ev.stopPropagation();
            const stage = document.getElementById('screenBox') || document.querySelector('.screen-container') || document.documentElement;
            const nativoAtivo = !!(document.fullscreenElement || document.webkitFullscreenElement);
            const cssAtivo = document.body.classList.contains('video-fullscreen-mode') || document.body.classList.contains('cinema-mode');
            const jaEmFull = nativoAtivo || cssAtivo;

            if (!jaEmFull) {{
                document.body.classList.add('video-fullscreen-mode');
                try {{
                    if (stage.requestFullscreen) {{
                        stage.requestFullscreen().catch(() => {{}});
                    }} else if (stage.webkitRequestFullscreen) {{
                        stage.webkitRequestFullscreen();
                    }}
                }} catch (e) {{}}
                atualizarBotoesFullscreen();
                mostrarHUD('📺 Só o canal na tela! (Aperte ESC ou mexa o mouse para sair)');
            }} else {{
                document.body.classList.remove('video-fullscreen-mode');
                document.body.classList.remove('cinema-mode');
                const btnC = document.getElementById('btnCinemaMode');
                if (btnC) btnC.classList.remove('active');
                try {{
                    if (document.fullscreenElement && document.exitFullscreen) {{
                        document.exitFullscreen().catch(() => {{}});
                    }} else if (document.webkitFullscreenElement && document.webkitExitFullscreen) {{
                        document.webkitExitFullscreen();
                    }}
                }} catch (e) {{}}
                atualizarBotoesFullscreen();
                mostrarHUD('📋 Lista de canais restaurada');
            }}
        }}
        window.alternarTelaCheia = alternarTelaCheia;

        video.addEventListener('dblclick', alternarTelaCheia);

        document.addEventListener('fullscreenchange', () => {{
            if (!document.fullscreenElement && !document.webkitFullscreenElement) {{
                document.body.classList.remove('video-fullscreen-mode');
            }}
            atualizarBotoesFullscreen();
        }});

        function abrirModalEpg(ev) {{
            if (ev && ev.stopPropagation) ev.stopPropagation();
            const modal = document.getElementById('epgModal');
            const list = document.getElementById('epgScheduleList');
            const chName = document.getElementById('epgModalChName');
            const chCat = document.getElementById('epgModalChCategory');
            const chLogo = document.getElementById('epgModalLogo');
            if (!modal || !list) return;
            const c = TODOS_CANAIS[canalAtualIndex] || TODOS_CANAIS[0];
            const epg = obterEpgDinamico(c);
            if (chName) chName.textContent = `#${{c.numero_str}} • ${{c.nome}}`;
            if (chCat) chCat.textContent = `${{c.categoria}} • ${{c.pais}} • Grade Automática 24h`;
            if (chLogo) {{
                const safeName = c.nome.replace(/'/g, "\\'");
                chLogo.innerHTML = c.logo ? `<img src="${{c.logo}}" alt="${{c.nome}}" onerror="this.outerHTML=obterBadgeSvgCliente('${{safeName}}')">` : obterBadgeSvgCliente(c.nome);
            }}
            list.innerHTML = `
                <div class="epg-item current">
                    <div class="epg-item-header">
                        <span class="epg-item-time">🕒 ${{epg.faixa}}</span>
                        <span class="epg-item-badge badge-live">🔴 NO AR AGORA • ${{epg.progresso}}%</span>
                    </div>
                    <div class="epg-item-title">${{epg.titulo}}</div>
                    <div class="epg-item-desc">Transmissão ao vivo em andamento • ${{c.categoria}}</div>
                </div>
                <div class="epg-item">
                    <div class="epg-item-header">
                        <span class="epg-item-time">🕒 ${{epg.proximaFaixa}}</span>
                        <span class="epg-item-badge badge-upcoming">⏭️ A SEGUIR</span>
                    </div>
                    <div class="epg-item-title">${{epg.proximoTitulo}}</div>
                    <div class="epg-item-desc">Próxima atração programada na sequência • ${{c.nome}}</div>
                </div>
                <div class="epg-item">
                    <div class="epg-item-header">
                        <span class="epg-item-time">🕒 ${{epg.depoisFaixa}}</span>
                        <span class="epg-item-badge badge-upcoming">📅 MAIS TARDE</span>
                    </div>
                    <div class="epg-item-title">${{epg.depoisTitulo}}</div>
                    <div class="epg-item-desc">Continuação da grade digital 24h • ${{c.pais}}</div>
                </div>
            `;
            modal.classList.add('open');
        }}
        window.abrirModalEpg = abrirModalEpg;

        const epgCard = document.getElementById('epgDockCard');
        if (epgCard) epgCard.addEventListener('click', abrirModalEpg);
        const btnCloseEpg = document.getElementById('epgModalDismiss');
        if (btnCloseEpg) btnCloseEpg.addEventListener('click', () => document.getElementById('epgModal').classList.remove('open'));
        const epgModalShade = document.getElementById('epgModal');
        if (epgModalShade) epgModalShade.addEventListener('click', (e) => {{
            if (e.target === epgModalShade) epgModalShade.classList.remove('open');
        }});

        // BOTÕES DE ENQUADRAMENTO / PROPORÇÃO
        const btnAspectDock = document.getElementById('btnAspectDock');
        if (btnAspectDock) btnAspectDock.addEventListener('click', alternarEnquadramento);

        const btnAspectHeader = document.getElementById('btnAspectHeader');
        if (btnAspectHeader) btnAspectHeader.addEventListener('click', alternarEnquadramento);

        // MODO CINEMA (TELA 100% LIMPA SÓ COM O CANAL)
        const btnCinema = document.getElementById('btnCinemaMode');
        btnCinema.addEventListener('click', () => {{
            const ativo = document.body.classList.toggle('cinema-mode');
            btnCinema.classList.toggle('active', ativo);
            atualizarBotoesFullscreen();
            mostrarHUD(ativo ? '🎬 Só o Canal na Tela! (ESC para voltar)' : '📋 Lista de Canais Restaurada');
        }});

        const btnFavFilter = document.getElementById('btnFavFilter');
        btnFavFilter.addEventListener('click', () => {{
            apenasFavoritos = !apenasFavoritos;
            btnFavFilter.classList.toggle('active', apenasFavoritos);
            aplicarFiltros(true);
            if (apenasFavoritos && document.body.classList.contains('channels-minimized')) {{
                alternarGavetaCanais(null, true);
            }}
            mostrarHUD(apenasFavoritos ? '⭐ Exibindo apenas favoritos' : '⚡ Exibindo todos os canais');
        }});

        // SELETOR DE PAÍSES
        document.querySelectorAll('.country-tab-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.country-tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                paisFiltro = btn.getAttribute('data-country');
                aplicarFiltros(true);
            }});
        }});

        // SELETOR DE CATEGORIAS (HISTÓRIA, COMBATE, COMÉDIA, SHOWS, VIP, ETC)
        document.querySelectorAll('.cat-pill').forEach(pill => {{
            pill.addEventListener('click', () => {{
                document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                catFiltro = pill.getAttribute('data-cat');
                aplicarFiltros(true);
            }});
        }});

        const mobileSearchInputEl = document.getElementById('mobileSearchInput');
        if (mobileSearchInputEl) {{
            mobileSearchInputEl.addEventListener('input', () => {{
                if (searchInput) searchInput.value = mobileSearchInputEl.value;
                aplicarFiltros(true);
            }});
        }}

        searchInput.addEventListener('input', () => {{
            if (mobileSearchInputEl) mobileSearchInputEl.value = searchInput.value;
            aplicarFiltros(true);
            if (searchInput.value.trim().length > 0 && document.body.classList.contains('channels-minimized')) {{
                alternarGavetaCanais(null, true);
            }}
        }});

        // CONTROLE REMOTO NUMÉRICO INTELIGENTE (0 a 9)
        let bufferNumeroCanal = '';
        let timerNumeroCanal = null;

        function processarNumeroCanal(digito) {{
            clearTimeout(timerNumeroCanal);
            bufferNumeroCanal += digito;
            if (bufferNumeroCanal.length > 4) bufferNumeroCanal = digito;

            const numDesejado = parseInt(bufferNumeroCanal, 10);
            mostrarHUD(`🔢 Canal #${{bufferNumeroCanal}}... (Pressione Enter ou aguarde)`);

            timerNumeroCanal = setTimeout(() => {{
                executarSintonizacaoPorNumero();
            }}, 1400);
        }}

        function executarSintonizacaoPorNumero() {{
            clearTimeout(timerNumeroCanal);
            if (!bufferNumeroCanal) return;

            const numDesejado = parseInt(bufferNumeroCanal, 10);
            bufferNumeroCanal = '';

            const idxEncontrado = TODOS_CANAIS.findIndex(c => c.numero === numDesejado);

            if (idxEncontrado !== -1) {{
                if (idxEncontrado >= canaisRenderizadosQtd) {{
                    canaisRenderizadosQtd = Math.min(TODOS_CANAIS.length, idxEncontrado + 20);
                    renderizarMaisCanais();
                }}
                sintonizar(idxEncontrado);
            }} else {{
                mostrarHUD(`⚠️ Canal #${{numDesejado}} não encontrado na grade`);
            }}
        }}

        // CONTROLE REMOTO PELO TECLADO
        window.addEventListener('keydown', (e) => {{
            if (e.target === searchInput) return;

            // Sintonização rápida por teclado numérico (0 a 9)
            if (/^[0-9]$/.test(e.key)) {{
                e.preventDefault();
                processarNumeroCanal(e.key);
                return;
            }}

            if (e.key === 'Enter') {{
                if (bufferNumeroCanal.length > 0) {{
                    e.preventDefault();
                    executarSintonizacaoPorNumero();
                    return;
                }}
            }}

            if (e.key === 'Escape') {{
                if (bufferNumeroCanal.length > 0) {{
                    bufferNumeroCanal = '';
                    clearTimeout(timerNumeroCanal);
                    mostrarHUD('✖ Digitação de canal cancelada');
                    return;
                }}
                if (document.body.classList.contains('video-fullscreen-mode') || document.body.classList.contains('cinema-mode')) {{
                    document.body.classList.remove('video-fullscreen-mode');
                    document.body.classList.remove('cinema-mode');
                    if (btnCinema) btnCinema.classList.remove('active');
                    atualizarBotoesFullscreen();
                    mostrarHUD('📋 Lista de canais restaurada');
                }}
                if (epgModalShade) epgModalShade.classList.remove('open');
                modalShade.classList.remove('open');
                return;
            }}

            switch (e.key) {{
                case ' ':
                    e.preventDefault();
                    if (video.paused) {{ video.play(); mostrarHUD('▶ Reproduzindo'); }}
                    else {{ video.pause(); mostrarHUD('⏸ Pausado'); }}
                    break;
                case 'a':
                case 'A':
                    e.preventDefault();
                    alternarEnquadramento();
                    break;
                case 'ArrowDown':
                case 'n':
                case 'N':
                    e.preventDefault();
                    navegarCanal(1);
                    break;
                case 'ArrowUp':
                case 'p':
                case 'P':
                    e.preventDefault();
                    navegarCanal(-1);
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    video.volume = Math.min(1, video.volume + 0.1);
                    mostrarHUD(`🔊 Volume: ${{Math.round(video.volume * 100)}}%`);
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    video.volume = Math.max(0, video.volume - 0.1);
                    mostrarHUD(`🔉 Volume: ${{Math.round(video.volume * 100)}}%`);
                    break;
                case 'm':
                case 'M':
                    video.muted = !video.muted;
                    mostrarHUD(video.muted ? '🔇 Áudio Mudo' : '🔊 Áudio Ativado');
                    break;
                case 'f':
                case 'F':
                    alternarTelaCheia();
                    break;
                case 'c':
                case 'C':
                    btnCinema.click();
                    break;
                case 'h':
                case 'H':
                    modalShade.classList.toggle('open');
                    break;
            }}
        }});

        // MODAL DE AJUDA
        const modalShade = document.getElementById('shortcutsModal');
        document.getElementById('btnKeyHelp').addEventListener('click', () => modalShade.classList.add('open'));
        document.getElementById('modalDismiss').addEventListener('click', () => modalShade.classList.remove('open'));
        modalShade.addEventListener('click', (e) => {{
            if (e.target === modalShade) modalShade.classList.remove('open');
        }});

        // MODAL DO CONTROLE REMOTO POR CELULAR COM QR CODE
        const remoteModal = document.getElementById('remoteModal');
        const btnQrRemote = document.getElementById('btnQrRemote');
        let qrCodeInstancia = null;

        btnQrRemote.addEventListener('click', async () => {{
            remoteModal.classList.add('open');
            if (!qrCodeInstancia) {{
                const renderizarQr = (url) => {{
                    document.getElementById('remoteUrlDisplay').textContent = url;
                    const container = document.getElementById('qrcodeContainer');
                    container.innerHTML = '';
                    qrCodeInstancia = new QRCode(container, {{
                        text: url,
                        width: 190,
                        height: 190,
                        colorDark: "#060913",
                        colorLight: "#ffffff",
                        correctLevel: QRCode.CorrectLevel.M
                    }});
                }};
                try {{
                    if (!EH_AMBIENTE_LOCAL && !LOCAL_PROXY_ATIVO) {{
                        throw new Error('Modo nuvem');
                    }}
                    const apiBase = EH_AMBIENTE_LOCAL ? '' : 'http://localhost:8080';
                    const resp = await fetch(apiBase + '/api/ip_local');
                    const data = await resp.json();
                    renderizarQr(data.url_controle);
                }} catch (err) {{
                    const fallbackUrl = EH_AMBIENTE_LOCAL
                        ? `http://${{window.location.hostname || '192.168.100.210'}}:8080/controle.html`
                        : window.location.origin;
                    renderizarQr(fallbackUrl);
                }}
            }}
        }});

        document.getElementById('remoteModalDismiss').addEventListener('click', () => remoteModal.classList.remove('open'));
        remoteModal.addEventListener('click', (e) => {{
            if (e.target === remoteModal) remoteModal.classList.remove('open');
        }});

        document.getElementById('btnCopiarLinkRemote').addEventListener('click', () => {{
            const url = document.getElementById('remoteUrlDisplay').textContent.trim();
            navigator.clipboard.writeText(url).then(() => {{
                mostrarHUD('📋 Link do controle copiado para o celular!');
            }}).catch(() => {{
                mostrarHUD('📋 Link: ' + url);
            }});
        }});

        // ESCUTADOR EM TEMPO REAL DE COMANDOS DO CELULAR (SOMENTE EM AMBIENTE LOCAL)
        async function ouvirComandosRemotos() {{
            if (!EH_AMBIENTE_LOCAL) return;
            try {{
                const resp = await fetch('/api/ouvir_comandos');
                if (resp.ok) {{
                    const cmds = await resp.json();
                    for (const item of cmds) {{
                        executarComandoRemoto(item.cmd, item.val);
                    }}
                }}
            }} catch (err) {{}}
        }}
        if (EH_AMBIENTE_LOCAL) {{
            setInterval(ouvirComandosRemotos, 350);
        }}

        function executarComandoRemoto(cmd, val) {{
            switch (cmd) {{
                case 'proximo':
                    navegarCanal(1);
                    break;
                case 'anterior':
                    navegarCanal(-1);
                    break;
                case 'playpause':
                    if (video.paused) {{ video.play(); mostrarHUD('▶ Reproduzindo (via Celular)'); }}
                    else {{ video.pause(); mostrarHUD('⏸ Pausado (via Celular)'); }}
                    break;
                case 'volume_up':
                    video.volume = Math.min(1, video.volume + 0.1);
                    mostrarHUD(`🔊 Volume: ${{Math.round(video.volume * 100)}}% (via Celular)`);
                    break;
                case 'volume_down':
                    video.volume = Math.max(0, video.volume - 0.1);
                    mostrarHUD(`🔉 Volume: ${{Math.round(video.volume * 100)}}% (via Celular)`);
                    break;
                case 'mute':
                    video.muted = !video.muted;
                    mostrarHUD(video.muted ? '🔇 Mudo (via Celular)' : '🔊 Áudio Ativado (via Celular)');
                    break;
                case 'aspect':
                    alternarEnquadramento();
                    break;
                case 'cinema':
                    btnCinema.click();
                    break;
                case 'fullscreen':
                    alternarTelaCheia();
                    break;
                case 'sintonizar':
                    const numDesejado = parseInt(val, 10);
                    const idx = TODOS_CANAIS.findIndex(c => c.numero === numDesejado);
                    if (idx !== -1) {{
                        if (idx >= canaisRenderizadosQtd) {{
                            canaisRenderizadosQtd = Math.min(TODOS_CANAIS.length, idx + 20);
                            renderizarMaisCanais();
                        }}
                        sintonizar(idx);
                        mostrarHUD(`📱 Celular sintonizou CH #${{numDesejado}}`);
                    }} else {{
                        mostrarHUD(`⚠️ Canal #${{numDesejado}} não encontrado`);
                    }}
                    break;
                case 'categoria':
                    const pill = document.querySelector(`.cat-pill[data-cat="${{val}}"]`);
                    if (pill) pill.click();
                    break;
                case 'recarregar':
                    window.location.reload();
                    break;
            }}
        }}

        // AUTO-OCULTAÇÃO DO BOTÃO FLUTUANTE E CURSOR APÓS 2s PARADO (TELA 100% LIMPA)
        let mouseIdleTimer = null;
        function resetarInatividadeMouse() {{
            document.body.classList.remove('mouse-idle');
            clearTimeout(mouseIdleTimer);
            mouseIdleTimer = setTimeout(() => {{
                document.body.classList.add('mouse-idle');
            }}, 2000);
        }}
        window.addEventListener('mousemove', resetarInatividadeMouse);
        window.addEventListener('touchstart', resetarInatividadeMouse);
        resetarInatividadeMouse();

        // INICIALIZAÇÃO AUTOMÁTICA
        aplicarEnquadramento(enquadramentoIndex, false);
        aplicarFiltros(true);
        const primeiroCanalValidoIdx = TODOS_CANAIS.findIndex(c => ehCanalDisponivelAgora(c));
        sintonizar(primeiroCanalValidoIdx >= 0 ? primeiroCanalValidoIdx : 0);
    </script>
</body>
</html>
"""

html_saida_path = SAIDA_DIR / "index.html"
html_desktop_path = DESKTOP_DIR / "ASSISTIR_TV.html"

html_saida_path.write_text(html_code, encoding="utf-8")
shutil.copyfile(html_saida_path, html_desktop_path)

print("ATUALIZAÇÃO COM PADRÃO 16:9 FIXO, ENQUADRAMENTO E ZERO TRAVAMENTO FINALIZADA COM SUCESSO!")
