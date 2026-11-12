import urllib.request
import ssl
import time

urls_to_test = [
    ("Las Estrellas (México)", "https://dai.google.com/ssai/event/_e1s_U52SCGL6zTnlTrbVQ/master.m3u8"),
    ("AZ UNO (México)", "https://mdstrm.com/live-stream-playlist/609b243156cca108312822a6.m3u8"),
    ("Señal Colombia", "https://streaming.rtvc.gov.co/TV_Senal_Colombia_live/smil:live.smil/playlist.m3u8"),
    ("TecnoRadio", "https://stream.zeno.fm/qvq7sm8mymzuv.m3u"),
    ("Retro Plus TV (Chile)", "https://tls-cl.cdnz.cl/retroplustvuno/live/playlist.m3u8"),
    ("TecnoTV PHP Token", "http://tecnotv.club/r9jb/phpcode/ssiptv.php?c=ch22&token=tecnotokenplustv230516F&f=.m3u8")
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("Testando amostra de transmissões:")
for name, u in urls_to_test:
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=6) as r:
            ms = int((time.time() - t0) * 1000)
            status = r.status
            print(f"✅ {name}: HTTP {status} | Latência: {ms}ms")
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        print(f"❌ {name}: FALHOU ({e}) | {ms}ms")
