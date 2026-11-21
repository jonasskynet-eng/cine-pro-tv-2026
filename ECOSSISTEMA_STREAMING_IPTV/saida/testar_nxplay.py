import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://nxplay.com.br/',
    'Origin': 'https://nxplay.com.br'
}

u = "https://cdn-5.nxplay.com.br/GLOBO_SP_TK/index.m3u8"
try:
    req = urllib.request.Request(u, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
        print(f"Status: {resp.status}")
except Exception as e:
    print(f"Erro: {e}")
