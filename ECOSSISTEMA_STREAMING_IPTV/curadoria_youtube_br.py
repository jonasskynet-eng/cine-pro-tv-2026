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
    # --- Infantil & Desenhos BR ---
    {
        "nome": "Fox Kids [Infantis]",
        "url": "https://stmv2.srvif.com/emlsilva/emlsilva/playlist.m3u8",
        "logo": "",
        "grupo": "Kids",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Jetsons TV [Infantis]",
        "url": "https://stmv1.srvif.com/jetsontv/jetsontv/playlist.m3u8",
        "logo": "",
        "grupo": "Kids",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Xtrema Cartoons",
        "url": "https://stmv6.voxtvhd.com.br/xtremacartoons/xtremacartoons/playlist.m3u8",
        "logo": "",
        "grupo": "Kids",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Beyblade | Pluto TV Brasil",
        "url": "https://service-stitcher.clusters.pluto.tv/v1/stitch/embed/hls/channel/633dc392e0282400071b0d39/master.m3u8?deviceId=channel&deviceModel=web&deviceVersion=1.0&appVersion=1.0&deviceType=rokuChannel&deviceMake=rokuChannel&deviceDNT=1",
        "logo": "",
        "grupo": "Kids",
        "pais": "🇧🇷 Brasil",
        "cors_star": 0,
    },
    # --- TV Aberta, Regionais e Notícias BR ---
    {
        "nome": "RBATV Band Pará HD",
        "url": "https://cdn.live.br1.jmvstream.com/w/LVW-15748/LVW15748_Yed7yzLuRC/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "DW Brasil Notícias",
        "url": "https://dwamdstream102.akamaized.net/hls/live/2015525/dwstream102/index.m3u8",
        "logo": "",
        "grupo": "News",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TV ALMG | MG Brasil",
        "url": "https://streaming.almg.gov.br/live/tvalmg.m3u8",
        "logo": "",
        "grupo": "News",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TV Cultura Pará (Funtelpa)",
        "url": "https://www.portalcultura.com.br/playerhtml/funtelpa/tv_funtelpa/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 0,
    },
    {
        "nome": "TVM Pará [TV Aberta]",
        "url": "https://video09.logicahost.com.br/tvmpara/tvmpara/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Super Marajoara [TV Aberta]",
        "url": "https://tv02.zas.media:1936/supermarajoara/supermarajoara/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TV MAX Rio | Brasil",
        "url": "https://5cf4a2c2512a2.streamlock.net:443/tvmax/tvmax/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TV Candidés",
        "url": "https://cdn.live.br1.jmvstream.com/w/LVW-8067/ngrp:LVW8067_ZffQjxn7UC_all/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Top Mix TV",
        "url": "https://video03.logicahost.com.br/topmixtv/topmixtv/chunklist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TV Ondas Play [Notícias]",
        "url": "https://stmv5.samcast.com.br/portalondasdemarica/portalondasdemarica/playlist.m3u8",
        "logo": "",
        "grupo": "News",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Solive TV",
        "url": "https://stmv6.voxtvhd.com.br/solivetv/solivetv/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TV Canal 72",
        "url": "https://stmv1.voxtvhd.com.br/canal72tv2/canal72tv2/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Elemental Channel",
        "url": "https://stmv1.samcast.com.br/ricardo2194/ricardo2194/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Assim é Portugal | Brasil",
        "url": "https://video04.logicahost.com.br/assimeportugal/assimeportugal/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    # --- Religiosos BR ---
    {
        "nome": "TV Pai Eterno (720p)",
        "url": "https://video09.logicahost.com.br/paieterno/paieterno/playlist.m3u8",
        "logo": "",
        "grupo": "Religious",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TV Igreja Mundial do Poder de Deus",
        "url": "https://stmv7.voxtvhd.com.br/pralan/pralan/playlist.m3u8",
        "logo": "",
        "grupo": "Religious",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TV Adorando Jesus",
        "url": "https://stmv1.srvif.com/tvadorando/tvadorando/playlist.m3u8",
        "logo": "",
        "grupo": "Religious",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Rede Mais Família",
        "url": "https://video09.logicahost.com.br/redefamilia/redefamilia/playlist.m3u8",
        "logo": "",
        "grupo": "Religious",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TV Manancial",
        "url": "https://srv4.zcast.com.br/flavio8792/flavio8792/playlist.m3u8",
        "logo": "",
        "grupo": "Religious",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TV SEPIOL",
        "url": "https://5a57bda70564a.streamlock.net/tvsepiol/tvsepiol.sdp/playlist.m3u8",
        "logo": "",
        "grupo": "Religious",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Gospel Music TV",
        "url": "https://stmv1.srvif.com/gmusic/gmusic/playlist.m3u8",
        "logo": "",
        "grupo": "Religious",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "TOP MIX TV 03 [Religiosos]",
        "url": "https://video01.logicahost.com.br/topmixtvgospelcanal03/topmixtvgospelcanal03/playlist.m3u8",
        "logo": "",
        "grupo": "Religious",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    # --- Portugal / Lusófonos ---
    {
        "nome": "TVI (720p)",
        "url": "https://raw.githubusercontent.com/thomraider12/canaistvpt/main/m3u8s/tvi.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇵🇹 Portugal / Lusófonos",
        "cors_star": 1,
    },
    {
        "nome": "V+ TVI (720p)",
        "url": "https://raw.githubusercontent.com/thomraider12/canaistvpt/main/m3u8s/vmaistvi.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇵🇹 Portugal / Lusófonos",
        "cors_star": 1,
    },
    {
        "nome": "ON TV Portugal",
        "url": "https://5ce9406b73c33.streamlock.net/ONFM/livestream/master.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇵🇹 Portugal / Lusófonos",
        "cors_star": 1,
    },
    {
        "nome": "TV Arapuan (720p)",
        "url": "https://5b7f3c45ab7c2.streamlock.net/arapuan/ngrp:arapuan_all/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "MNTV Brasil",
        "url": "https://www.khuwemultimedia.com/hls/mntv/mntv.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇧🇷 Brasil",
        "cors_star": 1,
    },
    {
        "nome": "Porto Canal (720p)",
        "url": "https://pull-live-156-1.global.ssl.fastly.net/pc5865dc25400thmb-ea6bf03b14fa318f7133/smil:pc1-jhrgyuoqe5865db-68tkgb14fa318f7133f03.smil/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇵🇹 Portugal / Lusófonos",
        "cors_star": 1,
    },
    {
        "nome": "RTP Mundo (576p)",
        "url": "https://n-5-2.eu.cdn-redge.media/livehls/oeu/mt/live/rtp_internacional/live.livx/playlist.m3u8",
        "logo": "",
        "grupo": "General",
        "pais": "🇵🇹 Portugal / Lusófonos",
        "cors_star": 0,
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
    if any(k in g for k in ("relig", "fonte tv", "plenitude", "rit tv", "universal", "terceiro anjo", "gospel", "pai eterno", "igreja", "adorando", "mais fam", "manancial", "sepiol")):
        return "⛪ Religiosos"
    if any(k in g for k in ("encantador", "document", "science", "nature")):
        return "🔬 Discovery & Ciência"
    if any(k in g for k in ("news", "notic", "cnn", "uol", "aratu", "canal 38", "dw brasil", "almg", "ondas")):
        return "📰 Notícias"
    if any(k in g for k in ("kids", "nickelodeon", "cartoon", "infantil", "fox kids", "jetsons", "beyblade", "xtrema")):
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
