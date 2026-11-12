import urllib.request
import time

u = "http://rtv30t.com:80/Wintvx/Wtv1020/71874.ts"
start = time.time()
try:
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        t_connect = time.time() - start
        data = resp.read(188 * 100) # Ler 100 pacotes TS
        t_total = time.time() - start
        print(f"Tempo de conexao: {t_connect:.3f}s | Tempo de leitura: {t_total:.3f}s | Bytes lidos: {len(data)}")
except Exception as e:
    print(f"Erro ao testar {u}: {e}")
