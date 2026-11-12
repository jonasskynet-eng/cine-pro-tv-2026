import urllib.request

# Testar se o chunk precisa de Referer do m3u8
m3u8_url = "http://rtv30t.com:80/live/Wintvx/Wtv1020/71874.m3u8"
req = urllib.request.Request(m3u8_url, headers={"User-Agent": "Mozilla/5.0"})
content = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
linhas = [l for l in content.splitlines() if l.startswith('/hls/')]
chunk_rel = linhas[0]
chunk_url = "http://rtv30t.com:80" + chunk_rel
print("Chunk URL:", chunk_url[:80])

# Testar com diferentes headers
headers_variantes = [
    {"User-Agent": "Mozilla/5.0"},
    {"User-Agent": "Mozilla/5.0", "Referer": m3u8_url},
    {"User-Agent": "VLC/3.0.18 LibVLC/3.0.18"},
    {"User-Agent": "IPTVSmartersPro"}
]

for h in headers_variantes:
    try:
        r = urllib.request.Request(chunk_url, headers=h)
        with urllib.request.urlopen(r, timeout=3) as resp:
            print("Sucesso com header:", h.get("User-Agent"), "Referer:", h.get("Referer"), "Status:", resp.status)
            break
    except Exception as e:
        print("Falha com header:", h.get("User-Agent"), "Referer:", h.get("Referer"), "->", e)
