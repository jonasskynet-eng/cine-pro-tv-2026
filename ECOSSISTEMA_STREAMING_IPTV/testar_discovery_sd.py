from pathlib import Path
import urllib.request

p = Path(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\lista_rtv30t_wintvx.m3u')
lines = p.read_text(encoding='utf-8', errors='ignore').splitlines()

desejados = [
    'Discovery Channel SD',
    'Discovery Kids SD',
    'Discovery Turbo SD',
    'Discovery H&H SD',
    'Discovery Science SD',
    'Discovery Theater SD',
    'Animal Planet SD',
    'ID SD',
    'Food Network SD',
    'TLC SD',
    'HGTV SD'
]

descobertos = {}
for i in range(len(lines)-1):
    l = lines[i]
    if l.startswith('#EXTINF:'):
        for d in desejados:
            if d.lower() in l.lower() and ('Canais |' in l or 'BR |' in l or 'BRASIL' in l):
                nome = l.split(',')[-1].strip()
                url = lines[i+1].strip()
                descobertos[d] = (nome, url)
                break

print("Testando versões SD / Digital leves:")
confirmados_sd = {}
for k, (nome, url) in descobertos.items():
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                print(f"[OK LEVE] {nome} -> {url}")
                confirmados_sd[k] = (nome, url)
            else:
                print(f"[STATUS {resp.status}] {nome}")
    except Exception as e:
        print(f"[FALHA] {nome} -> {e}")

print(f"\nTotal confirmados leves: {len(confirmados_sd)}")
