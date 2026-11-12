import urllib.request
import urllib.parse

u = "http://localhost:8080/proxy?url=" + urllib.parse.quote("https://amazonsat.brasilstream.com.br/hls/amazonsat/index.m3u8")
with urllib.request.urlopen(u, timeout=5) as r:
    print("Amazon Sat Status via Proxy:", r.status)
    content = r.read().decode('utf-8')
    linhas = content.splitlines()
    chunk_line = [l for l in linhas if l.startswith('/proxy?url=')][0]
    print("Primeiro chunk Amazon Sat:", chunk_line[:80])
    
# Testar buscar o chunk do Amazon Sat pelo proxy
with urllib.request.urlopen("http://localhost:8080" + chunk_line, timeout=5) as r2:
    print("Amazon Sat Chunk Status:", r2.status, "Bytes:", len(r2.read(5000)))
