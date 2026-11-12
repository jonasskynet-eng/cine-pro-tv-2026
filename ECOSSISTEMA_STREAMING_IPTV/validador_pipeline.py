"""
PIPELINE DE ENGENHARIA DE STREAMING IPTV
Integração: imDazui (Fontes) -> fanmingming (Ícones/Metadados) -> Validador de Baixa Latência -> Output M3U/JSON
Metodologia: Engenharia modular, sem dependências externas (Python nativo com concurrent.futures).
"""

import re
import urllib.request
import urllib.error
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Configurações do Pipeline
DIRETORIO_SAIDA = Path(__file__).parent / "saida"
DIRETORIO_SAIDA.mkdir(exist_ok=True)

# URL base dos ícones do fanmingming/live
BASE_ICONES_URL = "https://raw.githubusercontent.com/fanmingming/live/main/tv/"

# Amostra de fontes públicas e abertas para teste de validação
FONTES_TESTE = [
    {
        "nome": "TV Brasil",
        "url": "https://tvbrasil-stream.ebc.com.br/hls/tvbrasil/tvbrasil.m3u8",
        "grupo": "Abertos",
        "logo_id": "TVBrasil.png"
    },
    {
        "nome": "Canal Gov",
        "url": "https://stream.ebc.com.br/hls/canalgov/canalgov.m3u8",
        "grupo": "Governo",
        "logo_id": "CanalGov.png"
    },
    {
        "nome": "TV Cultura (Exemplo/Teste)",
        "url": "https://stream.cultura.com.br/hls/aovivo.m3u8",
        "grupo": "Cultura",
        "logo_id": "TVCultura.png"
    }
]

def testar_conectividade_stream(canal: dict, timeout: float = 3.5) -> dict:
    """
    Testa a latência e o status HTTP de uma URL de streaming (HLS / m3u8).
    Retorna o canal enriquecido com latência em milissegundos e status.
    """
    url = canal["url"]
    inicio = time.perf_counter()
    status_codigo = 0
    ativo = False
    mensagem_erro = ""

    requisicao = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*"
        }
    )

    try:
        # Abre conexão com limite de tempo curto para não travar a esteira
        with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
            status_codigo = resposta.getcode()
            # Lê apenas os primeiros 512 bytes para garantir que o manifesto m3u8 começou a baixar
            primeiros_bytes = resposta.read(512)
            if status_codigo == 200 and len(primeiros_bytes) > 0:
                ativo = True
    except urllib.error.HTTPError as e:
        status_codigo = e.code
        mensagem_erro = f"HTTP {e.code}"
    except urllib.error.URLError as e:
        mensagem_erro = f"Falha de Conexão: {e.reason}"
    except Exception as e:
        mensagem_erro = str(e)

    fim = time.perf_counter()
    latencia_ms = round((fim - inicio) * 1000, 2)

    return {
        "nome": canal["nome"],
        "url": canal["url"],
        "grupo": canal["grupo"],
        "logo": f"{BASE_ICONES_URL}{canal['logo_id']}",
        "ativo": ativo,
        "status_codigo": status_codigo,
        "latencia_ms": latencia_ms,
        "erro": mensagem_erro
    }

def executar_pipeline_validacao(lista_canais: list, max_trabalhadores: int = 5) -> list:
    """Executa o teste de múltiplos canais em paralelo via threads."""
    resultados = []
    print(f"[*] Iniciando validação de {len(lista_canais)} canais com {max_trabalhadores} threads concorrentes...")

    with ThreadPoolExecutor(max_workers=max_trabalhadores) as executor:
        tarefas = {executor.submit(testar_conectividade_stream, c): c for c in lista_canais}
        for tarefa in as_completed(tarefas):
            res = tarefa.result()
            estado = "ONLINE [OK]" if res["ativo"] else "OFFLINE [FALHA]"
            print(f" -> {res['nome']:<25} | {estado:<15} | Latência: {res['latencia_ms']} ms")
            resultados.append(res)

    return resultados

def exportar_m3u_higienizada(canais_validados: list, caminho_arquivo: Path):
    """Gera o arquivo de lista M3U padrão formatado com logos e grupos para o player lizongying/my-tv."""
    linhas = ["#EXTM3U name=\"Lista Filtrada de Baixa Latencia\""]
    
    # Ordena pelos canais ativos com menor latência
    canais_ordenados = sorted(
        [c for c in canais_validados if c["ativo"]],
        key=lambda x: x["latencia_ms"]
    )

    for c in canais_ordenados:
        cabecalho = f'#EXTINF:-1 tvg-name="{c["nome"]}" tvg-logo="{c["logo"]}" group-title="{c["grupo"]}",{c["nome"]}'
        linhas.append(cabecalho)
        linhas.append(c["url"])

    conteudo = "\n".join(linhas) + "\n"
    caminho_arquivo.write_text(conteudo, encoding="utf-8")
    print(f"[+] Lista M3U gerada com sucesso em: {caminho_arquivo} ({len(canais_ordenados)} canais ativos)")

def exportar_relatorio_json(canais: list, caminho_arquivo: Path):
    """Gera relatório de telemetria completo em JSON."""
    caminho_arquivo.write_text(json.dumps(canais, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Relatório de telemetria salvo em: {caminho_arquivo}")

if __name__ == "__main__":
    resultado = executar_pipeline_validacao(FONTES_TESTE)
    exportar_m3u_higienizada(resultado, DIRETORIO_SAIDA / "lista_validada.m3u")
    exportar_relatorio_json(resultado, DIRETORIO_SAIDA / "telemetria_canais.json")
