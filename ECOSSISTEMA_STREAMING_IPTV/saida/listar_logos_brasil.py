import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

# Listar arquivos no repositório tv-logos/countries/brazil via GitHub API
api_url = "https://api.github.com/repos/tv-logo/tv-logos/contents/countries/brazil"
try:
    req = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        nomes = [item['name'] for item in data if 'globo' in item['name'] or 'sbt' in item['name'] or 'record' in item['name'] or 'band' in item['name'] or 'cultura' in item['name'] or 'redetv' in item['name'] or 'futura' in item['name']]
        print("Logos disponíveis no GitHub:")
        for n in nomes:
            print(" ", n)
except Exception as e:
    print("Erro API GitHub:", e)
