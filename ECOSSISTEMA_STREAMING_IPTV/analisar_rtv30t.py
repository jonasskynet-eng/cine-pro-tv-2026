import urllib.request
import re
from pathlib import Path

PASTA_BASE = Path(r"C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
PASTA_SAIDA = PASTA_BASE / "saida"

url = "http://rtv30t.com/get.php?username=Wintvx&password=Wtv1020&type=m3u_plus"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

try:
    with urllib.request.urlopen(req, timeout=10.0) as resp:
        content = resp.read().decode("utf-8", errors="ignore")
        arquivo_local = PASTA_SAIDA / "lista_rtv30t_wintvx.m3u"
        arquivo_local.write_text(content, encoding="utf-8")
        
        lines = content.splitlines()
        extinf = [l for l in lines if l.startswith("#EXTINF:")]
        print(f"Total de canais na lista Wintvx: {len(extinf)}")

        grupos = set()
        padrao = re.compile(r'group-title="([^"]+)"')
        for l in extinf:
            m = padrao.search(l)
            if m:
                grupos.add(m.group(1))

        print(f"\nTotal de Categorias Encontradas: {len(grupos)}")
        for g in sorted(list(grupos)):
            print(f"  • {g}")

except Exception as e:
    print("Erro ao baixar:", e)
