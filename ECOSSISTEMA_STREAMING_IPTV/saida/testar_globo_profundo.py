import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

globo_cands = [
    "http://200.77.176.130:8000/udp/224.0.0.1:49152",
    "http://tv01.zas.media:1936/globo/globo/playlist.m3u8",
    "http://tvsd2.zoeweb.tv:1935/globo/smil:globo.smil/playlist.m3u8",
    "https://cdn.jmvstream.com/w/LVW-10800/LVW10800_Xvg4R0u57n/playlist.m3u8",
    "https://6836041ea1117.streamlock.net/globo/globo/playlist.m3u8",
    "https://s1.tvr.ovh/video83070/globo/playlist.m3u8",
    "http://170.83.16.50/GLOBO/index.m3u8",
    "http://170.83.16.50/TVGLOBO/index.m3u8",
    "http://170.83.16.50/REDEGLOBO/index.m3u8",
    "http://170.83.16.50/GLOBO_HD/index.m3u8",
    "http://170.83.16.50/RBS/index.m3u8",
    "http://170.83.16.50/RBS_TV/index.m3u8",
    "http://170.83.16.50/RPC/index.m3u8",
    "http://170.83.16.50/EPTV/index.m3u8"
]

print("Testando rotas adicionais de Globo:")
for u in globo_cands:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=2.5) as resp:
            data = resp.read(128).decode('utf-8', errors='ignore')
            if resp.status == 200 and '#EXTM3U' in data:
                print(f"  [SUCESSO GLOBO 200] {u}")
            else:
                print(f"  [Status {resp.status}] {u}")
    except Exception as e:
        # print(f"  [ERRO] {u}: {e}")
        pass
