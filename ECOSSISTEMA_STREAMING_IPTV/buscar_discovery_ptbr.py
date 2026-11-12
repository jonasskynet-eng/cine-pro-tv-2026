import urllib.request
import ssl
import re
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 1. Procurar nas contas do rtv30t.com (LISTA IPTV 2026.txt) os canais da Discovery no Brasil
import os
arquivo_txt = r'c:\Users\jonas\Documents\aula de logistica\Roteiro de estudos  Atividade Extensionista Empreendedorismo\LISTA IPTV 2026.txt'

servidor_xtream = 'http://rtv30t.com:80'
user = 'Wintvx'
pwd = 'Wtv1020'

print("Buscando canais Discovery PT-BR no painel Xtream Codes...")
url_live = f'{servidor_xtream}/player_api.php?username={user}&password={pwd}&action=get_live_streams'

req = urllib.request.Request(url_live, headers={'User-Agent': 'IPTVSmartersPro'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        canais_xtream = json.loads(r.read().decode('utf-8', errors='ignore'))
    
    discovery_ptbr = []
    for c in canais_xtream:
        nome = c.get('name', '')
        lower = nome.lower()
        if any(k in lower for k in ['discovery', 'animal planet', 'investigação discovery', 'investigation discovery', 'food network', 'tlc', 'hgtv']):
            stream_id = c.get('stream_id')
            stream_url = f"{servidor_xtream}/live/{user}/{pwd}/{stream_id}.ts"
            hls_url = f"{servidor_xtream}/live/{user}/{pwd}/{stream_id}.m3u8"
            discovery_ptbr.append({
                'nome': nome,
                'stream_id': stream_id,
                'url_ts': stream_url,
                'url_m3u8': hls_url,
                'categoria': c.get('category_id')
            })

    print(f"Total de canais Discovery em Português encontrados no servidor: {len(discovery_ptbr)}")
    for d in discovery_ptbr[:15]:
        print(f" - {d['nome']} -> {d['url_m3u8']}")
except Exception as e:
    print(f"Erro ao buscar no Xtream: {e}")
