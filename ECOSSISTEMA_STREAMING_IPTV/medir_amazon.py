import urllib.request
import time

u = "https://amazonsat.brasilstream.com.br/hls/amazonsat/index.m3u8"
start = time.time()
try:
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        t_connect = time.time() - start
        data = resp.read()
        t_total = time.time() - start
        print(f"Tempo de conexao: {t_connect:.3f}s | Tempo de leitura: {t_total:.3f}s | Bytes lidos: {len(data)}")
except Exception as e:
    print(f"Erro ao testar {u}: {e}")
