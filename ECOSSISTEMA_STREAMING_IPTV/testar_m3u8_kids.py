import urllib.request

u = "http://rtv30t.com:80/live/Wintvx/Wtv1020/71874.m3u8"
req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("M3U8 STATUS:", resp.status)
        content = resp.read().decode('utf-8')
        print("M3U8 CONTENT:\n", content[:400])
except Exception as e:
    print("M3U8 ERRO:", e)
