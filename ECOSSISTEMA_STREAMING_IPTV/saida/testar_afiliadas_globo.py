import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

# Testar feeds conhecidos de afiliadas da Globo
cands_globo = [
    ("Globo SP (Nxplay)", "https://cdn-5.nxplay.com.br/GLOBO_SP_TK/index.m3u8"),
    ("Globo RJ (Nxplay)", "https://cdn-5.nxplay.com.br/GLOBO_RJ_TK/index.m3u8"),
    ("Globo Minas (Nxplay)", "https://cdn-5.nxplay.com.br/GLOBO_MINAS_TK/index.m3u8"),
    ("Globo DF (Nxplay)", "https://cdn-5.nxplay.com.br/GLOBO_DF_TK/index.m3u8"),
    ("TV Morena (Globo)", "https://media.cdntvms.com.br/tvmorena/index.m3u8"),
    ("TV Gazeta AL (Globo)", "https://stmv1.samcast.com.br/gazetaweb/gazetaweb/playlist.m3u8"),
    ("TV Anhangüera (Globo)", "https://cdn.jmvstream.com/w/LVW-11200/LVW11200/playlist.m3u8"),
    ("Globo Nordeste", "https://video09.logicahost.com.br/globonordeste/globonordeste/playlist.m3u8"),
    ("TV Liberal (Globo)", "https://cdn.jmvstream.com/w/LVW-12345/playlist.m3u8"),
    ("Globo Play Simulado", "https://player.globo.com/live/1080p/index.m3u8")
]

for nome, u in cands_globo:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
            data = resp.read(128).decode('utf-8', errors='ignore')
            if resp.status == 200 and '#EXTM3U' in data:
                print(f"  [200 OK] {nome} -> {u}")
            else:
                print(f"  [{resp.status}] {nome}")
    except Exception as e:
        print(f"  [OFFLINE] {nome}: {e}")
