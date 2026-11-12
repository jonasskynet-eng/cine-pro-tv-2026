import urllib.request
import urllib.parse
import time

url = "http://localhost:8080/proxy?url=" + urllib.parse.quote("http://rtv30t.com:80/Wintvx/Wtv1020/71874.ts")
start = time.time()
try:
    with urllib.request.urlopen(url, timeout=5) as resp:
        t_resp = time.time() - start
        print(f"Proxy respondeu em {t_resp:.3f}s com status {resp.status}")
        chunk = resp.read(32 * 1024)
        t_total = time.time() - start
        print(f"Proxy leu {len(chunk)} bytes em {t_total:.3f}s total!")
except Exception as e:
    print("Erro:", e)
