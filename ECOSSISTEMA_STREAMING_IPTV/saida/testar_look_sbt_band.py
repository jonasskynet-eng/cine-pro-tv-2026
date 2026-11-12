import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

testes = [
    ("Globo SP Look", "http://95.211.149.215:8081/look/sptv/playlist.m3u8"),
    ("SBT Sambatech", "http://liveabr2.sambatech.com.br/abr/sbtabr_8fcdc5f0f8df8d4de56b22a2c6660470/livestreamabrsbtbkp.m3u8"),
    ("Band Look", "http://5.79.68.138:8081/look/band/playlist.m3u8")
]

for n, u in testes:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
            data = resp.read(128).decode('utf-8', errors='ignore')
            print(f"[{resp.status}] {n} -> {len(data)} bytes ({data[:50]})")
    except Exception as e:
        print(f"[ERRO] {n}: {e}")
