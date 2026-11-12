import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'
}

novos_candidatos = [
    ("Rede Globo (TV Morena/MS HD)", "https://media2.cdntvms.com.br/tv_morena_dorados/index.m3u8"),
    ("SBT Nacional Satélite (576p)", "https://media.cdntvms.com.br/sbt_sat/index.m3u8"),
    ("SBT Nacional Streamlock (720p)", "https://6836041ea1117.streamlock.net/cverde/cverde/playlist.m3u8"),
    ("Band Nacional Satélite (576p)", "https://media.cdntvms.com.br/band_sat/index.m3u8"),
    ("Record Nacional Satélite (576p)", "https://media.cdntvms.com.br/record_nacional_sat/index.m3u8"),
    ("Rede Brasil HD (1080p)", "https://redebrasil.nuvemplay.live/hls/stream.m3u8"),
    ("TV Cultura Fibra (720p)", "http://170.83.16.50/CULTURA/index.m3u8"),
    ("TV Cultura Oficial SP", "https://player-tvcultura.stream.uol.com.br/live/tvcultura.m3u8"),
    ("TV Cultura Fast", "https://fpa-gateway.tvcultura.com.br:8181/memfs/606caef0-a290-413d-9f1f-8fcdb3a73831.m3u8"),
    ("Rede TV! Fibra (720p)", "http://170.83.16.50/REDE_TV/index.m3u8"),
    ("Canal Futura Fibra (720p)", "http://170.83.16.50/FUTURA/index.m3u8"),
    ("TV Brasil EBC (720p)", "https://tvbrasil-stream.ebc.com.br/index.m3u8"),
    ("TV Gazeta SP (720p)", "http://186.219.52.187/gazeta/index.m3u8"),
    ("Record News Oficial", "https://rnw-rn.otteravision.com/rnw/rn/rnw_rn.m3u8"),
    ("Band TV RBA", "https://cdn.jmvstream.com/w/LVW-15748/LVW15748_Yed7yzLuRC/playlist.m3u8")
]

print("Testando novos candidatos de canais abertos:")
for nome, u in novos_candidatos:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3.5) as resp:
            data = resp.read(256).decode('utf-8', errors='ignore')
            if resp.status == 200 and '#EXTM3U' in data:
                print(f"  [SUCESSO 200 OK] {nome:32s} -> {u}")
            else:
                print(f"  [FALHOU {resp.status}] {nome:32s}")
    except Exception as e:
        print(f"  [ERRO] {nome:32s} -> {e}")
