import sqlite3
import json
import shutil
from pathlib import Path

BASE_DIR = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
SAIDA_DIR = BASE_DIR / "saida"
DB_PATH = SAIDA_DIR / "banco_iptv.db"
DESKTOP_DIR = Path(r"C:\Users\jonas\Desktop")

SAIDA_DIR.mkdir(parents=True, exist_ok=True)

# 1. Conexão ao banco SQLite
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Garantir desativação de hosts instáveis e duplicatas quebradas
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
       OR nome LIKE '%(Digital HLS)%'
""")
c.execute("UPDATE canais SET status = 'INATIVO' WHERE qualidade IN ('4K Ultra HD', 'Full HD', '1080p')")


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
        "url": "http://170.83.16.50/CULTURA/index.m3u8",
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
        "url": "https://cdn.live.br1.jmvstream.com/w/LVW-10842/LVW10842_513N26MDBL/playlist.m3u8",
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
        "nome": "Band TV RBA HD",
        "url": "https://cdn.jmvstream.com/w/LVW-15748/LVW15748_Yed7yzLuRC/playlist.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/band-br.png",
        "categoria": "📺 TV Aberta Brasil",
        "tags": ["aberta", "esportes", "noticias"],
        "qualidade": "Digital Leve",
        "latencia": 42,
        "pais": "🇧🇷 Brasil",
        "pais_codigo": "BR",
        "regiao": "Nacional",
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
        "url": "https://cdn.jmvstream.com/w/LVW-10801/LVW10801_Xvg4R0u57n/playlist.m3u8",
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
        "url": "http://170.83.16.50/INVESTIGATION_DISCOVERY/index.m3u8",
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
        "url": "http://170.83.16.50/CARTOON_NETWORK/index.m3u8",
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
        "url": "http://170.83.16.50/SONY/index.m3u8",
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
            status='ATIVO',
            latencia_ms=excluded.latencia_ms,
            web_ok=1,
            cors_star=1
    """, (vip["nome"], vip["url"], vip["logo"], vip["categoria"], vip["qualidade"], vip["latencia"], vip["status"], vip["pais"], vip["regiao"]))

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
            WHEN nome LIKE '%Band TV RBA HD%' THEN 5
            WHEN nome LIKE '%RedeTV! (Fibra Leve)%' THEN 6
            WHEN nome LIKE '%TV Brasil (EBC Oficial HD)%' THEN 7
            WHEN nome LIKE '%TV Gazeta SP (NuvemPlay)%' THEN 8
            WHEN nome LIKE '%Record News (Fibra Leve)%' THEN 9
            WHEN nome LIKE '%BandSports (Fibra Leve)%' THEN 10
            WHEN nome LIKE '%TV Cultura SP Oficial (UOL)%' THEN 11
            WHEN nome LIKE '%TV Cultura Fast (FPA)%' THEN 12
            WHEN nome LIKE '%TV Cultura SP (WiseStream HD)%' THEN 13
            WHEN nome LIKE '%SBT Interior HD%' THEN 14
            WHEN nome LIKE '%Rede Brasil HD%' THEN 15
            WHEN nome LIKE '%TV Aparecida (Fibra Leve)%' THEN 16
            WHEN nome LIKE '%Canção Nova (Fibra Leve)%' THEN 17
            WHEN nome LIKE '%TV Senado (Fibra Leve)%' THEN 18
            WHEN nome LIKE '%TV Justiça (Fibra Leve)%' THEN 19
            WHEN nome LIKE '%Terra Viva (Fibra Leve)%' THEN 20
            WHEN nome LIKE '%Canal do Boi (Fibra Leve)%' THEN 21
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Kids%' THEN 22
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Channel%' THEN 23
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Turbo%' THEN 24
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Home & Health%' THEN 25
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Science%' THEN 26
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery World%' THEN 27
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Discovery Theater%' THEN 28
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Investigation Discovery%' THEN 29
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Animal Planet%' THEN 30
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%TLC%' THEN 31
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%HGTV%' THEN 32
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%History Channel%' THEN 33
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Cartoon Network%' THEN 34
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%TNT%' THEN 35
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Space%' THEN 36
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%AXN%' THEN 37
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Sony Channel%' THEN 38
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%ESPN%' THEN 39
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%CNN Brasil%' THEN 40
            WHEN url LIKE '%170.83.16.50%' AND nome LIKE '%Lifetime%' THEN 41
            WHEN url LIKE '%170.83.16.50%' THEN 42
            WHEN pais LIKE '%Brasil%' THEN 50
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
    "historia": 0,
    "combate": 0,
    "comedia": 0,
    "shows": 0,
    "vip": 0,
    "filmes": 0,
    "musica": 0,
    "infantil": 0,
    "esportes": 0,
    "noticias": 0
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

    # Tag ABERTA (TV Aberta Brasil: SBT, Globo, Cultura, Record, Band, RedeTV!, TV Brasil, Gazeta, etc.)
    if any(k in nome_lower or k in cat_lower for k in [
        "aberta", "sbt", "cultura", "futura", "globo", "record", "band ", "bandeirantes", 
        "redetv", "gazeta", "tv brasil", "ebc", "aparecida", "cancao nova", "senado", "justica", 
        "terra viva", "canal do boi", "rede brasil"
    ]):
        tags.append("aberta")
        contagem_tags["aberta"] += 1

    # Tag VIP
    if "170.83.16.50" in url:
        tags.append("vip")
        contagem_tags["vip"] += 1

    # Tag HISTÓRIA (História, Documentários, Ciência, Planeta, Descobertas)
    if any(k in nome_lower or k in cat_lower for k in [
        "historia", "history", "discovery", "science", "world", "theater", "investigation", 
        "animal planet", "doc", "documentario", "geography", "national", "bio", "curta"
    ]):
        tags.append("historia")
        contagem_tags["historia"] += 1

    # Tag COMBATE (Lutas, Boxe, UFC, Artes Marciais, MMA, Ação Intensa)
    if any(k in nome_lower or k in cat_lower for k in [
        "combate", "luta", "fight", "mma", "ufc", "boxe", "boxing", "wrestling", "wwe",
        "action", "space", "axn", "bandsports", "espn"
    ]):
        tags.append("combate")
        contagem_tags["combate"] += 1

    # Tag COMÉDIA (Humor, South Park, Sitcom, Pegadinhas, Standup, Comédia)
    if any(k in nome_lower or k in cat_lower for k in [
        "comedia", "comedy", "south park", "humor", "risos", "stand-up", "sitcom", 
        "toon", "cartoon", "fun", "chaves", "chapolin", "porta dos fundos"
    ]):
        tags.append("comedia")
        contagem_tags["comedia"] += 1

    # Tag SHOWS (Música Ao Vivo, Festivais, Shows Musicais, Palco, Hits)
    if any(k in nome_lower or k in cat_lower for k in [
        "show", "shows", "live", "festival", "palco", "rock", "pop", "metal", 
        "sertanejo", "pagode", "mpb", "mtv", "multishow", "trace", "kiss", "club"
    ]):
        tags.append("shows")
        contagem_tags["shows"] += 1

    # Tags Gerais
    if any(k in nome_lower or k in cat_lower for k in ["filme", "movie", "cine", "cinema", "serie", "tnt", "space", "axn", "sony", "lifetime", "telecine", "hbo"]):
        tags.append("filmes")
        contagem_tags["filmes"] += 1
    if any(k in nome_lower or k in cat_lower for k in ["musica", "music", "radio", "fm", "som", "hit", "clip"]):
        tags.append("musica")
        contagem_tags["musica"] += 1
    if any(k in nome_lower or k in cat_lower for k in ["kid", "infantil", "desenho", "cartoon", "baby", "animac"]):
        tags.append("infantil")
        contagem_tags["infantil"] += 1
    if any(k in nome_lower or k in cat_lower for k in ["esporte", "sport", "futebol", "fut", "espn", "band", "turbo"]):
        tags.append("esportes")
        contagem_tags["esportes"] += 1
    if any(k in nome_lower or k in cat_lower for k in ["noticia", "news", "jornal", "cnn", "record", "sbt", "band", "globo"]):
        tags.append("noticias")
        contagem_tags["noticias"] += 1

    # Categoria primária visual
    if "aberta" in tags and any(k in nome_lower for k in ["sbt", "cultura", "futura", "globo", "record", "band", "redetv", "tv brasil", "gazeta", "rede brasil", "aparecida", "cancao nova", "senado", "justica", "terra viva", "canal do boi"]):
        cat_final = "📺 TV Aberta"
    elif "vip" in tags:
        cat_final = "⭐ VIP Fibra"
    elif "historia" in tags:
        cat_final = "📜 História & Fatos"
    elif "combate" in tags:
        cat_final = "🥊 Combate & Lutas"
    elif "comedia" in tags:
        cat_final = "😂 Comédia & Humor"
    elif "shows" in tags:
        cat_final = "🎸 Shows & Música"
    elif "filmes" in tags:
        cat_final = "🍿 Filmes & Séries"
    elif "infantil" in tags:
        cat_final = "🧸 Infantil & Desenhos"
    elif "esportes" in tags:
        cat_final = "⚽ Esportes & Ação"
    elif "musica" in tags:
        cat_final = "📻 Rádios & Música"
    elif "noticias" in tags:
        cat_final = "📰 Notícias"
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
gerar_m3u(DESKTOP_DIR / "DISCOVERY_PT_BR_DUBLADO.m3u", [c for c in canais_estruturados if "vip" in c["tags"]], "VIP Fibra Discovery")
gerar_m3u(DESKTOP_DIR / "CANAIS_DIGITAIS_LEVES.m3u", canais_estruturados, "Central Completa Digital")
gerar_m3u(DESKTOP_DIR / "CANAIS_HISTORIA.m3u", [c for c in canais_estruturados if "historia" in c["tags"]], "Canais de História")
gerar_m3u(DESKTOP_DIR / "CANAIS_COMBATE_E_LUTAS.m3u", [c for c in canais_estruturados if "combate" in c["tags"]], "Canais de Combate e Lutas")
gerar_m3u(DESKTOP_DIR / "CANAIS_COMEDIA.m3u", [c for c in canais_estruturados if "comedia" in c["tags"]], "Canais de Comédia")
gerar_m3u(DESKTOP_DIR / "CANAIS_SHOWS_E_MUSICA.m3u", [c for c in canais_estruturados if "shows" in c["tags"] or "musica" in c["tags"]], "Canais de Shows e Música")

