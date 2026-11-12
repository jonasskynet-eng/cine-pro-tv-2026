import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

globo_extra = [
    ("G1 Ao Vivo", "https://s2.glbimg.com/live/g1/index.m3u8"),
    ("Globo News (Amagi)", "https://amg00527-amg00527c5-amgplt0026.playout.now3.amagi.tv/globonews/master.m3u8"),
    ("Globo Internacional", "https://globo-live.latam.cdn.glbimg.com/hls/globo/index.m3u8"),
    ("Globo RJ Live", "https://stream.cademeucanal.com.br/globorj/index.m3u8"),
    ("Globo SP Live", "https://stream.cademeucanal.com.br/globosp/index.m3u8"),
    ("Canal Futura (Globo Oficial)", "http://170.83.16.50/FUTURA/index.m3u8"),
    ("Globo Rural Live", "https://s2.glbimg.com/globorural/index.m3u8")
]

for nome, u in globo_extra:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=2.5) as resp:
            data = resp.read(128).decode('utf-8', errors='ignore')
            print(f"[{resp.status}] {nome} -> {len(data)} bytes")
    except Exception as e:
        # print(f"[ERRO] {nome}: {e}")
        pass
