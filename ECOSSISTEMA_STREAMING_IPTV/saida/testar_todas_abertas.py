import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

# Testar múltiplos candidatos de emissoras abertas
cands = [
    # GLOBO
    ("Globo SP (Streamlock)", "https://5ad482a77183d.streamlock.net/globosp/globosp/playlist.m3u8"),
    ("Globo RJ (Streamlock)", "https://5ad482a77183d.streamlock.net/globorj/globorj/playlist.m3u8"),
    ("Globo Nacional (Logicahost)", "https://video09.logicahost.com.br/globo/globo/playlist.m3u8"),
    ("Rede Globo (JMV)", "https://cdn.jmvstream.com/w/LVW-10802/LVW10802_Xvg4R0u57n/playlist.m3u8"),
    ("Globo Minas (Streamlock)", "https://5ad482a77183d.streamlock.net/globominas/globominas/playlist.m3u8"),
    # SBT
    ("SBT Nacional HD (Streamlock)", "https://6836041ea1117.streamlock.net/cverde/cverde/playlist.m3u8"),
    ("SBT Interior (JMV)", "https://cdn.jmvstream.com/w/LVW-10801/LVW10801_Xvg4R0u57n/playlist.m3u8"),
    ("SBT Nova Mutum (Logica)", "https://video09.logicahost.com.br/sbtmutum/sbtmutum/playlist.m3u8"),
    ("SBT Rondonopolis (Logica)", "https://video09.logicahost.com.br/sbtroo/sbtroo/playlist.m3u8"),
    ("SBT Cuiaba (Logica)", "https://video09.logicahost.com.br/sbtcuiaba/sbtcuiaba/playlist.m3u8"),
    ("SBT GO (Zoeweb)", "http://tvsd2.zoeweb.tv:1935/tvsd2/smil:tvsd2.smil/playlist.m3u8?wdiptv"),
    # RECORD
    ("RecordTV Conquista", "https://tvconquistalrv.duckdns.org:3334/hls/tvconquistalrv.m3u8?ManoTV"),
    ("RecordTV Juara HD", "https://cdn.live.br1.jmvstream.com/w/LVW-10842/LVW10842_513N26MDBL/playlist.m3u8"),
    ("Record News Oficial", "https://rnw-rn.otteravision.com/rnw/rn/rnw_rn.m3u8"),
    ("Record News Fibra", "http://170.83.16.50/RECORD_NEWS/index.m3u8"),
    # BAND
    ("Band TV RBA", "https://cdn.jmvstream.com/w/LVW-15748/LVW15748_Yed7yzLuRC/playlist.m3u8"),
    ("BandSports Fibra", "http://170.83.16.50/BAND_SPORTS/index.m3u8"),
    ("Band TV Modelo", "https://video09.logicahost.com.br/tvmodelo/tvmodelo/chunklist_w146878062.m3u8"),
    # CULTURA
    ("TV Cultura Fibra", "http://170.83.16.50/CULTURA/index.m3u8"),
    ("TV Cultura Oficial SP", "https://player-tvcultura.stream.uol.com.br/live/tvcultura.m3u8"),
    ("TV Cultura Fast", "https://fpa-gateway.tvcultura.com.br:8181/memfs/606caef0-a290-413d-9f1f-8fcdb3a73831.m3u8"),
    ("TV Cultura Pará", "https://www.portalcultura.com.br/playerhtml/funtelpa/tv_funtelpa/chunklist_w144947531.m3u8"),
    # REDETV & OUTRAS
    ("Rede TV! Fibra", "http://170.83.16.50/REDE_TV/index.m3u8"),
    ("Rede TV! Paraná", "https://tv01.zas.media:1936/redetvparana/redetvparana/playlist.m3u8"),
    ("Rede Brasil HD", "https://redebrasil.nuvemplay.live/hls/stream.m3u8"),
    ("Canal Futura Fibra", "http://170.83.16.50/FUTURA/index.m3u8"),
    ("TV Brasil EBC", "https://tvbrasil-stream.ebc.com.br/index.m3u8"),
    ("TV Gazeta SP", "http://186.219.52.187/gazeta/index.m3u8"),
    ("TV Aparecida Fibra", "http://170.83.16.50/TV_APARECIDA/index.m3u8"),
    ("Canção Nova Fibra", "http://170.83.16.50/CANCAO_NOVA/index.m3u8"),
    ("TV Senado Fibra", "http://170.83.16.50/TV_SENADO/index.m3u8"),
    ("TV Justiça Fibra", "http://170.83.16.50/TV_JUSTICA/index.m3u8"),
    ("Terra Viva Fibra", "http://170.83.16.50/TERRA_VIVA/index.m3u8"),
    ("Canal do Boi Fibra", "http://170.83.16.50/CANAL_DO_BOI/index.m3u8")
]

print("Testando candidatos:")
for nome, u in cands:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
            data = resp.read(256).decode('utf-8', errors='ignore')
            if resp.status == 200 and '#EXTM3U' in data:
                print(f"  [200 OK] {nome:30s} -> {u}")
            else:
                print(f"  [Status {resp.status}] {nome:30s}")
    except Exception as e:
        print(f"  [OFFLINE] {nome:30s}")
