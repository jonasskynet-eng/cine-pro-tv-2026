import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

# Testar repositórios populares de canais do Brasil
urls = [
    "https://raw.githubusercontent.com/LITUATUI/M3UPT/main/M3U/M3U_MUNDO.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br_abema.m3u",
    "https://raw.githubusercontent.com/matthuisman/sptv-playlist/master/playlist.m3u8",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_brazil.m3u8"
]

encontrados = []

for u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
            text = resp.read().decode('utf-8', errors='ignore')
            lines = text.splitlines()
            print(f"Baixado {u} com {len(lines)} linhas")
            for i, l in enumerate(lines):
                if l.startswith('#EXTINF') and any(t in l.lower() for t in ['globo', 'sbt', 'record', 'band', 'cultura']):
                    if i + 1 < len(lines):
                        link = lines[i+1].strip()
                        if link.startswith('http'):
                            encontrados.append((l.split(',')[-1].strip(), link))
    except Exception as e:
        print(f"Erro em {u}: {e}")

print(f"\nTotal encontrados: {len(encontrados)}")
for n, l in encontrados[:25]:
    print(f"  {n} -> {l}")
