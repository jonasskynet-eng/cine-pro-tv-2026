from pathlib import Path
import re
import urllib.request

p = Path(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\lista_rtv30t_wintvx.m3u')
lines = p.read_text(encoding='utf-8', errors='ignore').splitlines()

termos = ['discovery', 'animal planet', 'investigation discovery', 'turbo', 'kids', 'sportv', 'espn', 'telecine', 'hbo']
candidatos = {}

for i in range(len(lines)-1):
    l = lines[i]
    if l.startswith('#EXTINF:'):
        for t in termos:
            if t in l.lower():
                nome = l.split(',')[-1].strip()
                url = lines[i+1].strip()
                # Apenas canais brasileiros / pt
                if any(x in l for x in ['Canais |', 'BR |', 'BRASIL', 'Infantis', 'Documentarios', 'Esportes', 'Filmes']):
                    if nome not in candidatos:
                        candidatos[nome] = url
                break

print(f'Total de candidatos encontrados: {len(candidatos)}')

# Testar uma amostra dos mais famosos
top_canais = [
    'Discovery Channel', 'Discovery Kids', 'Discovery Turbo', 'Discovery H&H',
    'Animal Planet', 'Investigation Discovery', 'SporTV', 'ESPN'
]

selecionados = []
for nome, url in candidatos.items():
    for tc in top_canais:
        if tc.lower() in nome.lower() and not any(s['target'] == tc for s in selecionados):
            selecionados.append({'target': tc, 'nome': nome, 'url': url})

print('\nTestando principais canais:')
ativos_confirmados = []
for item in selecionados:
    url = item['url']
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.status == 200:
                print(f"[OK] {item['nome']} -> {url}")
                ativos_confirmados.append(item)
            else:
                print(f"[STATUS {resp.status}] {item['nome']}")
    except Exception as e:
        print(f"[FALHA] {item['nome']} -> {e}")

print(f'\nTotal de canais confirmados 100% online: {len(ativos_confirmados)}')
