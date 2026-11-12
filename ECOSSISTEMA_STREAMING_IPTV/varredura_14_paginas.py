"""
VARREDOR INDUSTRIAL DAS 14 PÁGINAS DO GITHUB GIST
Busca: https://gist.github.com/search?l=M3U&o=asc&q=lista+de+iptv+&s=stars
Processa da Página 1 até a Página 14, audita com 60 threads e insere canais ativos no SQLite.
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

REGEX_GIST = re.compile(r'href="(/[a-zA-Z0-9_-]+/[0-9a-f]{20,40})"')
REGEX_EXTINF = re.compile(
    r'#EXTINF:(?P<duracao>-?\d+)\s*(?P<atributos>.*?),(?P<nome>[^\n\r]+)[\r\n]+(?P<url>http[s]?://[^\s\r\n]+)',
    re.MULTILINE
)
REGEX_LOGO = re.compile(r'tvg-logo="([^"]+)"')
REGEX_GRUPO = re.compile(r'group-title="([^"]+)"')

def classificar_geografia(nome: str, url: str) -> tuple:
    n = nome.lower()
    u = url.lower()
    if any(k in n or k in u for k in ["portugal", "rtp", "sic", "tvi", "euronews portugal", "euronews pt", ".pt/", "angola", "moçambique"]):
        return ("🇵🇹 Portugal / Lusófonos", "Europa")
    if any(k in n or k in u for k in ["latin america", "español", "espanha", "colombia", "argentina", "mexico", "chile"]):
        return ("🌎 América Latina / Internacional", "América Latina")
    if any(k in n or k in u for k in ["nasa", "bloomberg", "dw", "euronews germany", "al jazeera", "red bull", "global"]):
        return ("🌐 Internacional / Global", "Mundo")
    if any(k in n or k in u for k in ["sp", "são paulo", "sao paulo", "gazeta", "band sp", "globo sp", "sbt sp"]):
        return ("🇧🇷 Brasil", "São Paulo (SP)")
    if any(k in n or k in u for k in ["rj", "rio de janeiro", "globo rj"]):
        return ("🇧🇷 Brasil", "Rio de Janeiro (RJ)")
    if any(k in n or k in u for k in ["paraná", "parana", "catve", "rs", "tve rs", "sc", "sul"]):
        return ("🇧🇷 Brasil", "Região Sul (PR/SC/RS)")
    if any(k in n or k in u for k in ["aratu", "bahia", "ba", "pe", "recife", "ceará", "ceara", "fdr", "nordeste"]):
        return ("🇧🇷 Brasil", "Região Nordeste")
    if any(k in n or k in u for k in ["amazon sat", "amazonia", "go", "sbt go", "goiás", "brasília", "df"]):
        return ("🇧🇷 Brasil", "Norte / Centro-Oeste")
    return ("🇧🇷 Brasil", "Nacional / Geral")

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

def testar_stream(canal: dict, timeout: float = 2.0) -> dict:
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
    return {**canal, "online": online, "latencia_ms": latencia, "status": "ATIVO" if online else "INATIVO"}

def executar_varredura_14_paginas():
    print("==================================================================")
    print("🌐 VARREDURA INDUSTRIAL DAS 14 PÁGINAS DO GITHUB GIST")
    print("==================================================================")

    todos_gists = []
    
    # 1. Coleta os links das 14 páginas de resultados
    for p in range(1, 15):
        url_busca = f"https://gist.github.com/search?l=M3U&o=asc&q=lista+de+iptv+&s=stars&p={p}"
        print(f"[*] Acessando Página {p}/14: {url_busca}")
        try:
            req = urllib.request.Request(url_busca, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                links = REGEX_GIST.findall(html)
                novos = [l for l in links if l not in todos_gists]
                todos_gists.extend(novos)
                print(f"    -> Encontrados {len(novos)} gists novos na Página {p}. (Total acumulado: {len(todos_gists)})")
        except Exception as e:
            print(f"    [-] Erro na Página {p}: {e}")
        time.sleep(0.5)

    print(f"\n[+] Total consolidado de Gists únicos para auditoria: {len(todos_gists)}")

    # 2. Conecta ao banco de dados SQLite
    conn = sqlite3.connect(CAMINHO_BANCO)
    cur = conn.cursor()

    canais_para_testar = []
    urls_vistas = set()

    # Extrai o conteúdo raw de cada Gist
    for i, g in enumerate(todos_gists, 1):
        autor = g.strip("/").split("/")[0]
        raw_url = f"https://gist.githubusercontent.com{g}/raw"
        print(f"[{i}/{len(todos_gists)}] Baixando Gist de: {autor}...")
        try:
            req = urllib.request.Request(raw_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                conteudo = resp.read().decode("utf-8", errors="ignore")
        except:
            continue

        for m in REGEX_EXTINF.finditer(conteudo):
            nome = m.group("nome").strip()
            url_stream = m.group("url").strip()
            if url_stream in urls_vistas:
                continue
            urls_vistas.add(url_stream)

            match_logo = REGEX_LOGO.search(m.group("atributos"))
            match_grupo = REGEX_GRUPO.search(m.group("atributos"))
            logo = match_logo.group(1) if match_logo else ""
            grupo = match_grupo.group(1) if match_grupo else ""

            pais, regiao = classificar_geografia(nome, url_stream)
            categoria = categorizar(nome, grupo)

            canais_para_testar.append({
                "nome": nome,
                "url": url_stream,
                "logo": logo,
                "categoria": categoria,
                "qualidade": "Full HD" if "1080" in nome else ("HD" if "720" in nome else "Digital"),
                "pais": pais,
                "regiao": regiao
            })

    print(f"\n[+] Total de canais brutos extraídos das 14 páginas: {len(canais_para_testar)}")
    print(f"[*] Auditando todos os canais em paralelo com 60 conexões simultâneas...")

    # 3. Teste concorrente massivo
    validados = []
    with ThreadPoolExecutor(max_workers=60) as pool:
        tarefas = [pool.submit(testar_stream, c) for c in canais_para_testar]
        for t in as_completed(tarefas):
            validados.append(t.result())

    # 4. Inserção no banco SQLite
    ativos_adicionados = 0
    for c in validados:
        if c["status"] == "ATIVO":
            ativos_adicionados += 1
            cur.execute("""
                INSERT INTO canais (nome, url, logo, categoria, qualidade, latencia_ms, status, pais, regiao, data_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(url) DO UPDATE SET
                    latencia_ms = excluded.latencia_ms,
                    status = excluded.status,
                    pais = excluded.pais,
                    regiao = excluded.regiao,
                    data_atualizacao = CURRENT_TIMESTAMP;
            """, (c["nome"], c["url"], c["logo"], c["categoria"], c["qualidade"], c["latencia_ms"], c["status"], c["pais"], c["regiao"]))

    conn.commit()

    # Conta o total consolidado ativo
    cur.execute("SELECT COUNT(*) FROM canais WHERE status = 'ATIVO';")
    total_ativos_banco = cur.fetchone()[0]

    cur.execute("""
        SELECT nome, url, logo, categoria, qualidade, latencia_ms, pais, regiao
        FROM canais
        WHERE status = 'ATIVO'
        ORDER BY 
            CASE WHEN pais LIKE '%Brasil%' THEN 1 ELSE 2 END,
            pais, regiao, categoria, nome;
    """)
    todos_banco = cur.fetchall()
    conn.close()

    todos_sinc = []
    for r in todos_banco:
        todos_sinc.append({
            "nome": r[0], "url": r[1], "logo": r[2], "categoria": r[3],
            "qualidade": r[4], "latencia_ms": r[5], "pais": r[6], "regiao": r[7]
        })

    # 5. Atualiza o arquivo de dados JSON e o player na Área de Trabalho
    (PASTA_SAIDA / "servico_iptv_dados.json").write_text(json.dumps(todos_sinc, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Executa a geração do player visual atualizado
    from organizar_geografia_iptv import executar_organizacao
    executar_organizacao()

    print("\n==================================================================")
    print("✅ VARREDURA DAS 14 PÁGINAS CONCLUÍDA COM SUCESSO!")
    print("==================================================================")
    print(f"-> Gists auditados nas 14 páginas : {len(todos_gists)}")
    print(f"-> Novos canais ativos salvos     : {ativos_adicionados}")
    print(f"-> Total consolidado no banco     : {total_ativos_banco} canais ativos")

if __name__ == "__main__":
    executar_varredura_14_paginas()
