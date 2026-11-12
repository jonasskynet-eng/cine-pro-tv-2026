"""
MOTOR ACELERADOR DE IPTV V2 (TURBO & QUALIDADE)
Componentes:
1. Validação Paralela Massiva (50 threads simultâneas - 1.000 canais em segundos).
2. Detecção Real de Qualidade HLS: Analisa manifesto m3u8 para extrair Resolução (1080p, 720p) e Bitrate.
3. Higienizador Regex & Mapeamento de Ícones do fanmingming/live.
4. Exportação Otimizada para o Player lizongying/my-tv.
"""

import os
import re
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PASTA_BASE = Path(__file__).parent
PASTA_SAIDA = PASTA_BASE / "saida"
PASTA_SAIDA.mkdir(exist_ok=True)

URL_BASE_LOGOS = "https://raw.githubusercontent.com/fanmingming/live/main/tv/"

# Padrões Regex para extração de resolução e bitrate em HLS (.m3u8)
REGEX_RESOLUCAO = re.compile(r'RESOLUTION=(\d+x\d+)', re.IGNORECASE)
REGEX_BITRATE = re.compile(r'BANDWIDTH=(\d+)', re.IGNORECASE)

# Lista de fontes públicas e abertas (demonstração de alta velocidade e qualidade)
FONTES_M3U_TESTE = [
    {
        "nome_bruto": "TV Brasil [FHD]",
        "url": "https://tvbrasil-stream.ebc.com.br/hls/tvbrasil/tvbrasil.m3u8",
        "categoria": "Abertos",
        "logo_sugerido": "TVBrasil.png"
    },
    {
        "nome_bruto": "Canal Gov - Oficial HD",
        "url": "https://stream.ebc.com.br/hls/canalgov/canalgov.m3u8",
        "categoria": "Governo",
        "logo_sugerido": "CanalGov.png"
    },
    {
        "nome_bruto": "NASA TV HD (Público)",
        "url": "https://ntv1.akamaized.net/hls/live/2014075/NASA-NTV1-HLS/master.m3u8",
        "categoria": "Ciência e Documentários",
        "logo_sugerido": "NASA.png"
    },
    {
        "nome_bruto": "Red Bull TV Live Sports",
        "url": "https://rbmn-live.akamaized.net/hls/live/590964/BoRB-AT/master.m3u8",
        "categoria": "Esportes",
        "logo_sugerido": "RedBull.png"
    },
    {
        "nome_bruto": "DW Deutsch (Alemanha Internacional)",
        "url": "https://dwamdstream102.akamaized.net/hls/live/2015525/dwstream102/index.m3u8",
        "categoria": "Notícias",
        "logo_sugerido": "DW.png"
    }
]

def higienizar_nome_canal(nome_bruto: str) -> str:
    """Remove caracteres ruidosos, tags desnecessárias e padroniza o nome."""
    limpo = re.sub(r'\[.*?\]|\(.*?\)', '', nome_bruto)
    limpo = re.sub(r'\s+', ' ', limpo).strip()
    return limpo

def analisar_fluxo_hls(url: str, timeout: float = 3.0) -> dict:
    """
    Realiza teste de velocidade, latência e extrai resolução real via manifesto HLS.
    """
    inicio = time.perf_counter()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }
    
    resolucao = "Desconhecida"
    bitrate_kbps = 0
    tamanho_bytes = 0
    online = False
    erro = ""

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            codigo_http = resp.getcode()
            if codigo_http == 200:
                online = True
                # Baixa os primeiros 4KB do manifesto para capturar tags de stream
                bloco = resp.read(4096).decode('utf-8', errors='ignore')
                tamanho_bytes = len(bloco)
                
                # Procura resolução máxima no manifesto
                resolucoes = REGEX_RESOLUCAO.findall(bloco)
                if resolucoes:
                    # Pega a maior resolução disponível
                    resolucao = resolucoes[-1]
                
                bitrates = REGEX_BITRATE.findall(bloco)
                if bitrates:
                    bitrate_kbps = round(max([int(b) for b in bitrates]) / 1000)

    except urllib.error.HTTPError as e:
        erro = f"HTTP {e.code}"
    except urllib.error.URLError as e:
        erro = f"Erro Conexão: {e.reason}"
    except Exception as e:
        erro = str(e)

    latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)
    
    # Classificação de Qualidade
    if "1080" in resolucao or (bitrate_kbps > 2500):
        selo_qualidade = "FHD (1080p)"
    elif "720" in resolucao or (bitrate_kbps > 1500):
        selo_qualidade = "HD (720p)"
    elif online:
        selo_qualidade = "SD / Dinâmico"
    else:
        selo_qualidade = "Offline"

    return {
        "online": online,
        "latencia_ms": latencia_ms,
        "resolucao": resolucao,
        "bitrate_kbps": bitrate_kbps,
        "selo_qualidade": selo_qualidade,
        "erro": erro
    }

