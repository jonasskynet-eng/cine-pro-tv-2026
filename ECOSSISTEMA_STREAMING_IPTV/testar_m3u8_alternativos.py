import urllib.request

links = [
    ("Discovery Channel sua.tv", "http://hls1.sua.tv:80/live/discoverychannelfhd/s.m3u8"),
    ("Discovery Kids 181.224", "http://181.224.200.5:2277/play/a00o/index.m3u8"),
    ("Discovery Turbo 38.134", "http://38.134.250.110:8000/play/a01y/index.m3u8"),
    ("Discovery Science 45.171", "http://45.171.64.30:6060/play/a007/index.m3u8"),
    ("Discovery H&H 45.184", "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/39.m3u8"),
    ("Animal Planet 190.128", "http://190.128.214.97:64333/play/a01n/index.m3u8"),
    ("Investigation ID 45.184", "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/41.m3u8")
]

for nome, url in links:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f"[OK] {nome} -> Status: {resp.status} - Content: {len(resp.read())} bytes")
    except Exception as e:
        print(f"[FALHA] {nome} -> {e}")
