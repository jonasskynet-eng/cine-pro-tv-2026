import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

logos = [
    "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/sbt-br.png",
    "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-cultura-br.png",
    "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/record-tv-br.png",
    "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/rede-bandeirantes-br.png",
    "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/redetv-br.png",
    "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tv-brasil-br.png",
    "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/canal-futura-br.png"
]

for l in logos:
    try:
        req = urllib.request.Request(l, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
            print(f"[{resp.status}] Logo: {l.split('/')[-1]}")
    except Exception as e:
        print(f"[ERRO] {l.split('/')[-1]}: {e}")