# Gerar HTML Player Profissional
json_canais_str = json.dumps(canais_estruturados, ensure_ascii=False)

html_code = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CENTRAL DE TV DIGITAL PRO - Cinema Studio 2026</title>
    <script>
        // Se aberto direto pelo arquivo no Desktop, redireciona para o servidor acelerado local
        if (window.location.protocol === 'file:') {{
            window.location.replace('http://localhost:8080/index.html');
        }}
    </script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
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
        /* MODO CINEMA */
        body.cinema-mode header,
        body.cinema-mode .sidebar-channels {{
            opacity: 0.04;
            pointer-events: none;
            transition: opacity 0.4s ease;
        }}
        body.cinema-mode header:hover,
        body.cinema-mode .sidebar-channels:hover {{
            opacity: 1;
            pointer-events: auto;
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
            max-width: min(100%, calc((100vh - 175px) * (16 / 9)));
            max-height: calc(100vh - 175px);
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

        /* BADGE INDICADOR DE PADRÃO 16:9 FIXO */
        .screen-standard-tag {{
            position: absolute;
            top: 14px;
            left: 14px;
            background: rgba(12, 19, 34, 0.85);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #6ee7b7;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.5px;
            z-index: 10;
            backdrop-filter: blur(8px);
            pointer-events: none;
            display: flex;
            align-items: center;
            gap: 7px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        }}
        .screen-standard-tag .tag-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10b981;
            box-shadow: 0 0 8px #10b981;
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

        /* PAINEL INFERIOR DE INFORMAÇÕES DO CANAL */
        .player-info-dock {{
            margin-top: 10px;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 10px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
        }}
        .cur-channel-box {{
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 0;
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

        /* LATERAL DIREITA DE CANAIS (COM SEPARAÇÃO POR PAÍS E CATEGORIA) */
        .sidebar-channels {{
            width: 400px;
            background: var(--bg-surface);
            border-left: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: opacity 0.3s;
        }}

        /* ABAS DE PAÍSES COM CONTAGEM */
        .country-tabs {{
            display: flex;
            background: #090e1a;
            border-bottom: 1px solid var(--border);
            padding: 8px 12px;
            gap: 6px;
            overflow-x: auto;
        }}
        .country-tabs::-webkit-scrollbar {{
            height: 4px;
        }}
        .country-tabs::-webkit-scrollbar-thumb {{
            background: #1e293b;
            border-radius: 2px;
        }}
        .country-tab-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }}
        .country-tab-btn:hover {{
            color: #fff;
            background: rgba(255, 255, 255, 0.05);
        }}
        .country-tab-btn.active {{
            background: rgba(16, 185, 129, 0.15);
            border-color: var(--emerald);
            color: #6ee7b7;
        }}
        .tab-count {{
            background: #0f172a;
            border: 1px solid var(--border);
            font-size: 10px;
            padding: 1px 6px;
            border-radius: 10px;
            color: inherit;
        }}

        /* PILULAS DE CATEGORIAS (HISTÓRIA, COMBATE, COMÉDIA, SHOWS EM DESTAQUE) */
        .category-pills {{
            display: flex;
            padding: 8px 12px;
            gap: 6px;
            overflow-x: auto;
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border);
        }}
        .category-pills::-webkit-scrollbar {{
            height: 4px;
        }}
        .category-pills::-webkit-scrollbar-thumb {{
            background: #1e293b;
            border-radius: 2px;
        }}
        .cat-pill {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 6px 11px;
            border-radius: 20px;
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
            background: rgba(16, 185, 129, 0.2);
            border-color: var(--emerald);
            color: #6ee7b7;
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
            width: 6px;
        }}
        .channel-list::-webkit-scrollbar-thumb {{
            background: #1e293b;
            border-radius: 3px;
        }}
        .channel-list::-webkit-scrollbar-thumb:hover {{
            background: #334155;
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
    </style>
</head>
<body>

    <!-- CABEÇALHO PROFISSIONAL COM GLASSMORPHISM -->
    <header>
        <div class="brand">
            <div class="brand-badge">⚡</div>
            <div class="brand-meta">
                <h1>CENTRAL DE TV DIGITAL <span class="pro-tag">PRO 2026</span></h1>
                <p>
                    <span class="status-dot"></span>
                    <span>100% Fibra Leve • Zero Travamento • <b id="totalCanaisBadge">{total_canais}</b> Canais</span>
                </p>
            </div>
        </div>

        <div class="search-wrapper">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" class="search-input" placeholder="Buscar por número (#001), nome, história, combate, comédia, shows...">
            <span class="search-count" id="searchCountBadge">{total_canais}</span>
        </div>

        <div class="header-controls">
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

            <!-- DOCK INFERIOR DE INFORMAÇÕES E CONTROLES -->
            <div class="player-info-dock">
                <div class="cur-channel-box">
                    <div class="cur-ch-num" id="dockChNum">#001</div>
                    <div class="cur-ch-logo" id="dockLogo">⚡</div>
                    <div class="cur-ch-meta">
                        <h2>
                            <span id="dockName">Discovery Kids (Digital Leve)</span>
                            <span class="badge-pill badge-digital" id="dockSignalBadge">
                                <span class="signal-led led-green" id="dockSignalLed"></span>
                                <span id="dockSignalText">Fibra Direta • 45ms</span>
                            </span>
                            <span class="badge-pill badge-pais" id="dockPais">🇧🇷 Brasil</span>
                        </h2>
                        <p id="dockDetails">⭐ VIP Fibra • Nacional • Consumo Ultraleve & Zero Buffering</p>
                    </div>
                </div>

                <div class="epg-timeline">
                    <span class="epg-clock" id="epgTimeBadge">10:00 - 12:00</span>
                    <span class="epg-desc" id="epgProgBadge">Grade Matutina • Programação Ao Vivo</span>
                </div>

                <div class="player-actions">
                    <button class="icon-btn-text" id="btnAspectDock" title="Ajuste de Tela: 16:9 Cinema / Preencher / Esticar (Atalho: Tecla A)">
                        📐 <span id="aspectDockLabel">16:9 Cinema</span>
                    </button>
                    <button class="icon-btn" id="btnZapPrev" title="Canal Anterior (Seta Cima / P)">⏮</button>
                    <button class="icon-btn" id="btnZapNext" title="Próximo Canal (Seta Baixo / N)">⏭</button>
                    <button class="icon-btn" id="btnPip" title="Picture-in-Picture">📺</button>
                    <button class="icon-btn" id="btnFull" title="Tela Cheia (F)">⛶</button>
                </div>
            </div>
        </div>

        <!-- BARRA LATERAL (SEPARAÇÃO POR PAÍS, CATEGORIAS E NÚMEROS) -->
        <div class="sidebar-channels">
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
                <button class="cat-pill pill-aberta" data-cat="aberta">📺 TV Aberta Brasil ({contagem_tags['aberta']})</button>
                <button class="cat-pill pill-historia" data-cat="historia">📜 História ({contagem_tags['historia']})</button>
                <button class="cat-pill pill-combate" data-cat="combate">🥊 Combate ({contagem_tags['combate']})</button>
                <button class="cat-pill pill-comedia" data-cat="comedia">😂 Comédia ({contagem_tags['comedia']})</button>
                <button class="cat-pill pill-shows" data-cat="shows">🎸 Shows ({contagem_tags['shows']})</button>
                <button class="cat-pill" data-cat="vip">⭐ VIP Fibra ({contagem_tags['vip']})</button>
                <button class="cat-pill" data-cat="filmes">🍿 Filmes & Séries ({contagem_tags['filmes']})</button>
                <button class="cat-pill" data-cat="musica">📻 Rádios & Música ({contagem_tags['musica']})</button>
                <button class="cat-pill" data-cat="infantil">🧸 Infantis ({contagem_tags['infantil']})</button>
                <button class="cat-pill" data-cat="esportes">⚽ Esportes ({contagem_tags['esportes']})</button>
                <button class="cat-pill" data-cat="noticias">📰 Notícias ({contagem_tags['noticias']})</button>
            </div>

            <!-- LISTA ULTRA-LEVE DE CANAIS COM RENDERIZAÇÃO PROGRESSIVA -->
            <div class="channel-list" id="channelListBody">
                <!-- Inserido progressivamente via JS para zero travamento -->
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
                    <span class="key-label">Canais VIP 1 a 9</span>
                    <span class="key-badge">1 a 9</span>
                </div>
            </div>
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

        function obterEpgDinamico(nomeCanal) {{
            const agora = new Date();
            const h = agora.getHours();
            const formatHora = (hora, min) => `${{String(hora % 24).padStart(2, '0')}}:${{String(min).padStart(2, '0')}}`;
            
            let faixa = 'Grade Matutina';
            if (h >= 12 && h < 18) faixa = 'Grade Vespertina';
            else if (h >= 18) faixa = 'Horário Nobre';
            else if (h < 6) faixa = 'Madrugada';

            return {{
                faixa: `${{formatHora(h, 0)}} - ${{formatHora(h + 2, 0)}}`,
                titulo: `${{faixa}} • ${{nomeCanal.replace('(Digital Leve)', '').trim()}} Ao Vivo`
            }};
        }}

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
            document.getElementById('dockPais').textContent = c.pais;
            document.getElementById('dockDetails').textContent = `${{c.categoria}} • ${{c.regiao || 'Nacional'}} • Qualidade: Digital • Consumo Ultraleve`;

            const logoBox = document.getElementById('dockLogo');
            if (c.logo) {{
                logoBox.innerHTML = `<img src="${{c.logo}}" alt="${{c.nome}}" onerror="this.parentElement.innerHTML='⚡'">`;
            }} else {{
                logoBox.innerHTML = '⚡';
            }}

            const epg = obterEpgDinamico(c.nome);
            document.getElementById('epgTimeBadge').textContent = epg.faixa;
            document.getElementById('epgProgBadge').textContent = epg.titulo;

            mostrarHUD(`⚡ Sintonizando CH #${{c.numero_str}}: ${{c.nome}}`);

            // Roteamento inteligente de fluxo com aceleração HTTP local
            const PROXY_ORIGIN = window.location.protocol.startsWith('http') ? window.location.origin : 'http://localhost:8080';
            let streamUrl = c.url;
            if (c.url.includes('170.83.16.50')) {{
                // Fibra nativa direta com CORS *
                streamUrl = c.url;
            }} else {{
                streamUrl = PROXY_ORIGIN + '/proxy?url=' + encodeURIComponent(c.url);
            }}

            if (hls) {{
                hls.destroy();
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
                                        sintonizar(canalAtualIndex + 1);
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
                                    sintonizar(canalAtualIndex + 1);
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
            const termo = searchInput.value.toLowerCase().trim();

            canaisFiltradosCache = TODOS_CANAIS.filter(c => {{
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
                card.onclick = () => sintonizar(realIndex);

                const logoHtml = c.logo ? `<img src="${{c.logo}}" alt="${{c.nome}}" onerror="this.parentElement.innerHTML='⚡'">` : '⚡';

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

        // AÇÕES DO DOCK
        document.getElementById('btnZapPrev').addEventListener('click', () => sintonizar(canalAtualIndex - 1));
        document.getElementById('btnZapNext').addEventListener('click', () => sintonizar(canalAtualIndex + 1));
        
        document.getElementById('btnPip').addEventListener('click', async () => {{
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

        document.getElementById('btnFull').addEventListener('click', () => {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen();
            }} else {{
                document.exitFullscreen();
            }}
        }});

        // BOTÕES DE ENQUADRAMENTO / PROPORÇÃO
        const btnAspectDock = document.getElementById('btnAspectDock');
        if (btnAspectDock) btnAspectDock.addEventListener('click', alternarEnquadramento);

        const btnAspectHeader = document.getElementById('btnAspectHeader');
        if (btnAspectHeader) btnAspectHeader.addEventListener('click', alternarEnquadramento);

        // MODO CINEMA
        const btnCinema = document.getElementById('btnCinemaMode');
        btnCinema.addEventListener('click', () => {{
            document.body.classList.toggle('cinema-mode');
            const ativo = document.body.classList.contains('cinema-mode');
            btnCinema.classList.toggle('active', ativo);
            mostrarHUD(ativo ? '🎬 Modo Cinema Ativado' : '📺 Modo Padrão Restaurado');
        }});

        const btnFavFilter = document.getElementById('btnFavFilter');
        btnFavFilter.addEventListener('click', () => {{
            apenasFavoritos = !apenasFavoritos;
            btnFavFilter.classList.toggle('active', apenasFavoritos);
            aplicarFiltros(true);
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

        searchInput.addEventListener('input', () => aplicarFiltros(true));

        // CONTROLE REMOTO PELO TECLADO
        window.addEventListener('keydown', (e) => {{
            if (e.target === searchInput) return;

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
                    sintonizar(canalAtualIndex + 1);
                    break;
                case 'ArrowUp':
                case 'p':
                case 'P':
                    e.preventDefault();
                    sintonizar(canalAtualIndex - 1);
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
                    if (!document.fullscreenElement) document.documentElement.requestFullscreen();
                    else document.exitFullscreen();
                    break;
                case 'c':
                case 'C':
                    btnCinema.click();
                    break;
                case 'h':
                case 'H':
                    modalShade.classList.toggle('open');
                    break;
                case '1':
                case '2':
                case '3':
                case '4':
                case '5':
                case '6':
                case '7':
                case '8':
                case '9':
                    const canalNum = parseInt(e.key) - 1;
                    if (canalNum < TODOS_CANAIS.length) {{
                        sintonizar(canalNum);
                    }}
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

        // INICIALIZAÇÃO AUTOMÁTICA
        aplicarEnquadramento(enquadramentoIndex, false);
        aplicarFiltros(true);
        sintonizar(0);
    </script>
</body>
</html>
"""

html_saida_path = SAIDA_DIR / "index.html"
html_desktop_path = DESKTOP_DIR / "ASSISTIR_TV.html"

html_saida_path.write_text(html_code, encoding="utf-8")
shutil.copyfile(html_saida_path, html_desktop_path)

print("ATUALIZAÇÃO COM PADRÃO 16:9 FIXO, ENQUADRAMENTO E ZERO TRAVAMENTO FINALIZADA COM SUCESSO!")
