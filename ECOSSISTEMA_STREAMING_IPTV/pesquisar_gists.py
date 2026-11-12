import urllib.request
import re
import json

url = "https://gist.github.com/search?q=lista+de+iptv"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        print(f"Página de busca carregada: {len(html)} bytes")
        
        # Encontra identificadores de gists na página
        padrao = re.compile(r'href="(/[a-zA-Z0-9_-]+/[0-9a-f]{20,40})"')
        links = padrao.findall(html)
        unicos = list(dict.fromkeys(links))
        print(f"Total de Gists encontrados nos resultados: {len(unicos)}")
        for g in unicos[:10]:
            print(" -> https://gist.githubusercontent.com" + g + "/raw")
except Exception as e:
    print("Erro na requisição:", e)
