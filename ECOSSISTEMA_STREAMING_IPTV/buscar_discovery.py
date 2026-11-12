import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls_to_check = [
    'https://iptv-org.github.io/iptv/categories/documentary.m3u',
    'https://iptv-org.github.io/iptv/categories/kids.m3u',
    'https://iptv-org.github.io/iptv/languages/por.m3u',
    'https://iptv-org.github.io/iptv/languages/spa.m3u'
]

discovery_channels = []

for u in urls_to_check:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
            lines = resp.read().decode('utf-8', errors='ignore').splitlines()
        
        cur_info = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#EXTINF:'):
                cur_info = line
            elif not line.startswith('#') and cur_info:
                lower_info = cur_info.lower()
                if any(k in lower_info for k in ['discovery', 'animal planet', 'investigation discovery', 'hgtv', 'tlc']):
                    nome = cur_info.split(',')[-1].strip()
                    logo_m = re.search(r'tvg-logo="([^"]+)"', cur_info)
                    logo = logo_m.group(1) if logo_m else ''
                    grp_m = re.search(r'group-title="([^"]+)"', cur_info)
                    cat = grp_m.group(1).strip() if grp_m else 'Documentários'
                    discovery_channels.append({
                        'nome': nome,
                        'url': line,
                        'logo': logo,
                        'categoria': cat,
                        'fonte': u.split('/')[-1]
                    })
                cur_info = None
    except Exception as e:
        print(f"Erro em {u}: {e}")

print(f"Total de canais Discovery coletados do GitHub iptv-org: {len(discovery_channels)}")
vistos = set()
unicos = []
for d in discovery_channels:
    if d['nome'] not in vistos:
        vistos.add(d['nome'])
        unicos.append(d)

print(f"Total de canais Discovery únicos: {len(unicos)}")
for item in unicos[:35]:
    print(f" - {item['nome']} [{item['categoria']}] -> {item['url'][:65]}")
