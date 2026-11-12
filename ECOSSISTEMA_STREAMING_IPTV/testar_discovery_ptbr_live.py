import urllib.request
import json
import time

servidor = 'http://rtv30t.com:80'
user = 'Wintvx'
pwd = 'Wtv1020'

url_live = f'{servidor}/player_api.php?username={user}&password={pwd}&action=get_live_streams'
req = urllib.request.Request(url_live, headers={'User-Agent': 'IPTVSmartersPro'})
with urllib.request.urlopen(req, timeout=10) as r:
    canais = json.loads(r.read().decode('utf-8', errors='ignore'))

# Mapear os canais principais em FHD / HD
desejados = [
    'Discovery Channel FHD',
    'Discovery Kids FHD',
    'Discovery Turbo FHD',
    'Discovery H&H FHD',
    'Discovery Science HD',
    'Discovery Theater FHD',
    'Discovery World FHD',
    'Animal Planet FHD',
    'ID FHD',
    'TLC FHD',
    'Food Network FHD',
    'HGTV FHD'
]

selecionados = {}
for c in canais:
    nome = c.get('name', '').strip()
    for d in desejados:
        if d.lower() == nome.lower() or (d.lower() in nome.lower() and ('fhd' in nome.lower() or 'hd' in nome.lower())):
            if d not in selecionados:
                selecionados[d] = c

print(f"Canais selecionados para teste de sinal ao vivo: {len(selecionados)}")
for d, c in selecionados.items():
    sid = c.get('stream_id')
    stream_url = f"{servidor}/live/{user}/{pwd}/{sid}.ts"
    t0 = time.time()
    try:
        r_stream = urllib.request.Request(stream_url, headers={'User-Agent': 'VLC/3.0.18'})
        with urllib.request.urlopen(r_stream, timeout=4) as res:
            data = res.read(10240) # baixar 10KB
            ms = int((time.time() - t0) * 1000)
            print(f"✅ {c.get('name')}: OK ({len(data)} bytes) | Latência: {ms}ms | ID: {sid}")
    except Exception as e:
        print(f"❌ {c.get('name')}: {e}")
