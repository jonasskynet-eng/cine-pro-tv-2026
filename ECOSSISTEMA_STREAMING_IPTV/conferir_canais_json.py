import json
from pathlib import Path

p = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\index.html")
txt = p.read_text(encoding="utf-8")
start = txt.find("const CANAIS = [")
end = txt.find("];", start) + 1
canais = json.loads(txt[start+15:end])
print(f"Total de canais M3U8 validados no JSON: {len(canais)}")
for c in canais[:10]:
    print(f"- {c['nome']} ({c['categoria']}) -> {c['url'][:60]}")
