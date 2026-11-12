import urllib.request
import ssl
import time
from concurrent.futures import ThreadPoolExecutor

urls_to_test = [
    ("ESPN Brasil (1080p)", "http://181.78.197.59:8000/play/a07z/index.m3u8"),
    ("ESPN 3 Brasil (1080p)", "http://181.78.197.59:8000/play/a081/index.m3u8"),
    ("ESPN 4 Brasil (1080p)", "http://181.78.197.59:8000/play/a07n/index.m3u8"),
    ("CazéTV (1080p)", "http://138.204.86.4:8080/CAZE_TV/playlist.m3u8"),
    ("ge Fast Globo (1080p)", "https://dfr80qz435crc.cloudfront.net/EFGH/Amagi/Globo/GE_Fast_BR/playlist.m3u8"),
    ("Band Sports (1080p)", "https://cdn-5.nxplay.com.br/BAND_SPORTS/index.m3u8"),
    ("SporTV 2 (1080p)", "http://195.178.110.110/sportv2/index.m3u8"),
    ("SporTV 3 (1080p)", "http://195.178.110.110/sportv3/index.m3u8"),
    ("Combate (UFC / Lutas)", "http://143.14.134.107/167/index.m3u8"),
    ("Red Bull TV Esportes", "https://rbmn-live.akamaized.net/hls/live/590964/BoRB-AT/master.m3u8")
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def testar(item):
    name, u = item
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=3.5) as resp:
            ms = int((time.time() - t0) * 1000)
            return (True, name, resp.status, ms, u)
    except Exception as e:
        return (False, name, str(e), 0, u)

with ThreadPoolExecutor(max_workers=5) as ex:
    results = list(ex.map(testar, urls_to_test))

print("AUDITORIA DOS CANAIS DE ESPORTE:")
for r in results:
    if r[0]:
        print(f"✅ {r[1]}: HTTP {r[2]} | {r[3]}ms | {r[4]}")
    else:
        print(f"❌ {r[1]}: {r[2]}")
