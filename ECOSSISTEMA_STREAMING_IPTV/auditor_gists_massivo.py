"""
AUDITOR MASSIVO DE GISTS DO GITHUB PARA O BANCO DE DADOS
Varre os 10 Gists encontrados, extrai canais, testa conectividade com 60 threads,
armazena os canais com bom sinal no SQLite banco_iptv.db e atualiza o player.
"""

import urllib.request
import re
import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PASTA_BASE = Path(r"C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
PASTA_SAIDA = PASTA_BASE / "saida"
CAMINHO_BANCO = PASTA_SAIDA / "banco_iptv.db"
DESKTOP = Path(r"C:\Users\jonas\Desktop")

GISTS_ALVO = [
    ("inoxentmohsin1", "https://gist.githubusercontent.com/inoxentmohsin1/c7ffc1837bf122eb5a041b653e3a5b03/raw"),
    ("Srpinho", "https://gist.githubusercontent.com/Srpinho/42268b955153be2bc10ecd54c33883aa/raw"),
    ("j0avw", "https://gist.githubusercontent.com/j0avw/55330c453dff55f91fd1902b74e92e95/raw"),
    ("rei1401", "https://gist.githubusercontent.com/rei1401/28121cc2f605b67cc56bbdd59814b6b3/raw"),
    ("emmanuels9-del", "https://gist.githubusercontent.com/emmanuels9-del/7c32f8bb7b209a93b35e0a53b40c6fef/raw"),
    ("lgtec", "https://gist.githubusercontent.com/lgtec/e854a0780541c150ca8a083af6085523/raw"),
    ("isamac", "https://gist.githubusercontent.com/isamac/d584462bab318cee9fd33a3cd87d6117/raw"),
    ("marciogif", "https://gist.githubusercontent.com/marciogif/db41af9bd84396d703c11c900ee8e26d/raw")
]

REGEX_EXTINF = re.compile(
    r'#EXTINF:(?P<duracao>-?\d+)\s*(?P<atributos>.*?),(?P<nome>[^\n\r]+)[\r\n]+(?P<url>http[s]?://[^\s\r\n]+)',
    re.MULTILINE
)
REGEX_LOGO = re.compile(r'tvg-logo="([^"]+)"')
REGEX_GRUPO = re.compile(r'group-title="([^"]+)"')

def categorizar(nome: str, grupo: str) -> str:
    n = nome.lower()
    g = grupo.lower()
    if any(k in n or k in g for k in ["filme", "movie", "cinema", "serie", "ação", "terror", "drama", "adrenalina", "amc", "axn", "suspense", "faroeste", "arnold", "csi"]):
        return "🎬 Filmes e Séries"
    elif any(k in n or k in g for k in ["kids", "desenho", "infantil", "bob", "avatar", "anime", "cartoon", "baby", "cartoon", "tokusatsu", "pica"]):
        return "👶 Desenhos 24h"
    elif any(k in n or k in g for k in ["esporte", "sport", "futebol", "rural", "red bull", "fifa", "caze", "espn"]):
        return "⚽ Esportes"
    elif any(k in n or k in g for k in ["news", "notícia", "noticia", "jornal", "uol", "cnn", "bm&c", "aratu", "dw", "record"]):
        return "📰 Notícias"
    elif any(k in n or k in g for k in ["music", "música", "musica", "clip", "rock", "pop", "fm", "hit", "radio", "rádio"]):
        return "🎵 Música e Shows"
    else:
        return "🌎 Variedades e TV Aberta"

def testar_canal(canal: dict, timeout: float = 2.0) -> dict:
    url = canal["url"]
    inicio = time.perf_counter()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}
    online = False
    try:
        req = urllib.request.Request(url, headers=headers)
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

def processar_todos_os_gists():
    conn = sqlite3.connect(CAMINHO_BANCO)
    cur = conn.cursor()

    total_novos_encontrados = 0
    total_ativos_salvos = 0

    print("==================================================================")
    print("🔍 AUDITORIA COMPLETA DE GISTS DO GITHUB PARA O BANCO DE DADOS")
    print("==================================================================")

    for autor, url_gist in GISTS_ALVO:
        print(f"\n[*] Baixando Gist de: '{autor}'...")
        try:
            req = urllib.request.Request(url_gist, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                conteudo = resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"[-] Falha ao acessar {autor}: {e}")
            continue

        canais_gist = []
        urls_vistas = set()

        for m in REGEX_EXTINF.finditer(conteudo):
            atributos = m.group("atributos")
            nome = m.group("nome").strip()
            url_stream = m.group("url").strip()

            if url_stream in urls_vistas:
                continue
            urls_vistas.add(url_stream)

            match_logo = REGEX_LOGO.search(atributos)
            match_grupo = REGEX_GRUPO.search(atributos)
            logo = match_logo.group(1) if match_logo else ""
            grupo = match_grupo.group(1) if match_grupo else ""

            canais_gist.append({
                "nome": nome,
                "url": url_stream,
                "logo": logo,
                "categoria": categorizar(nome, grupo),
                "qualidade": "Full HD" if "1080" in nome else ("HD" if "720" in nome else "Digital")
            })

        print(f" -> Encontrados {len(canais_gist)} canais brutos neste Gist.")
        total_novos_encontrados += len(canais_gist)

        if not canais_gist:
            continue

        # Registra fonte no banco
        cur.execute("""
            INSERT INTO fontes (nome_fonte, url_fonte, total_canais, data_verificacao)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(nome_fonte) DO UPDATE SET
                total_canais = excluded.total_canais,
                data_verificacao = CURRENT_TIMESTAMP;
        """, (autor, url_gist, len(canais_gist)))
        cur.execute("SELECT id FROM fontes WHERE nome_fonte = ?", (autor,))
        fonte_id = cur.fetchone()[0]

        # Testa os canais em lote
        validados = []
        with ThreadPoolExecutor(max_workers=50) as pool:
            tarefas = [pool.submit(testar_canal, c) for c in canais_gist[:50]]
            for t in as_completed(tarefas):
                validados.append(t.result())

        ativos_fonte = 0
        for c in validados:
            if c["status"] == "ATIVO":
                ativos_fonte += 1
                total_ativos_salvos += 1
                print(f"    🟢 [BOM SINAL]: {c['nome']} | Latência: {c['latencia_ms']} ms")

            # Salva no banco de dados
            cur.execute("""
                INSERT INTO canais (fonte_id, nome, url, logo, categoria, qualidade, latencia_ms, status, data_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(url) DO UPDATE SET
                    latencia_ms = excluded.latencia_ms,
                    status = excluded.status,
                    data_atualizacao = CURRENT_TIMESTAMP;
            """, (fonte_id, c["nome"], c["url"], c["logo"], c["categoria"], c["qualidade"], c["latencia_ms"], c["status"]))

        cur.execute("UPDATE fontes SET canais_vivos = ? WHERE id = ?", (ativos_fonte, fonte_id))
        conn.commit()

    conn.close()

    print("\n==================================================================")
    print("📊 SINCRONIZANDO BANCO DE DADOS COM O PLAYER VISUAL...")
    print("==================================================================")
    
    # Executa a sincronização do banco
    from gerenciador_banco_iptv import sincronizar_banco_com_player
    sincronizar_banco_com_player()

if __name__ == "__main__":
    processar_todos_os_gists()
