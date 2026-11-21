import urllib.request
import ssl

u = "http://200.77.176.130:8000/udp/224.0.0.1:49152"
try:
    with urllib.request.urlopen(u, timeout=3) as resp:
        print("Status:", resp.status)
        print("Content-Type:", resp.headers.get('Content-Type'))
        chunk = resp.read(1024)
        print("Lido bytes:", len(chunk), "começa com:", chunk[:16].hex())
except Exception as e:
    print("Erro:", e)
