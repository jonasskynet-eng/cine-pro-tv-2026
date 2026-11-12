import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

url = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/br.m3u"
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        print(f"Baixado br.m3u com {len(content.splitlines())} linhas")
        
        # Filtrar canais de interesse
        linhas = content.splitlines()
        for i, l in enumerate(linhas):
            if l.startswith('#EXTINF'):
                low = l.lower()
                if any(k in low for k in ['globo', 'sbt', 'cultura', 'band', 'record', 'redetv', 'gazeta', 'brasil']):
                    if i + 1 < len(linhas):
                        u = linhas[i+1].strip()
                        print(f"  {l.split(',')[-1].strip()} -> {u}")
except Exception as e:
    print("Erro ao baixar br.m3u:", e)
