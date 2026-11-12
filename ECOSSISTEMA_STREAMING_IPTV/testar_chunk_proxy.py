import urllib.request
import urllib.parse

# 1. Pegar manifesto pelo proxy
u_m3u8 = "http://localhost:8080/proxy?url=" + urllib.parse.quote("http://rtv30t.com:80/live/Wintvx/Wtv1020/71874.m3u8")
resp = urllib.request.urlopen(u_m3u8, timeout=5)
manifest = resp.read().decode('utf-8')
print("Manifest lido pelo proxy:")
linhas = manifest.splitlines()
chunk_line = [l for l in linhas if l.startswith('/proxy?url=')][0]
print("Primeiro chunk pelo proxy:", chunk_line[:100])

# 2. Testar buscar o chunk pelo proxy
u_chunk = "http://localhost:8080" + chunk_line
print("Testando fetch do chunk...")
try:
    with urllib.request.urlopen(u_chunk, timeout=5) as r2:
        print("CHUNK STATUS:", r2.status)
        print("CHUNK LEN:", len(r2.read(5000)))
except Exception as e:
    print("ERRO NO CHUNK:", e)
