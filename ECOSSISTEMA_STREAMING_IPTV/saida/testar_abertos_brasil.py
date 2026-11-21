import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'
}

canais_teste = [
    ("TV Globo SP (HD)", "http://170.84.165.204/Globo_HD/index.m3u8"),
    ("Band SP (HD)", "http://170.84.165.204/BAND_HD/index.m3u8"),
    ("Record SP (HD)", "http://170.84.165.204/Record_HD/index.m3u8"),
    ("TV Cultura Fibra", "http://170.83.16.50/CULTURA/index.m3u8"),
    ("TV Cultura SP Oficial", "https://player-tvcultura.stream.uol.com.br/live/tvcultura.m3u8"),
    ("TV Cultura Fast Oficial", "https://fpa-gateway.tvcultura.com.br:8181/memfs/606caef0-a290-413d-9f1f-8fcdb3a73831.m3u8"),
    ("RedeTV! Fibra", "http://170.83.16.50/REDE_TV/index.m3u8"),
    ("Canal Futura Fibra", "http://170.83.16.50/FUTURA/index.m3u8"),
    ("SBT Nacional HD", "https://cdn.live.br1.jmvstream.com/w/LVW-10801/LVW10801_Xvg4R0u57n/chunklist.m3u8"),
    ("SBT Interior HD", "https://cdn.jmvstream.com/w/LVW-10801/LVW10801_Xvg4R0u57n/playlist.m3u8"),
    ("SBT News HD", "https://amg00527-amg00527c5-amgplt0026.playout.now3.amagi.tv/ts-us-1/sbtnews/master.m3u8"),
    ("Record News Oficial", "https://rnw-rn.otteravision.com/rnw/rn/rnw_rn.m3u8"),
    ("Record News Samsung", "https://rnw-rn-samsungtvplus.otteravision.com/rnw/rn/rnw_rn.m3u8"),
    ("TV Brasil EBC", "https://tvbrasil-stream.ebc.com.br/index.m3u8"),
    ("TV Gazeta SP", "http://186.219.52.187/gazeta/index.m3u8"),
    ("Band TV RBA", "https://cdn.jmvstream.com/w/LVW-15748/LVW15748_Yed7yzLuRC/playlist.m3u8"),
    ("BandSports Fibra", "http://170.83.16.50/BAND_SPORTS/index.m3u8"),
    ("TV Aparecida Fibra", "http://170.83.16.50/TV_APARECIDA/index.m3u8"),
    ("Canção Nova Fibra", "http://170.83.16.50/CANCAO_NOVA/index.m3u8"),
    ("TV Senado Fibra", "http://170.83.16.50/TV_SENADO/index.m3u8"),
    ("TV Justiça Fibra", "http://170.83.16.50/TV_JUSTICA/index.m3u8"),
    ("Terra Viva Fibra", "http://170.83.16.50/TERRA_VIVA/index.m3u8")
]

print("Testando canais abertos brasileiros:")
for nome, u in canais_teste:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3.5) as resp:
            data = resp.read(256).decode('utf-8', errors='ignore')
            if resp.status == 200 and '#EXTM3U' in data:
                print(f"  [VIVO] {nome:25s} -> 200 OK ({u})")
            else:
                print(f"  [FALHOU {resp.status}] {nome:25s} -> {u}")
    except Exception as e:
        print(f"  [ERRO] {nome:25s} -> {e}")
