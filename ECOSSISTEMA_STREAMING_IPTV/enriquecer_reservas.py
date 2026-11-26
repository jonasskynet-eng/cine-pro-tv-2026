"""
Enriquece os canais brasileiros principais de docs/canais.json e ECOSSISTEMA_STREAMING_IPTV/saida/canais.json
com 2º e 3º links reservas (res e res2 — Plano B e Plano C) extraídos de URLs distintas já auditadas no catálogo.
Mantém exatamente os mesmos 200 canais da degustação pública.
"""

import json
import re
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAIZ = BASE_DIR.parent
ARQ_DOCS = RAIZ / "docs" / "canais.json"
ARQ_SAIDA = BASE_DIR / "saida" / "canais.json"
ARQ_VIP = BASE_DIR / "vip_privado" / "catalogo_vip_migrado.json"

FAMILIAS_BR = [
    ("sbt", ["sbt"]),
    ("record", ["recordtv", "record tv", "tv record", "record news"]),
    ("band", ["band tv", "band ", "bandeirantes", "bandnews", "band news"]),
    ("redetv", ["redetv", "rede tv"]),
    ("cultura", ["tv cultura", "cultura sp"]),
    ("tv_brasil", ["tv brasil", "ebc"]),
    ("futura", ["canal futura", "futura"]),
    ("rede_brasil", ["rede brasil"]),
    ("gazeta", ["tv gazeta", "gazeta sp"]),
    ("camara", ["tv camara"]),
    ("senado", ["tv senado"]),
    ("justica", ["tv justica"]),
    ("cnn_br", ["cnn brasil"]),
    ("jovem_pan", ["jovem pan"]),
    ("rede_vida", ["rede vida", "redevida"]),
]


def _norm(txt: str) -> str:
    s = unicodedata.normalize("NFKD", txt or "").encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def _identificar_familia(nome: str):
    n = _norm(nome)
    for fam, termos in FAMILIAS_BR:
        if any(t in n for t in termos):
            return fam
    return None


def main():
    if not ARQ_DOCS.exists():
        print("docs/canais.json não encontrado.")
        return

    base = json.loads(ARQ_DOCS.read_text(encoding="utf-8", errors="ignore"))
    pool = list(base)
    if ARQ_VIP.exists():
        try:
            vip = json.loads(ARQ_VIP.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(vip, list):
                pool.extend(vip)
        except Exception:
            pass

    urls_por_familia = {}
    for ch in pool:
        if not isinstance(ch, dict):
            continue
        fam = _identificar_familia(ch.get("nome", ""))
        if not fam:
            continue
        bucket = urls_por_familia.setdefault(fam, [])
        for campo in ("url", "res", "reserva_url", "res2"):
            u = str(ch.get(campo, "") or "").strip()
            if u.startswith("http") and u not in bucket:
                bucket.append(u)

    enriquecidos = 0
    for ch in base:
        fam = _identificar_familia(ch.get("nome", ""))
        if not fam:
            continue
        candidatos = [u for u in urls_por_familia.get(fam, []) if u != ch.get("url")]
        existentes = []
        for campo in ("res", "reserva_url", "res2"):
            u = str(ch.get(campo, "") or "").strip()
            if u and u != ch.get("url") and u not in existentes:
                existentes.append(u)
        for u in candidatos:
            if u not in existentes:
                existentes.append(u)
            if len(existentes) >= 2:
                break
        if existentes:
            ch["res"] = existentes[0]
            if len(existentes) >= 2:
                ch["res2"] = existentes[1]
            enriquecidos += 1

    conteudo = json.dumps(base, ensure_ascii=False, separators=(",", ":"))
    ARQ_DOCS.write_text(conteudo, encoding="utf-8")
    if ARQ_SAIDA.parent.exists():
        ARQ_SAIDA.write_text(conteudo, encoding="utf-8")

    print(f"Canais mantidos: {len(base)} | Canais com Plano B/C reforçado: {enriquecidos}")


if __name__ == "__main__":
    main()
