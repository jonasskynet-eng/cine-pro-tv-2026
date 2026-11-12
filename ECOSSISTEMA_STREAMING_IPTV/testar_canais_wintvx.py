import urllib.request

canais_teste = [
    ('Discovery Channel FHD', 'http://rtv30t.com:80/Wintvx/Wtv1020/71862.ts'),
    ('Discovery Kids FHD', 'http://rtv30t.com:80/Wintvx/Wtv1020/71871.ts'),
    ('Discovery Turbo FHD', 'http://rtv30t.com:80/Wintvx/Wtv1020/71883.ts'),
    ('Animal Planet FHD', 'http://rtv30t.com:80/Wintvx/Wtv1020/71772.ts')
]

for nome, url in canais_teste:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            ct = resp.headers.get('Content-Type')
            cors = resp.headers.get('Access-Control-Allow-Origin')
            data = resp.read(5000)
            print(f'{nome} -> STATUS: {resp.status} | Content-Type: {ct} | CORS: {cors} | Bytes: {len(data)}')
    except Exception as e:
        print(f'{nome} -> ERRO: {e}')
