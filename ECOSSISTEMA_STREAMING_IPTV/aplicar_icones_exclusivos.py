import sqlite3
import urllib.parse
import hashlib
import re

# Banco de dados
DB_PATH = r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. Dicionário de Logos Oficiais em Alta Resolução (GitHub tv-logos, Wikimedia, etc.)
LOGOS_OFICIAIS = [
    # TV Aberta Brasil
    (r"\bsbt\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/sbt-br.png"),
    (r"\bcultura\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-cultura-br.png"),
    (r"\bglobo\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-globo-br.png"),
    (r"\brecord news\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/record-news-br.png"),
    (r"\brecord\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/record-tv-br.png"),
    (r"\bbandnews\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/bandnews-tv-br.png"),
    (r"\bbandsports\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/bandsports-br.png"),
    (r"\bband\b|\bbandeirantes\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/rede-bandeirantes-br.png"),
    (r"\bredetv\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/redetv-br.png"),
    (r"\btv brasil\b|\bebc\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-brasil-br.png"),
    (r"\bgazeta\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-gazeta-sao-paulo-br.png"),
    (r"\baparecida\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-aparecida-br.png"),
    (r"\bcancao nova\b|\bcanção nova\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/cancao-nova-tv-br.png"),
    (r"\bsenado\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-senado-br.png"),
    (r"\bcamara\b|\bcâmara\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-camara-br.png"),
    (r"\bjustica\b|\bjustiça\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-justica-br.png"),
    (r"\brede brasil\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/rede-brasil-de-televisao-br.png"),
    (r"\bfutura\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/canal-futura-br.png"),
    (r"\bcnt\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/rede-cnt-br.png"),
    (r"\brural\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/canal-rural-br.png"),
    (r"\bterra viva\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/terra-viva-br.png"),
    (r"\bcanal do boi\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/canal-do-boi-br.png"),
    (r"\bagrocanal\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/agrocanal-br.png"),
    (r"\btve rs\b|\btve\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tve-rs-br.png"),
    (r"\bsesc\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/sesctv-br.png"),
    (r"\bcatve\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/catve-br.png"),
    (r"\bpai eterno\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-pai-eterno-br.png"),
    (r"\bevangelizar\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-evangelizar-br.png"),
    (r"\brede vida\b|\bredevida\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/redevida-br.png"),
    (r"\bboa vontade\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/boa-vontade-tv-br.png"),
    (r"\brito tv\b|\brito\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/rito-tv-br.png"),
    (r"\bideal tv\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/ideal-tv-br.png"),

    # Infantis
    (r"\bcartoon network\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/cartoon-network-br.png"),
    (r"\bcartoonito\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/cartoonito-br.png"),
    (r"\bdiscovery kids\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-kids-br.png"),
    (r"\bnickelodeon\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/nickelodeon-br.png"),
    (r"\bnick jr\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/nick-jr-br.png"),
    (r"\bdisney channel\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/disney-channel-br.png"),
    (r"\bdisney junior\b|\bdisney jr\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/disney-junior-br.png"),
    (r"\bgloobinho\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/gloobinho-br.png"),
    (r"\bgloob\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/gloob-br.png"),
    (r"\bra tim bum\b|\brá tim bum\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-ra-tim-bum-br.png"),
    (r"\bturma da monica\b|\bturma da mônica\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/turma-da-monica-br.png"),
    (r"\btooncast\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tooncast-br.png"),
    (r"\bboomerang\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/boomerang-br.png"),
    (r"\bbaby tv\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/baby-tv-br.png"),
    (r"\btooncami\b|\btoonami\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/toonami-br.png"),

    # Séries, Humor & Maratonas
    (r"\bsouth park\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/south-park-br.png"),
    (r"\bporta dos fundos\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/porta-dos-fundos-br.png"),
    (r"\bcomedy central\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/comedy-central-br.png"),
    (r"\bchaves\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/chaves-br.png"),
    (r"\bchapolin\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/chapolin-br.png"),
    (r"\bjornada nas estrelas\b|\bstar trek\b|\bvoyager\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/star-trek-br.png"),
    (r"\bdoctor who\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/doctor-who-br.png"),
    (r"\bncis\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/ncis-br.png"),
    (r"\bcsi\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/csi-br.png"),
    (r"\bmacgyver\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/macgyver-br.png"),
    (r"\bdexter\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/dexter-br.png"),
    (r"\bmasterchef\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/masterchef-br.png"),
    (r"\bcatfish\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/catfish-br.png"),

    # Documentários & História
    (r"\bdiscovery turbo\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-turbo-br.png"),
    (r"\bdiscovery science\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-science-br.png"),
    (r"\bdiscovery world\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-world-br.png"),
    (r"\bdiscovery theater\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-theater-br.png"),
    (r"\bdiscovery home & health\b|\bdiscovery home and health\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-home-and-health-br.png"),
    (r"\binvestigation discovery\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/investigation-discovery-br.png"),
    (r"\banimal planet\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/animal-planet-br.png"),
    (r"\bhistory\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/history-br.png"),
    (r"\bnational geographic\b|\bnat geo\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/national-geographic-br.png"),
    (r"\bnasa\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/nasa-tv-br.png"),
    (r"\bdw\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/dw-br.png"),

    # Filmes & Cinema
    (r"\btnt\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tnt-br.png"),
    (r"\bspace\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/space-br.png"),
    (r"\bwarner\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/warner-channel-br.png"),
    (r"\bsony\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/sony-channel-br.png"),
    (r"\baxn\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/axn-br.png"),
    (r"\buniversal\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/universal-tv-br.png"),
    (r"\bparamount\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/paramount-network-br.png"),
    (r"\btelecine\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/telecine-premium-br.png"),
    (r"\bmegapix\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/megapix-br.png"),
    (r"\bcanal brasil\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/canal-brasil-br.png"),
    (r"\bcinemax\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/cinemax-br.png"),
    (r"\bhbo\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/hbo-br.png"),

    # Combate & Esportes
    (r"\bcombate\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/combate-br.png"),
    (r"\bsportv\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/sportv-br.png"),
    (r"\bespn\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/espn-brasil.png"),
    (r"\bpremiere\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/premiere-clubes-br.png"),
    (r"\btnt sports\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tnt-sports-br.png"),
    (r"\bufc\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/ufc-br.png"),
    (r"\bwwe\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/wwe-br.png"),

    # Notícias
    (r"\bcnn\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/cnn-brasil.png"),
    (r"\bjovem pan news\b|\bjovem pan\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/jovem-pan-news-br.png"),
    (r"\bbloomberg\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/bloomberg-tv-br.png"),
    (r"\beuronews\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/euronews-br.png"),

    # Música
    (r"\bmtv\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/mtv-br.png"),
    (r"\bmultishow\b", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/multishow-br.png"),
]

# 2. Paletas de gradientes modernas para o gerador de badges exclusivos
GRADIENTES = [
    ("#1e3a8a", "#3b82f6"), # Azul Safira
    ("#065f46", "#10b981"), # Verde Esmeralda
    ("#7c2d12", "#f97316"), # Laranja Âmbar
    ("#581c87", "#a855f7"), # Roxo Ametista
    ("#831843", "#ec4899"), # Rosa Pink
    ("#164e63", "#06b6d4"), # Ciano Oceano
    ("#881337", "#f43f5e"), # Carmim Rubro
    ("#1e293b", "#475569"), # Titânio Escuro
    ("#713f12", "#eab308"), # Dourado Ouro
    ("#14532d", "#22c55e"), # Verde Floresta
]

def extrair_iniciais(nome):
    # Remove sufixos como (720p), (Digital Leve), HD, etc.
    limpo = re.sub(r"\(.*?\)|\[.*?\]|\bHD\b|\bSD\b|\b4K\b|\bFHD\b|\bDigital\b|\bLeve\b|\bFibra\b", "", nome).strip()
    palavras = [p for p in limpo.split() if p.lower() not in ["de", "da", "do", "das", "dos", "e", "the", "a", "tv"]]
    if not palavras:
        palavras = limpo.split()
    
    if len(palavras) >= 3:
        iniciais = (palavras[0][0] + palavras[1][0] + palavras[2][0]).upper()
    elif len(palavras) == 2:
        iniciais = (palavras[0][:2] + palavras[1][0]).upper()
    elif len(palavras) == 1 and len(palavras[0]) >= 3:
        iniciais = palavras[0][:3].upper()
    elif len(palavras) == 1:
        iniciais = palavras[0].upper()
    else:
        iniciais = "TV"
    return iniciais[:4]

def gerar_badge_svg(nome, categoria=""):
    iniciais = extrair_iniciais(nome)
    # Hash determinístico para cor única e estável do canal
    h = int(hashlib.md5(nome.encode("utf-8")).hexdigest(), 16)
    c1, c2 = GRADIENTES[h % len(GRADIENTES)]
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <defs>
    <linearGradient id="grad_{h%1000}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="100" height="100" rx="22" fill="url(#grad_{h%1000})"/>
  <rect x="2" y="2" width="96" height="96" rx="20" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>
  <text x="50" y="58" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="30" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="1">{iniciais}</text>
  <rect x="28" y="72" width="44" height="14" rx="7" fill="rgba(0,0,0,0.3)"/>
  <text x="50" y="82.5" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="8.5" font-weight="800" fill="rgba(255,255,255,0.85)" text-anchor="middle" letter-spacing="0.5">LIVE</text>
</svg>"""
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)

# 3. Ler todos os canais ativos
c.execute("SELECT id, nome, logo, categoria FROM canais WHERE status = 'ATIVO'")
canais = c.fetchall()

atualizados_oficiais = 0
atualizados_badges = 0
mantidos_bons = 0

for c_id, nome, logo, cat in canais:
    nome_lower = nome.lower()
    novo_logo = None
    
    # Verificar se logo atual é inválido / spam / 127.0.0.1
    logo_invalido = (
        not logo 
        or logo.strip() == "" 
        or "127.0.0.1" in logo 
        or "88tv.store" in logo 
        or "localhost" in logo
        or "casino" in logo.lower()
    )
    
    # 1º Passo: Checar correspondência com Logo Oficial
    for padrao, url_oficial in LOGOS_OFICIAIS:
        if re.search(padrao, nome_lower):
            novo_logo = url_oficial
            atualizados_oficiais += 1
            break
            
    # 2º Passo: Se não achou oficial, e o logo atual for inválido, gerar Badge Exclusivo
    if not novo_logo:
        if logo_invalido:
            novo_logo = gerar_badge_svg(nome, cat)
            atualizados_badges += 1
        else:
            mantidos_bons += 1
            novo_logo = logo
            
    # Atualizar canal no banco
    c.execute("UPDATE canais SET logo = ? WHERE id = ?", (novo_logo, c_id))

conn.commit()
print("=== RESULTADO DA PERSONALIZAÇÃO DE ÍCONES ===")
print(f"Canais com Logos Oficiais Mapeados em Alta Definição: {atualizados_oficiais}")
print(f"Canais com Badges Vetoriais Exclusivos Gerados:       {atualizados_badges}")
print(f"Canais que mantiveram Logos Originais Válidos:        {mantidos_bons}")
print(f"Total de canais ativos processados:                   {len(canais)}")

# Verificar se sobrou algum canal sem logo
c.execute("SELECT count(*) FROM canais WHERE status = 'ATIVO' AND (logo IS NULL OR logo = '')")
restantes_sem_logo = c.fetchone()[0]
print(f"Canais sem logo restantes: {restantes_sem_logo} (ZERO!)")

conn.close()
