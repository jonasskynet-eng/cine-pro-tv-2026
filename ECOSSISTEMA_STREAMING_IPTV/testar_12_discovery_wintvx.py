from pathlib import Path
import urllib.request
import re

p = Path(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\lista_rtv30t_wintvx.m3u')
lines = p.read_text(encoding='utf-8', errors='ignore').splitlines()

alvos = [
    'Discovery Channel',
    'Discovery Kids',
    'Discovery Turbo',
    'Discovery H&H',
    'Discovery Science',
    'Discovery Theater',
    'Discovery World',
    'Animal Planet',
    'Investigation Discovery',
    'Food Network',
    'TLC',
    'HGTV'
]

canais_encontrados = {a: [] for a in alvos}

for i in range(len(lines)-1):
    l = lines[i]
    if l.startswith('#EXTINF:'):
        for alvo in alvos:
            if alvo.lower() in l.lower():
                nome = l.split(',')[-1].strip()
                url = lines[i+1].strip()
                # Apenas se for pt / br
                if any(x in l for x in ['Canais |', 'BR |', 'BRASIL', 'Infantis', 'Documentarios', 'Variedades']):
                    canais_encontrados[alvo].append((nome, url))
                break

print("Testando variantes de cada um dos 12 canais Discovery:")
melhores = {}

for alvo, lista in canais_encontrados.items():
    print(f"\n--- {alvo} (Variantes: {len(lista)}) ---")
    achou = False
    for nome, url in lista:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    print(f"  [ATIVO] {nome} -> {url}")
                    melhores[alvo] = (nome, url)
                    achou = True
                    break
        except Exception:
            pass
    if not achou:
        print(f"  [X] Nenhuma variante online encontrada para {alvo}")

print("\n\n=== RESULTADO FINAL: 12 CANAIS DISCOVERY ATIVOS ===")
for alvo, (nome, url) in melhores.items():
    print(f"{alvo}: {nome} -> {url}")
