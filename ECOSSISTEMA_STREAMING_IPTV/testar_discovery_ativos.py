import urllib.request
import ssl
import time
from concurrent.futures import ThreadPoolExecutor

urls_to_test = [
    ("Discovery Channel", "https://streaming.aurora.enhanced.live/live/mpc/enl0eG1mLmVncmVzc2lvbl9tb2RlbA/hls/live/channel_01.m3u8"),
    ("Discovery Kids Brasil", "http://15.204.246.24:8080/DiscoveryKidsHD/index.m3u8"),
    ("Discovery Kids Latino", "http://181.224.200.5:2277/play/a00o/index.m3u8"),
    ("Discovery World Brasil", "http://15.204.246.24:8080/DiscoveryWorldHD/index.m3u8"),
    ("Discovery Turbo Latino", "http://38.134.250.110:8000/play/a01y/index.m3u8"),
    ("Discovery Science", "http://45.171.64.30:6060/play/a007/index.m3u8"),
    ("Discovery Theater HD", "http://181.224.200.5:2277/play/a0bj/index.m3u8"),
    ("Discovery Home & Health", "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/39.m3u8"),
    ("Animal Planet HD", "http://190.128.214.97:64333/play/a01n/index.m3u8"),
    ("Investigation Discovery", "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/41.m3u8"),
    ("TLC Latin America", "http://38.134.250.110:8000/play/a00n/index.m3u8"),
    ("HGTV Latin America", "http://38.87.224.19:2220/play/a01p/index.m3u8"),
    ("Pluto TV Turbo (24h)", "https://jmp2.uk/plu-6014761dfb91870008ea6463.m3u8"),
    ("Pluto TV Investigation (24h)", "https://jmp2.uk/plu-63808dc806aa4700075f319a.m3u8")
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

with ThreadPoolExecutor(max_workers=7) as ex:
    results = list(ex.map(testar, urls_to_test))

print("AUDITORIA DA FAMÍLIA DISCOVERY:")
for r in results:
    if r[0]:
        print(f"✅ {r[1]}: HTTP {r[2]} | {r[3]}ms | {r[4]}")
    else:
        print(f"❌ {r[1]}: {r[2]}")
