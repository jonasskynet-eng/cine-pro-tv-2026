"""
COLETOR AUTOMÁTICO E FILTRADOR DE CANAIS GLOBAIS
Baixa listas públicas brutas (imDazui / IPTV-org), filtra canais do Brasil/Lusófonos,
e envia diretamente para o Motor Acelerador de Validação Turbo.
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

# Fontes remotas públicas e abertas de repositórios do GitHub
URLS_LISTAS_PUBLICAS = [
    # Lista organizada de canais abertos do Brasil (IPTV-org / imDazui)
    "https://iptv-org.github.io/iptv/countries/br.m3u",
    # Lista de canais em português
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

def baixar_lista_remota(url: str, timeout: float = 10.0) -> str:
    """Baixa o conteúdo textual de uma lista M3U da internet."""
    print(f"[*] Baixando lista remota: {url} ...")
    requisicao = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
            conteudo = resposta.read().decode('utf-8', errors='ignore')
            print(f"[OK] Download concluído ({round(len(conteudo) / 1024, 1)} KB).")
            return conteudo
    except Exception as e:
        print(f"[FALHA] Não foi possível baixar a lista {url}: {e}")
        return ""

def extrair_canais_m3u(texto_m3u: str) -> list:
    """Extrai canais estruturados a partir do texto de uma lista M3U."""
    canais = []
    urls_vistas = set()

    for match in REGEX_EXTINF.finditer(texto_m3u):
        atributos = match.group('atributos')
        nome = match.group('nome').strip()
        url = match.group('url').strip()

        if url in urls_vistas:
            continue
        urls_vistas.add(url)

        # Extrai logo e categoria se existirem
        match_logo = REGEX_LOGO.search(atributos)
        match_grupo = REGEX_GRUPO.search(atributos)

        logo = match_logo.group(1) if match_logo else ""
        grupo = match_grupo.group(1) if match_grupo else "Geral"

        canais.append({
            "nome": nome,
            "url": url,
            "logo": logo,
            "grupo": grupo
        })

    print(f"[+] Total de canais únicos encontrados no arquivo: {len(canais)}")
    return canais

def testar_fluxo_individual(canal: dict, timeout: float = 2.5) -> dict:
    """Testa a conexão e valida a qualidade real do canal."""
    url = canal["url"]
    inicio = time.perf_counter()
    online = False
    resolucao = "Desconhecida"
    bitrate_kbps = 0
    erro = ""

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
    except urllib.error.HTTPError as e:
        erro = f"HTTP {e.code}"
    except urllib.error.URLError as e:
        erro = f"Rede: {e.reason}"
    except Exception as e:
        erro = str(e)

    latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)

    # Classificação de Qualidade
    if "1080" in resolucao or bitrate_kbps > 2500:
        selo = "FHD (1080p)"
    elif "720" in resolucao or bitrate_kbps > 1500:
        selo = "HD (720p)"
    elif online:
        selo = "SD / Ao Vivo"
    else:
        selo = "Offline"

    return {
        **canal,
        "online": online,
        "latencia_ms": latencia_ms,
        "resolucao": resolucao,
        "bitrate_kbps": bitrate_kbps,
        "selo": selo,
        "erro": erro
    }

def processar_em_massa(canais: list, max_threads: int = 50, limite_amostra: int = 60) -> list:
    """Valida uma lista massiva de canais com alta concorrência."""
    amostra = canais[:limite_amostra] if limite_amostra else canais
    print(f"\n🚀 Iniciando validação concorrente de {len(amostra)} canais com {max_threads} conexões simultâneas...")
    
    validados = []
    inicio = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_threads) as pool:
        tarefas = {pool.submit(testar_fluxo_individual, c): c for c in amostra}
        for t in as_completed(tarefas):
            res = t.result()
            if res["online"]:
                print(f" [🟢 ONLINE] {res['nome']:<26} | {res['selo']:<12} | {res['latencia_ms']} ms")
            validados.append(res)

    tempo_decorrido = round(time.perf_counter() - inicio, 2)
    ativos = [c for c in validados if c["online"]]
    print(f"\n⚡ Concluído em {tempo_decorrido}s!")
    print(f"   -> Canais Ativos Encontrados: {len(ativos)} de {len(validados)}")
    return validados

def exportar_lista_final(canais: list, caminho_m3u: Path):
    """Exporta a lista final filtrada com padrão compatível com lizongying/my-tv."""
    linhas = [
        '#EXTM3U name="Canais Brasil - Otimizados e Testados"',
        '#EXT-X-VERSION:3'
    ]

    ativos = [c for c in canais if c["online"]]
    # Ordena: 1080p primeiro, depois menor latência
    ativos.sort(key=lambda x: (0 if "1080" in x["selo"] else 1, x["latencia_ms"]))

    for c in ativos:
        nome_formatado = f"{c['nome']} [{c['selo']}]"
        linha_inf = f'#EXTINF:-1 tvg-id="{c["nome"]}" tvg-name="{c["nome"]}" tvg-logo="{c["logo"]}" group-title="{c["grupo"]}",{nome_formatado}'
        linhas.append(linha_inf)
        linhas.append(c["url"])

    caminho_m3u.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"[+] Lista M3U final salva em: {caminho_m3u}")

if __name__ == "__main__":
    conteudo_total = ""
    for url in URLS_LISTAS_PUBLICAS:
        conteudo_total += baixar_lista_remota(url) + "\n"

    canais_encontrados = extrair_canais_m3u(conteudo_total)
    if canais_encontrados:
        canais_testados = processar_em_massa(canais_encontrados, max_threads=60, limite_amostra=50)
        exportar_lista_final(canais_testados, PASTA_SAIDA / "lista_brasil_turbo.m3u")
        
        # Salva o arquivo de telemetria
        (PASTA_SAIDA / "telemetria_brasil.json").write_text(
            json.dumps(canais_testados, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
