from pathlib import Path
p = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\index.html")
txt = p.read_text(encoding="utf-8")

s = txt.find("function sintonizar")
e = txt.find("function normalizar", s)
print(txt[s:e])
