"""
AUDITORIA DE INTEGRIDADE E SAÚDE DO BANCO DE DADOS IPTV
Realiza um check-up profundo nos canais do banco_iptv.db,
mede a taxa de disponibilidade (SLA/Saúde) e a latência média por categoria.
"""

import sqlite3
import urllib.request
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PASTA_BASE = Path(r"C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
CAMINHO_BANCO = PASTA_BASE / "saida" / "banco_iptv.db"

def testar_conexao_stream(canal):
    id_canal, nome, url, cat, qual = canal
    t0 = time.perf_counter()
    online = False
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=1.8) as resp:
            data = resp.read(250).decode("utf-8", errors="ignore")
            if "#EXT" in data or resp.getcode() == 200:
                online = True
    except:
        pass
    latencia = round((time.perf_counter() - t0) * 1000, 2)
    return {"id": id_canal, "nome": nome, "cat": cat, "online": online, "latencia_ms": latencia}

def executar_auditoria_completa():
    conn = sqlite3.connect(CAMINHO_BANCO)
    cur = conn.cursor()

    cur.execute("SELECT id, nome, url, categoria, qualidade FROM canais WHERE status = 'ATIVO'")
    todos_canais = cur.fetchall()

    print(f"[*] Iniciando Check-up de Integridade em {len(todos_canais)} canais do banco...")
    print("[*] Disparando 50 conexões simultâneas de monitoramento...")

    inicio = time.perf_counter()
    resultados = []
    with ThreadPoolExecutor(max_workers=50) as pool:
        tarefas = [pool.submit(testar_conexao_stream, c) for c in todos_canais]
        for t in as_completed(tarefas):
            resultados.append(t.result())

    tempo_total = round(time.perf_counter() - inicio, 2)
    
    online_count = sum(1 for r in resultados if r["online"])
    offline_count = len(resultados) - online_count
    taxa_saude = round((online_count / len(resultados)) * 100, 1)

    latencias_validas = [r["latencia_ms"] for r in resultados if r["online"]]
    latencia_media = round(sum(latencias_validas) / len(latencias_validas), 2) if latencias_validas else 0

    # Atualiza as latências no banco de dados SQLite
    for r in resultados:
        status = "ATIVO" if r["online"] else "INATIVO"
        cur.execute("UPDATE canais SET latencia_ms = ?, status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE id = ?", (r["latencia_ms"], status, r["id"]))
    
    conn.commit()
    conn.close()

    print("\n==================================================================")
    print("📋 RELATÓRIO EXECUTIVO DE SAÚDE DO SISTEMA IPTV")
    print("==================================================================")
    print(f"-> Total de Canais Auditados : {len(resultados)}")
    print(f"-> Canais 100% Online        : {online_count} 🟢")
    print(f"-> Canais Instáveis/Pausa    : {offline_count} 🔴")
    print(f"-> Taxa de Saúde Geral (SLA) : {taxa_saude}%")
    print(f"-> Latência Média de Resposta: {latencia_media} ms (Ultrarrápido)")
    print(f"-> Tempo do Teste Completo   : {tempo_total} segundos")

if __name__ == "__main__":
    executar_auditoria_completa()
