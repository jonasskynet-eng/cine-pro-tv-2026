"""
Coletor de Guia de Programação (EPG) Real em XMLTV Brasileiro para o CinePro TV.
Baixa fontes abertas de EPG (iptv-epg.org e epg.pw), filtra apenas a janela das
próximas 14 horas e gera docs/epg_br.json ultracompacto para o player web.
"""

from datetime import datetime, timezone, timedelta
import gzip
import json
import os
from pathlib import Path
import re
import time
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET

BASE_DIR = Path(__file__).resolve().parent
SAIDA_DIR = BASE_DIR / "saida"
DOCS_DIR = BASE_DIR.parent / "docs"
DESKTOP_DIR = Path(r"C:\Users\jonas\Desktop\iptv") if os.name == "nt" else (SAIDA_DIR / "playlists_m3u")

FONTES_XMLTV = [
    ("iptv-epg.org", "https://iptv-epg.org/files/epg-br.xml", False),
    ("epg.pw", "https://epg.pw/xmltv/epg_BR.xml.gz", True),
]


def normalizar_chave(texto: str) -> str:
    txt = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode("ascii").lower()
    txt = re.sub(r"^(br|pt)\s*[-:|]\s*", "", txt)
    txt = re.sub(
        r"^(sao paulo/sp|rio de janeiro/rj|belo horizonte/mg|brasilia/df|curitiba/pr|porto alegre/rs|sp|rj|mg)\s+",
        "",
        txt,
    )
    txt = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", txt)
    txt = re.sub(r"\b(hd|fhd|sd|uhd|4k|fibra|leve|digital|oficial|ao vivo|3)\b", " ", txt)
    txt = re.sub(r"[^a-z0-9]+", " ", txt).strip()
    return txt


def parse_xmltv_ts(valor: str) -> int:
    if not valor:
        return 0
    m = re.match(r"(\d{14})(?:\s*([+-]\d{4}))?", valor.strip())
    if not m:
        return 0
    dt = datetime.strptime(m.group(1), "%Y%m%d%H%M%S")
    tz_str = m.group(2)
    if tz_str:
        sinal = 1 if tz_str[0] == "+" else -1
        horas = int(tz_str[1:3])
        mins = int(tz_str[3:5])
        offset = timezone(timedelta(hours=sinal * horas, minutes=sinal * mins))
        dt = dt.replace(tzinfo=offset)
    else:
        dt = dt.replace(tzinfo=timezone(timedelta(hours=-3)))
    return int(dt.timestamp())


def baixar_fonte(url: str, eh_gzip: bool) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=18) as resp:
        bruto = resp.read()
    return gzip.decompress(bruto) if eh_gzip else bruto


def coletar_epg() -> dict:
    agora = int(time.time())
    janela_inicio = agora - 3600       # 1h atrás
    janela_fim = agora + 6 * 3600      # 6h à frente (enxuto e leve)

    mapa_canais = {}
    fontes_ok = []

    for nome_fonte, url, eh_gzip in FONTES_XMLTV:
        try:
            xml_bytes = baixar_fonte(url, eh_gzip)
            root = ET.fromstring(xml_bytes)
        except Exception as exc:
            print(f"[EPG] Aviso ao baixar {nome_fonte}: {exc}")
            continue

        id_para_chave = {}
        for ch in root.findall("channel"):
            cid = ch.attrib.get("id", "")
            disp = ch.findtext("display-name") or cid
            chave = normalizar_chave(disp) or normalizar_chave(cid)
            if cid and chave:
                id_para_chave[cid] = chave

        inseridos_fonte = 0
        for prog in root.findall("programme"):
            cid = prog.attrib.get("channel", "")
            chave = id_para_chave.get(cid)
            if not chave:
                continue
            ini = parse_xmltv_ts(prog.attrib.get("start", ""))
            fim = parse_xmltv_ts(prog.attrib.get("stop", ""))
            if not ini or not fim or fim <= janela_inicio or ini >= janela_fim:
                continue
            titulo = (prog.findtext("title") or "").strip()
            if not titulo:
                continue
            desc = (prog.findtext("desc") or "").strip()
            if desc.lower() == titulo.lower():
                desc = ""
            elif len(desc) > 65:
                desc = desc[:62].rstrip() + "..."
            lista = mapa_canais.setdefault(chave, [])
            lista.append([ini, fim, titulo, desc] if desc else [ini, fim, titulo])
            inseridos_fonte += 1

        if inseridos_fonte > 0:
            fontes_ok.append(nome_fonte)
            print(f"[EPG] {nome_fonte}: {inseridos_fonte} programas na janela de hoje.")

    # Deduplicar e ordenar programas de cada canal
    canais_limpos = {}
    for chave, progs in mapa_canais.items():
        vistos = set()
        ordenados = []
        for item in sorted(progs, key=lambda x: x[0]):
            assinatura = (item[0], item[2].lower())
            if assinatura in vistos:
                continue
            vistos.add(assinatura)
            ordenados.append(item)
        if ordenados:
            canais_limpos[chave] = ordenados[:8]

    return {
        "atualizado_em": agora,
        "fontes": fontes_ok,
        "total_canais": len(canais_limpos),
        "canais": canais_limpos,
    }


def main():
    pacote = coletar_epg()
    if pacote["total_canais"] == 0:
        print("[EPG] Nenhuma fonte respondeu agora; mantendo arquivo EPG anterior se existir.")
        return

    conteudo = json.dumps(pacote, ensure_ascii=False, separators=(",", ":"))
    SAIDA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (SAIDA_DIR / "epg_br.json").write_text(conteudo, encoding="utf-8")
    (DOCS_DIR / "epg_br.json").write_text(conteudo, encoding="utf-8")
    if DESKTOP_DIR.exists():
        (DESKTOP_DIR / "epg_br.json").write_text(conteudo, encoding="utf-8")
    print(f"[EPG] Gerado epg_br.json com {pacote['total_canais']} canais reais ({len(conteudo) // 1024} KB).")


if __name__ == "__main__":
    main()
