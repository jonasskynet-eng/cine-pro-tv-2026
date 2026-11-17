import concurrent.futures
import json
import pathlib
import re
import urllib.request

BASE_DIR = pathlib.Path(__file__).resolve().parent
OUT_JSON = BASE_DIR / "canais_comunidade_br.json"

FONTES = [
    ("iptv-org BR", "https://iptv-org.github.io/iptv/countries/br.m3u", "🇧🇷 Brasil"),
    ("Free-TV BR", "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_brazil.m3u8", "🇧🇷 Brasil"),
]

EXTRAS_MANUAIS = [
    {
        "nome": "Runtime TV Brasil (HTTPS)",
        "url": "https://stream.ads.ottera.tv/playlist.m3u8?network_id=2153",
        "logo": "",
        "grupo": "Movies",
        "pais": "🇧🇷 Brasil",
        "cors_star": 0,
    },
    {
        "nome": "Reino Infantil TV (HTTPS)",
        "url": "https://www.khuwemultimedia.com/hls/reinoinfantiltv/reinoinfantiltv.m3u8",
        "logo": "",
        "grupo": "Kids",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TVI Ficção (720p)",
        "url": "https://raw.githubusercontent.com/thomraider12/canaistvpt/main/m3u8s/tvificcao.m3u8",
        "logo": "",
        "grupo": "Series",
        "pais": "🇵🇹 Portugal / Lusófonos",
        "cors_star": 1,
    },
]


def coletar_candidatos():
    vistos = {}
    for _, fonte_url, pais in FONTES:
        req = urllib.request.Request(fonte_url, headers={"User-Agent": "Mozilla/5.0"})
        txt = urllib.request.urlopen(req, timeout=12).read().decode("utf-8", errors="ignore")
        nome_cur, logo_cur, grp_cur = "", "", ""
        for linha in txt.splitlines():
            s = linha.strip()
            if s.startswith("#EXTINF"):
                m_logo = re.search(r'tvg-logo="([^"]+)"', s)
                m_grp = re.search(r'group-title="([^"]+)"', s)
                logo_cur = m_logo.group(1) if m_logo else ""
                grp_cur = m_grp.group(1) if m_grp else ""
                nome_cur = s.split(",")[-1].strip()
            elif s.startswith("https://") and s not in vistos:
                if (
                    "[Not 24/7]" in nome_cur
                    or "_h265" in s.lower()
                    or re.match(r"^https://\d+\.\d+\.\d+\.\d+", s)
                    or "youtube.com" in s
                    or "youtu.be" in s
                ):
                    continue
                vistos[s] = {
                    "nome": nome_cur,
                    "url": s,
                    "logo": logo_cur,
                    "grupo": grp_cur,
                    "pais": pais,
                }
    for item in EXTRAS_MANUAIS:
        vistos.setdefault(item["url"], item)
    return list(vistos.values())


def testar_canal(item):
    try:
        req = urllib.request.Request(item["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            cors = resp.headers.get("Access-Control-Allow-Origin", "")
            body = resp.read(250).decode("utf-8", errors="ignore")
            if resp.status == 200 and "#EXTM3U" in body:
                item["cors_star"] = 1 if cors.strip() == "*" else 0
                return item
    except Exception:
        return None
    return None


def mapear_categoria(grupo, nome):
    g = (grupo + " " + nome).lower()
    if any(k in g for k in ("relig", "fonte tv", "plenitude", "rit tv", "universal", "terceiro anjo")):
        return "⛪ Religiosos"
    if any(k in g for k in ("encantador", "document", "science", "nature")):
        return "🔬 Discovery & Ciência"
    if any(k in g for k in ("news", "notic", "cnn", "uol", "aratu", "canal 38")):
        return "📰 Notícias"
    if any(k in g for k in ("kids", "nickelodeon", "cartoon", "infantil")):
        return "🧸 Infantil & Desenhos"
    if any(k in g for k in ("sport", "red bull")):
        return "⚽ Esportes & Ação"
    if any(k in g for k in ("movie", "runtime", "cine")):
        return "🎬 Filmes & Cinema"
    if any(k in g for k in ("series", "classic", "awtv", "ficção", "ficcao")):
        return "🍿 Séries & Maratona"
    return "📺 TV Aberta Brasil"


def main():
    cands = coletar_candidatos()
    print(f"Candidatos coletados (sem [Not 24/7] / H265): {len(cands)}")
    aprovados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
        for res in pool.map(testar_canal, cands):
            if res:
                res["categoria"] = mapear_categoria(res.get("grupo", ""), res["nome"])
                aprovados.append(res)

    aprovados.sort(key=lambda x: (x["categoria"], x["nome"].lower()))
    OUT_JSON.write_text(json.dumps(aprovados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Aprovados ao vivo e salvos em {OUT_JSON.name}: {len(aprovados)}")
    for a in aprovados:
        print(f"  - {a['categoria']} | CORS={'*' if a['cors_star'] else 'Ponte'} | {a['nome']}")


if __name__ == "__main__":
    main()
