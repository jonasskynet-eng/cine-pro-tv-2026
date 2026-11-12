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

url_pagina2 = "https://gist.github.com/search?p=2&q=lista+de+iptv"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

print("[*] Acessando Página 2 do GitHub Gist...")
req = urllib.request.Request(url_pagina2, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
except Exception as e:
    print(f"Erro ao acessar página 2: {e}")
    html = ""

padrao = re.compile(r'href="(/[a-zA-Z0-9_-]+/[0-9a-f]{20,40})"')
links = padrao.findall(html)
gists_p2 = list(dict.fromkeys(links))
print(f"[+] Total de Gists encontrados na Página 2: {len(gists_p2)}")

REGEX_EXTINF = re.compile(
    r'#EXTINF:(?P<duracao>-?\d+)\s*(?P<atributos>.*?),(?P<nome>[^\n\r]+)[\r\n]+(?P<url>http[s]?://[^\s\r\n]+)',
    re.MULTILINE
)
REGEX_LOGO = re.compile(r'tvg-logo="([^"]+)"')
REGEX_GRUPO = re.compile(r'group-title="([^"]+)"')

def categorizar(nome: str, grupo: str) -> str:
    n = nome.lower()
    g = grupo.lower()
    if any(k in n or k in g for k in ["filme", "movie", "cinema", "serie", "ação", "terror", "drama", "adrenalina", "amc", "axn", "suspense", "faroeste", "arnold", "csi", "oblivion"]):
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
    headers_req = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}
    online = False
    try:
        r = urllib.request.Request(url, headers=headers_req)
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            data = resp.read(250).decode("utf-8", errors="ignore")
            if "#EXT" in data or resp.getcode() == 200:
                online = True
    except:
        pass
    
    latencia = round((time.perf_counter() - inicio) * 1000, 2)
    return {**canal, "online": online, "latencia_ms": latencia, "status": "ATIVO" if online else "INATIVO"}

conn = sqlite3.connect(CAMINHO_BANCO)
cur = conn.cursor()

total_novos_ativos = 0

for g in gists_p2:
    partes = g.strip("/").split("/")
    autor = partes[0]
    raw_url = f"https://gist.githubusercontent.com{g}/raw"
    print(f"\n[*] Baixando Gist Página 2: {autor}...")
    
    try:
        r = urllib.request.Request(raw_url, headers=headers)
        with urllib.request.urlopen(r, timeout=6.0) as resp:
            conteudo = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[-] Falha em {autor}: {e}")
        continue

    canais = []
    urls_vistas = set()
    for m in REGEX_EXTINF.finditer(conteudo):
        nome = m.group("nome").strip()
        url_canal = m.group("url").strip()
        if url_canal in urls_vistas:
            continue
        urls_vistas.add(url_canal)
        
        match_logo = REGEX_LOGO.search(m.group("atributos"))
        match_grupo = REGEX_GRUPO.search(m.group("atributos"))
        logo = match_logo.group(1) if match_logo else ""
        grupo = match_grupo.group(1) if match_grupo else ""

        canais.append({
            "nome": nome,
            "url": url_canal,
            "logo": logo,
            "categoria": categorizar(nome, grupo),
            "qualidade": "Full HD" if "1080" in nome else ("HD" if "720" in nome else "Digital")
        })

    print(f" -> Encontrados {len(canais)} canais neste Gist.")
    if not canais:
        continue

    # Registra fonte
    cur.execute("""
        INSERT INTO fontes (nome_fonte, url_fonte, total_canais, data_verificacao)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(nome_fonte) DO UPDATE SET
            total_canais = excluded.total_canais,
            data_verificacao = CURRENT_TIMESTAMP;
    """, (autor + " (P2)", raw_url, len(canais)))

    # Testa os canais
    validados = []
    with ThreadPoolExecutor(max_workers=50) as pool:
        tarefas = [pool.submit(testar_stream, c) for c in canais[:40]]
        for t in as_completed(tarefas):
            validados.append(t.result())

    for c in validados:
        if c["status"] == "ATIVO":
            total_novos_ativos += 1
            print(f"    🟢 [BOM SINAL]: {c['nome']} | Latência: {c['latencia_ms']} ms")
            cur.execute("""
                INSERT INTO canais (nome, url, logo, categoria, qualidade, latencia_ms, status, data_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(url) DO UPDATE SET
                    latencia_ms = excluded.latencia_ms,
                    status = excluded.status,
                    data_atualizacao = CURRENT_TIMESTAMP;
            """, (c["nome"], c["url"], c["logo"], c["categoria"], c["qualidade"], c["latencia_ms"], c["status"]))

    conn.commit()

# Limpeza e sincronização
cur.execute("SELECT COUNT(*) FROM canais WHERE status = 'ATIVO';")
total_ativos_banco = cur.fetchone()[0]

cur.execute("""
    SELECT nome, url, logo, categoria, qualidade, latencia_ms
    FROM canais
    WHERE status = 'ATIVO'
    ORDER BY categoria, latencia_ms ASC;
""")
todos_banco = cur.fetchall()
conn.close()

lista_sinc = []
for r in todos_banco:
    lista_sinc.append({
        "nome": r[0],
        "url": r[1],
        "logo": r[2],
        "categoria": r[3],
        "qualidade": r[4],
        "latencia_ms": r[5]
    })

# Sincroniza index.html e ASSISTIR_TV.html
template_atual = (PASTA_BASE / "saida" / "index.html").read_text(encoding="utf-8")
novo_html = re.sub(r'const canais = \[.*?\];', f'const canais = {json.dumps(lista_sinc, ensure_ascii=False)};', template_atual, flags=re.DOTALL)
novo_html = re.sub(r'<div class="badge">.*?</div>', f'<div class="badge">{len(lista_sinc)} Canais Prontos</div>', novo_html)
novo_html = re.sub(r'<button class="active" onclick="filtrarCategoria\(\'todas\'\)">.*?</button>', f'<button class="active" onclick="filtrarCategoria(\'todas\')">Todas ({len(lista_sinc)})</button>', novo_html)

(PASTA_BASE / "saida" / "index.html").write_text(novo_html, encoding="utf-8")
(DESKTOP / "ASSISTIR_TV.html").write_text(novo_html, encoding="utf-8")

print(f"\n[SUCESSO] Página 2 concluída! Total consolidado no banco: {total_ativos_banco} canais ativos!")
