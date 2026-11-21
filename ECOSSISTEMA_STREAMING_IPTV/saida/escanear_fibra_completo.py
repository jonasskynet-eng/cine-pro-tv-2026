import urllib.request
import ssl
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0'}
base = "http://170.83.16.50/"

candidatos = [
    "GLOBO", "TV_GLOBO", "REDE_GLOBO", "GLOBO_SP", "GLOBO_RJ", "GLOBO_MINAS", "GLOBO_DF", "GLOBO_NE",
    "SBT", "TV_SBT", "REDE_SBT", "SBT_SP", "SBT_HD", "SBT_INTERIOR",
    "RECORD", "TV_RECORD", "REDE_RECORD", "RECORD_SP", "RECORD_NEWS", "RECORDTV",
    "BAND", "TV_BAND", "REDE_BAND", "BAND_SP", "BANDEIRANTES", "REDE_BANDEIRANTES",
    "CULTURA", "TV_CULTURA", "REDE_CULTURA",
    "REDETV", "REDE_TV", "TV_REDETV",
    "GAZETA", "TV_GAZETA", "REDE_GAZETA",
    "TV_BRASIL", "TVBRASIL", "EBC",
    "FUTURA", "CANAL_FUTURA",
    "APARECIDA", "TV_APARECIDA", "CANCAO_NOVA", "REDE_VIDA", "RIT", "BOA_VONTADE",
    "TV_ESCOLA", "TV_SENADO", "TV_CAMARA", "JUSTICA", "TV_JUSTICA",
    "TERRA_VIVA", "AGRO_CANAL", "CANAL_DO_BOI", "CANAL_RURAL",
    "CNN_BRASIL", "JOVEM_PAN", "JOVEM_PAN_NEWS", "JP_NEWS",
    "PREMIERE", "PREMIERE_CLUBES", "SPORTV", "SPORTV2", "SPORTV3", "ESPN", "ESPN2", "ESPN4", "FOX_SPORTS",
    "TELECINE_PREMIUM", "TELECINE_ACTION", "TELECINE_TOUCH", "TELECINE_FUN", "TELECINE_PIPOCA", "TELECINE_CULT",
    "MEGAPIX", "CINEMAX", "HBO", "WARNER", "UNIVERSAL", "PARAMOUNT", "STUDIO_UNIVERSAL"
]

def checar(nome):
    url = f"{base}{nome}/index.m3u8"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=2.0) as resp:
            if resp.status == 200:
                body = resp.read(64).decode('utf-8', errors='ignore')
                if '#EXTM3U' in body:
                    return (nome, url, True)
    except Exception:
        pass
    return (nome, url, False)

print("Escaneando canais no servidor 170.83.16.50...")
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(checar, c) for c in candidatos]
    for fut in futures:
        nome, url, ok = fut.result()
        if ok:
            print(f"  --> ENCONTRADO: {nome} ({url})")