def processar_canal(canal: dict) -> dict:
    nome_limpo = higienizar_nome_canal(canal["nome_bruto"])
    analise = analisar_fluxo_hls(canal["url"])
    
    return {
        "nome": nome_limpo,
        "nome_exibicao": f"{nome_limpo} [{analise['selo_qualidade']}]" if analise['online'] else nome_limpo,
        "url": canal["url"],
        "categoria": canal["categoria"],
        "logo": f"{URL_BASE_LOGOS}{canal['logo_sugerido']}",
        **analise
    }

def executar_turbo_pipeline(lista_canais: list, max_concorrencia: int = 50) -> list:
    print(f"\n=======================================================")
    print(f"🚀 INICIANDO PROCESSAMENTO TURBO (Concorrência: {max_concorrencia} threads)")
    print(f"=======================================================\n")
    
    resultados = []
    inicio_geral = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_concorrencia) as pool:
        tarefas = {pool.submit(processar_canal, c): c for c in lista_canais}
        for t in as_completed(tarefas):
            res = t.result()
            status_icone = "🟢 ONLINE" if res["online"] else "🔴 OFFLINE"
            print(f"{status_icone} | {res['nome']:<28} | {res['selo_qualidade']:<12} | {res['latencia_ms']:>6} ms | Bitrate: {res['bitrate_kbps']} kbps")
            resultados.append(res)

    tempo_total = round(time.perf_counter() - inicio_geral, 2)
    print(f"\n⚡ Concluído em {tempo_total}s! Total processado: {len(resultados)} canais.")
    return resultados

def salvar_lista_m3u_otimizada(canais: list, caminho_arquivo: Path):
    """Gera o arquivo M3U pronto para lizongying/my-tv com logos e metadados."""
    linhas = [
        '#EXTM3U name="Canais Otimizados Alta Fidelidade"',
        '#EXT-X-VERSION:3'
    ]
    
    # Filtra apenas online e ordena por menor latência e maior qualidade
    ativos = [c for c in canais if c["online"]]
    ativos.sort(key=lambda x: (0 if "FHD" in x["selo_qualidade"] else 1, x["latencia_ms"]))

    for c in ativos:
        linha_extinf = (
            f'#EXTINF:-1 tvg-id="{c["nome"]}" tvg-name="{c["nome"]}" tvg-logo="{c["logo"]}" '
            f'group-title="{c["categoria"]}",{c["nome_exibicao"]}'
        )
        linhas.append(linha_extinf)
        linhas.append(c["url"])

    caminho_arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"\n📄 Lista M3U Otimizada salva em: {caminho_arquivo}")
    print(f"   -> Canais Ativos Disponíveis: {len(ativos)} de {len(canais)}")

if __name__ == "__main__":
    canais_processados = executar_turbo_pipeline(FONTES_M3U_TESTE)
    salvar_lista_m3u_otimizada(canais_processados, PASTA_SAIDA / "lista_ultra_rapida.m3u")
    
    # Salva relatório de métricas em JSON
    (PASTA_SAIDA / "metricas_performance.json").write_text(
        json.dumps(canais_processados, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"📊 Relatório de Métricas salvo em: {PASTA_SAIDA / 'metricas_performance.json'}")
