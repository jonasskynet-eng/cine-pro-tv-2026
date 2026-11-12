import urllib.request
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json

PASTA_BASE = Path(r"C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
ARQUIVO_M3U = PASTA_BASE / "saida" / "lista_brasil_turbo.m3u"

linhas = ARQUIVO_M3U.read_text(encoding="utf-8").splitlines()
candidatos = []
for i, l in enumerate(linhas):
    if l.startswith("#EXTINF:") and i + 1 < len(linhas):
        nome = l.split(",")[-1].strip()
        url = linhas[i+1].strip()
        candidatos.append((nome, url))

def testar_stream_real(item):
    nome, url = item
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = resp.read(300).decode("utf-8", errors="ignore")
            if "#EXT" in data:
                return {"nome": nome, "url": url, "online": True}
    except:
        pass
    return {"nome": nome, "url": url, "online": False}

aprovados = []
with ThreadPoolExecutor(max_workers=30) as pool:
    tarefas = [pool.submit(testar_stream_real, c) for c in candidatos]
    for t in as_completed(tarefas):
        res = t.result()
        if res["online"]:
            aprovados.append(res)

# Adiciona canais internacionais e FAST que nunca caem
canais_ouro = [
    {"nome": "Red Bull TV Esportes [1080p]", "url": "https://rbmn-live.akamaized.net/hls/live/590964/BoRB-AT/master.m3u8", "categoria": "⚽ Esportes"},
    {"nome": "New Brasil HD (CloudFront) [1080p]", "url": "https://dfr80qz435crc.cloudfront.net/EFGH/Amagi/NewCo/New_Brasil_BR/New_Brasil.m3u8", "categoria": "📰 Notícias"},
    {"nome": "FIFA+ Brasil [720p]", "url": "https://e3be9ac5.wurl.com/master/f36d25e7e52f1ba8d7e56eb859c636563214f541/TEctYnJfRklGQVBsdXNQb3J0dWd1ZXNlX0hMUw/playlist.m3u8", "categoria": "⚽ Esportes"},
    {"nome": "Amazon Sat HD [1080p]", "url": "https://amazonsat.brasilstream.com.br/hls/amazonsat/index.m3u8", "categoria": "🌎 Cultura"},
    {"nome": "DW Brasil Notícias [1080p]", "url": "https://dwamdstream102.akamaized.net/hls/live/2015525/dwstream102/index.m3u8", "categoria": "📰 Notícias"},
    {"nome": "NASA TV Espaço HD [720p]", "url": "https://ntv1.akamaized.net/hls/live/2014075/NASA-NTV1-HLS/master.m3u8", "categoria": "🌎 Documentários"}
]

for ap in aprovados:
    if not any(c["url"] == ap["url"] for c in canais_ouro):
        canais_ouro.append({
            "nome": ap["nome"],
            "url": ap["url"],
            "categoria": "🌎 Ao Vivo"
        })

print(f"Total de canais aprovados no Filtro Ouro: {len(canais_ouro)}")
(PASTA_BASE / "saida" / "canais_ouro.json").write_text(json.dumps(canais_ouro, indent=2, ensure_ascii=False), encoding="utf-8")
