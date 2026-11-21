import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}

# Lista de URLs candidatas que encontramos para teste
testes = [
    ("SBT Nacional HD", "https://6836041ea1117.streamlock.net/cverde/cverde/playlist.m3u8"),
    ("SBT Interior HD", "https://cdn.jmvstream.com/w/LVW-10801/LVW10801_Xvg4R0u57n/playlist.m3u8"),
    ("TV Cultura (Fibra Leve)", "http://170.83.16.50/CULTURA/index.m3u8"),
    ("TV Cultura SP Oficial", "https://player-tvcultura.stream.uol.com.br/live/tvcultura.m3u8"),
    ("TV Cultura Fast", "https://fpa-gateway.tvcultura.com.br:8181/memfs/606caef0-a290-413d-9f1f-8fcdb3a73831.m3u8"),
    ("RedeTV! (Fibra Leve)", "http://170.83.16.50/REDE_TV/index.m3u8"),
    ("RecordTV Conquista", "https://tvconquistalrv.duckdns.org:3334/hls/tvconquistalrv.m3u8?ManoTV"),
    ("RecordTV Juara HD", "https://cdn.live.br1.jmvstream.com/w/LVW-10842/LVW10842_513N26MDBL/playlist.m3u8"),
    ("Record News (Fibra Leve)", "http://170.83.16.50/RECORD_NEWS/index.m3u8"),
    ("Record News Samsung", "https://rnw-rn-samsungtvplus.otteravision.com/rnw/rn/rnw_rn.m3u8"),
    ("Band TV RBA", "https://cdn.jmvstream.com/w/LVW-15748/LVW15748_Yed7yzLuRC/playlist.m3u8"),
    ("BandSports (Fibra Leve)", "http://170.83.16.50/BAND_SPORTS/index.m3u8"),
    ("TV Brasil EBC Oficial", "https://tvbrasil-stream.ebc.com.br/index.m3u8"),
    ("Canal Futura (Fibra Leve)", "http://170.83.16.50/FUTURA/index.m3u8"),
    ("TV Gazeta SP", "http://186.219.52.187/gazeta/index.m3u8"),
    ("Rede Brasil HD", "https://redebrasil.nuvemplay.live/hls/stream.m3u8"),
    ("TV Aparecida (Fibra Leve)", "http://170.83.16.50/TV_APARECIDA/index.m3u8"),
    ("Canção Nova (Fibra Leve)", "http://170.83.16.50/CANCAO_NOVA/index.m3u8"),
    ("TV Senado (Fibra Leve)", "http://170.83.16.50/TV_SENADO/index.m3u8"),
    ("TV Justiça (Fibra Leve)", "http://170.83.16.50/TV_JUSTICA/index.m3u8"),
    ("Terra Viva (Fibra Leve)", "http://170.83.16.50/TERRA_VIVA/index.m3u8")
]

print("Validando fluxos HLS:")
for nome, u in testes:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3.5) as resp:
            data = resp.read(200).decode('utf-8', errors='ignore')
            if resp.status == 200 and '#EXTM3U' in data:
                print(f"  [CONFIRMADO 200] {nome:25s} -> {len(data)} bytes lidos")
    except Exception as e:
        print(f"  [ERRO] {nome:25s} -> {e}")
