import urllib.request
import ssl

urls = [
    ('Boas Novas 1080p', 'https://cdn.jmvstream.com/w/LVW-9375/LVW9375_6i0wPBCHYc/playlist.m3u8'),
    ('Amazon Sat HD', 'https://amazonsat.brasilstream.com.br/hls/amazonsat/index.m3u8'),
    ('Kenan & Kel BR', 'https://jmp2.uk/plu-5ffcc5130fd98c0007f2e216.m3u8'),
    ('Comedy Central Brasil', 'https://stmv2.srvif.com/gafeab/gafeab/playlist.m3u8'),
    ('Loading 720p', 'https://stmv1.srvif.com/loadingtv/loadingtv/playlist.m3u8')
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for name, u in urls:
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=4) as r:
            cors = r.headers.get('Access-Control-Allow-Origin')
            data = r.read(150)
            print(f"✅ {name}: HTTP {r.status} | Bytes: {len(data)} | CORS: {cors}")
    except Exception as e:
        print(f"❌ {name}: {e}")
