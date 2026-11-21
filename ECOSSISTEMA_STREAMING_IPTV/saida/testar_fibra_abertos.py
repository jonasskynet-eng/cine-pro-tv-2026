import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0'}

base_fibra = "http://170.83.16.50/"
candidatos_fibra = [
    "GLOBO/index.m3u8",
    "GLOBO_HD/index.m3u8",
    "GLOBO_SP/index.m3u8",
    "GLOBO_RJ/index.m3u8",
    "REDE_GLOBO/index.m3u8",
    "SBT/index.m3u8",
    "SBT_HD/index.m3u8",
    "SBT_SP/index.m3u8",
    "RECORD/index.m3u8",
    "RECORD_HD/index.m3u8",
    "RECORD_SP/index.m3u8",
    "BAND/index.m3u8",
    "BAND_HD/index.m3u8",
    "BAND_SP/index.m3u8",
    "CULTURA/index.m3u8",
    "TV_CULTURA/index.m3u8",
    "REDETV/index.m3u8",
    "REDE_TV/index.m3u8",
    "REDETV_HD/index.m3u8",
    "GAZETA/index.m3u8",
    "TV_GAZETA/index.m3u8",
    "TV_BRASIL/index.m3u8",
    "FUTURA/index.m3u8"
]

print("Testando rotas em http://170.83.16.50/:")
for rota in candidatos_fibra:
    u = base_fibra + rota
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=2.5) as resp:
            data = resp.read(128).decode('utf-8', errors='ignore')
            if resp.status == 200 and '#EXTM3U' in data:
                print(f"  [SUCESSO] {u}")
            else:
                print(f"  [Status {resp.status}] {u}")
    except Exception as e:
        # print(f"  [ERRO] {rota}: {e}")
        pass
