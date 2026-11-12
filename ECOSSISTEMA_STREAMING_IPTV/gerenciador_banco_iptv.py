"""
GERENCIADOR DE BANCO DE DADOS RELACIONAL DE IPTV (SQLITE 3NF)
Módulo de Arquitetura:
1. Cria e gerencia banco de dados relacional SQLite 'banco_iptv.db'.
2. Registra fontes, histórico de auditoria, latência real e resolução.
3. Filtra apenas canais com sinal 100% comprovado (Status = 'ATIVO').
4. Exporta automaticamente a lista higienizada e atualiza o player.
"""

import sqlite3
import urllib.request
import re
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PASTA_BASE = Path(r"C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
PASTA_SAIDA = PASTA_BASE / "saida"
CAMINHO_BANCO = PASTA_SAIDA / "banco_iptv.db"
DESKTOP = Path(r"C:\Users\jonas\Desktop")

def inicializar_banco() -> sqlite3.Connection:
    """Cria as tabelas e índices relacionais no SQLite."""
    conn = sqlite3.connect(CAMINHO_BANCO)
    cursor = conn.cursor()
    
    # 1. Tabela de Fontes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fontes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_fonte TEXT UNIQUE,
            url_fonte TEXT,
            total_canais INTEGER DEFAULT 0,
            canais_vivos INTEGER DEFAULT 0,
            data_verificacao DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Tabela de Canais (Modelagem 3NF com Chave Estrangeira)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS canais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fonte_id INTEGER,
            nome TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            logo TEXT,
            categoria TEXT,
            qualidade TEXT,
            latencia_ms REAL,
            status TEXT CHECK(status IN ('ATIVO', 'INATIVO')),
            data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fonte_id) REFERENCES fontes(id)
        );
    """)

    # 3. Índices de Alta Performance para buscas em < 1ms
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_status_cat ON canais(status, categoria);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_latencia ON canais(latencia_ms);")
    
    conn.commit()
    return conn

def testar_sinal(canal: dict, timeout: float = 2.0) -> dict:
    url = canal["url"]
    inicio = time.perf_counter()
    online = False
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read(250).decode("utf-8", errors="ignore")
            if "#EXT" in data or resp.getcode() == 200:
                online = True
    except:
        pass
    
    latencia = round((time.perf_counter() - inicio) * 1000, 2)
    return {
        **canal,
        "online": online,
        "latencia_ms": latencia,
        "status": "ATIVO" if online else "INATIVO"
    }

def alimentar_banco_com_canais(lista_canais: list, nome_fonte: str, url_fonte: str):
    conn = inicializar_banco()
    cursor = conn.cursor()

    print(f"\n[*] Auditando e inserindo no Banco de Dados: Fonte '{nome_fonte}'...")
    
    # Registra ou atualiza a fonte
    cursor.execute("""
        INSERT INTO fontes (nome_fonte, url_fonte, total_canais, data_verificacao)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(nome_fonte) DO UPDATE SET
            total_canais = excluded.total_canais,
            data_verificacao = CURRENT_TIMESTAMP;
    """, (nome_fonte, url_fonte, len(lista_canais)))
    
    cursor.execute("SELECT id FROM fontes WHERE nome_fonte = ?", (nome_fonte,))
    fonte_id = cursor.fetchone()[0]

    # Validação paralela em lote
    validados = []
    with ThreadPoolExecutor(max_workers=50) as pool:
        tarefas = [pool.submit(testar_sinal, c) for c in lista_canais]
        for t in as_completed(tarefas):
            validados.append(t.result())

    ativos_count = 0
    for c in validados:
        if c["status"] == "ATIVO":
            ativos_count += 1
            
        cursor.execute("""
            INSERT INTO canais (fonte_id, nome, url, logo, categoria, qualidade, latencia_ms, status, data_atualizacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(url) DO UPDATE SET
                latencia_ms = excluded.latencia_ms,
                status = excluded.status,
                qualidade = excluded.qualidade,
                data_atualizacao = CURRENT_TIMESTAMP;
        """, (fonte_id, c["nome"], c["url"], c.get("logo", ""), c.get("categoria", "Geral"), c.get("qualidade", "HD"), c["latencia_ms"], c["status"]))

    cursor.execute("UPDATE fontes SET canais_vivos = ? WHERE id = ?", (ativos_count, fonte_id))
    conn.commit()
    conn.close()

    print(f"[OK] Banco SQLite atualizado! Canais ativos salvos: {ativos_count} de {len(lista_canais)}")

def sincronizar_banco_com_player():
    """Lê apenas os canais com status 'ATIVO' do banco de dados e atualiza o player."""
    conn = inicializar_banco()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, url, logo, categoria, qualidade, latencia_ms
        FROM canais
        WHERE status = 'ATIVO'
        ORDER BY categoria, latencia_ms ASC;
    """)
    linhas = cursor.fetchall()
    conn.close()

    canais_ativos = []
    for r in linhas:
        canais_ativos.append({
            "nome": r[0],
            "url": r[1],
            "logo": r[2],
            "categoria": r[3],
            "qualidade": r[4],
            "latencia_ms": r[5]
        })

    # Atualiza JSON de telemetria
    (PASTA_SAIDA / "servico_iptv_dados.json").write_text(json.dumps(canais_ativos, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Atualiza Lista M3U
    m3u_linhas = ['#EXTM3U name="Banco de Dados IPTV Ouro"', '#EXT-X-VERSION:3']
    for c in canais_ativos:
        m3u_linhas.append(f'#EXTINF:-1 tvg-logo="{c["logo"]}" group-title="{c["categoria"]}",{c["nome"]}')
        m3u_linhas.append(c["url"])

    (PASTA_SAIDA / "servico_iptv_comercial.m3u").write_text("\n".join(m3u_linhas) + "\n", encoding="utf-8")
    (PASTA_SAIDA / "lista_brasil_turbo.m3u").write_text("\n".join(m3u_linhas) + "\n", encoding="utf-8")
    (PASTA_SAIDA / "tv.m3u").write_text("\n".join(m3u_linhas) + "\n", encoding="utf-8")

    print(f"\n[+] Sincronização concluída! {len(canais_ativos)} canais ativos disponíveis no banco de dados.")

if __name__ == "__main__":
    # Carrega os canais já validados da nossa base
    arquivo_atual = PASTA_SAIDA / "servico_iptv_dados.json"
    if arquivo_atual.exists():
        dados = json.loads(arquivo_atual.read_text(encoding="utf-8"))
        alimentar_banco_com_canais(dados, "Rede Oficial Ouro", "https://iptv-org.github.io/iptv/countries/br.m3u")
    sincronizar_banco_com_player()
