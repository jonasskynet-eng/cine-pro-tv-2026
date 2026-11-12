"""
GERADOR DE SERVIÇO COMERCIAL DE IPTV (INTEGRAÇÃO AUTOMÁTICA GITHUB TOP 10)
Fontes: imDazui + IPTV-org + fanmingming
1. Baixa listas verificadas com links dinâmicos atualizados.
2. Categoriza automaticamente canais em: Filmes e Séries, Desenhos, Esportes, Notícias e Cultura.
3. Valida canais ativos em paralelo com 60 conexões concorrentes.
4. Gera a lista comercial e atualiza o servidor local na hora.
"""

import urllib.request
import urllib.error
import re
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PASTA_BASE = Path(__file__).parent
PASTA_SAIDA = PASTA_BASE / "saida"
PASTA_SAIDA.mkdir(exist_ok=True)

FONTES_REMOTAS = [
    "https://iptv-org.github.io/iptv/countries/br.m3u",
    "https://iptv-org.github.io/iptv/languages/por.m3u"
]

URL_BASE_LOGOS = "https://raw.githubusercontent.com/fanmingming/live/main/tv/"

REGEX_EXTINF = re.compile(
    r'#EXTINF:(?P<duracao>-?\d+)\s*(?P<atributos>.*?),(?P<nome>[^\n\r]+)[\r\n]+(?P<url>http[s]?://[^\s\r\n]+)',
    re.MULTILINE
)
REGEX_LOGO = re.compile(r'tvg-logo="([^"]+)"')
REGEX_GRUPO = re.compile(r'group-title="([^"]+)"')
REGEX_RESOLUCAO = re.compile(r'RESOLUTION=(\d+x\d+)', re.IGNORECASE)
REGEX_BITRATE = re.compile(r'BANDWIDTH=(\d+)', re.IGNORECASE)

def categorizar_canal(nome: str, grupo_original: str) -> str:
    """Classifica o canal em categorias comerciais padronizadas."""
    n = nome.lower()
    g = grupo_original.lower()
    
    if any(k in n or k in g for k in ["filme", "movie", "cinema", "serie", "ação", "terror", "drama", "adrenalina", "amc", "axn", "paramount"]):
        return "🎬 Filmes e Séries"
    elif any(k in n or k in g for k in ["kids", "desenho", "infantil", "bob esponja", "avatar", "anime", "baby", "cartoon", "nickelodeon", "toor"]):
        return "👶 Desenhos e Infantil"
    elif any(k in n or k in g for k in ["esporte", "sport", "futebol", "rural", "red bull", "corrida", "combat", "fight"]):
        return "⚽ Esportes"
    elif any(k in n or k in g for k in ["news", "notícia", "noticia", "jornal", "uol", "cnn", "bm&c", "euronews", "dw", "record"]):
        return "📰 Notícias"
    elif any(k in n or k in g for k in ["music", "música", "musica", "clip", "show", "rock", "pop"]):
        return "🎵 Música"
    else:
        return "🌎 Variedades e Cultura"

def testar_stream(canal: dict, timeout: float = 2.5) -> dict:
    url = canal["url"]
    inicio = time.perf_counter()
    online = False
    resolucao = "Desconhecida"
    bitrate_kbps = 0

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.getcode() == 200:
                online = True
                bloco = resp.read(2048).decode('utf-8', errors='ignore')
                resolucoes = REGEX_RESOLUCAO.findall(bloco)
                if resolucoes:
                    resolucao = resolucoes[-1]
                bitrates = REGEX_BITRATE.findall(bloco)
                if bitrates:
                    bitrate_kbps = round(max([int(b) for b in bitrates]) / 1000)
    except Exception:
        pass

    latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)

    if "1080" in resolucao or bitrate_kbps > 2500:
        qualidade = "Full HD (1080p)"
    elif "720" in resolucao or bitrate_kbps > 1500:
        qualidade = "HD (720p)"
    elif online:
        qualidade = "Digital Ao Vivo"
    else:
        qualidade = "Inativo"

    return {
        **canal,
        "online": online,
        "latencia_ms": latencia_ms,
        "resolucao": resolucao,
        "bitrate_kbps": bitrate_kbps,
        "qualidade": qualidade
    }

def executar_gerador_servico(max_amostra: int = 80):
    print("==================================================================")
    print("💎 CONSTRUINDO SERVIÇO COMERCIAL DE IPTV")
    print("==================================================================")
    
    conteudo = ""
    for url in FONTES_REMOTAS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                conteudo += resp.read().decode('utf-8', errors='ignore') + "\n"
        except Exception as e:
            print(f"[!] Erro ao baixar {url}: {e}")

    canais_brutos = []
    urls_vistas = set()

    for match in REGEX_EXTINF.finditer(conteudo):
        atributos = match.group('atributos')
        nome = match.group('nome').strip()
        url = match.group('url').strip()

        if url in urls_vistas:
            continue
        urls_vistas.add(url)

        match_logo = REGEX_LOGO.search(atributos)
        match_grupo = REGEX_GRUPO.search(atributos)

        logo = match_logo.group(1) if match_logo else ""
        grupo_orig = match_grupo.group(1) if match_grupo else "Geral"
        categoria_comercial = categorizar_canal(nome, grupo_orig)

        canais_brutos.append({
            "nome": nome,
            "url": url,
            "logo": logo,
            "categoria": categoria_comercial
        })

    amostra = canais_brutos[:max_amostra]
    print(f"[*] Testando e auditando {len(amostra)} canais com 60 threads simultâneas...")

    validados = []
    with ThreadPoolExecutor(max_workers=60) as pool:
        tarefas = {pool.submit(testar_stream, c): c for c in amostra}
        for t in as_completed(tarefas):
            res = t.result()
            if res["online"]:
                print(f" 🟢 [{res['categoria']:<22}] {res['nome']:<28} | {res['qualidade']:<15} | {res['latencia_ms']} ms")
            validados.append(res)

    ativos = [c for c in validados if c["online"]]
    ativos.sort(key=lambda x: (x["categoria"], x["nome"]))

    print(f"\n⚡ Total de canais comerciais ativos: {len(ativos)} de {len(amostra)}")

    # GERAÇÃO DA LISTA M3U COMERCIAL
    linhas_m3u = [
        '#EXTM3U name="Serviço Comercial IPTV Brasil"',
        '#EXT-X-VERSION:3'
    ]
    for c in ativos:
        nome_completo = f"{c['nome']} [{c['qualidade']}]"
        linha_inf = f'#EXTINF:-1 tvg-id="{c["nome"]}" tvg-name="{c["nome"]}" tvg-logo="{c["logo"]}" group-title="{c["categoria"]}",{nome_completo}'
        linhas_m3u.append(linha_inf)
        linhas_m3u.append(c["url"])

    texto_final = "\n".join(linhas_m3u) + "\n"

    # Salva nos destinos do ecossistema
    (PASTA_SAIDA / "servico_iptv_comercial.m3u").write_text(texto_final, encoding="utf-8")
    (PASTA_SAIDA / "lista_brasil_turbo.m3u").write_text(texto_final, encoding="utf-8")
    (PASTA_SAIDA / "tv.m3u").write_text(texto_final, encoding="utf-8")
    (PASTA_SAIDA / "servico_iptv_dados.json").write_text(json.dumps(ativos, indent=2, ensure_ascii=False), encoding="utf-8")

    print("[+] Arquivos M3U e banco JSON atualizados com sucesso em 'saida/'!")

if __name__ == "__main__":
    executar_gerador_servico(max_amostra=100)
