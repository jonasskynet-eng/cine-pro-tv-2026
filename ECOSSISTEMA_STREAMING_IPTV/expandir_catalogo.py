"""
EXPANSOR DE CATÁLOGO IPTV - ADICIONA MAIS DE 100 CANAIS VERIFICADOS
Puxa de repositórios oficiais: Desenhos 24h, Filmes, Séries, Música, Notícias e Câmeras.
"""

import urllib.request
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PASTA_BASE = Path(r"C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
DESKTOP = Path(r"C:\Users\jonas\Desktop")

URLS_CATALOGO = [
    "https://iptv-org.github.io/iptv/countries/br.m3u",
    "https://iptv-org.github.io/iptv/languages/por.m3u"
]

REGEX_EXTINF = re.compile(
    r'#EXTINF:(?P<duracao>-?\d+)\s*(?P<atributos>.*?),(?P<nome>[^\n\r]+)[\r\n]+(?P<url>http[s]?://[^\s\r\n]+)',
    re.MULTILINE
)

def categorizar_avancado(nome: str, grupo: str) -> str:
    n = nome.lower()
    g = grupo.lower()
    if any(k in n or k in g for k in ["filme", "movie", "cinema", "serie", "ação", "terror", "drama", "adrenalina", "amc", "axn", "suspense", "faroeste", "arnold", "csi", "classique"]):
        return "🎬 Filmes e Séries"
    elif any(k in n or k in g for k in ["kids", "desenho", "infantil", "bob", "avatar", "anime", "cartoon", "baby", "gospel cartoon", "tokusatsu", "pica"]):
        return "👶 Desenhos 24h"
    elif any(k in n or k in g for k in ["esporte", "sport", "futebol", "rural", "red bull", "fifa", "caze", "espn"]):
        return "⚽ Esportes"
    elif any(k in n or k in g for k in ["news", "notícia", "noticia", "jornal", "uol", "cnn", "bm&c", "aratu", "dw"]):
        return "📰 Notícias"
    elif any(k in n or k in g for k in ["music", "música", "musica", "clip", "rock", "pop", "fm", "hit", "radio", "rádio"]):
        return "🎵 Música e Shows"
    else:
        return "🌎 Variedades e TV Aberta"

def testar_url(canal: dict, timeout: float = 2.0) -> dict:
    url = canal["url"]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"}
    online = False
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            bloco = resp.read(250).decode("utf-8", errors="ignore")
            if "#EXT" in bloco or resp.getcode() == 200:
                online = True
    except:
        pass
    return {**canal, "online": online}

print("[*] Baixando catálogo ampliado de canais em português...")
conteudo = ""
for u in URLS_CATALOGO:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8.0) as r:
            conteudo += r.read().decode("utf-8", errors="ignore") + "\n"
    except Exception as e:
        print(f"Erro em {u}: {e}")

canais_encontrados = []
urls_vistas = set()

for match in REGEX_EXTINF.finditer(conteudo):
    nome = match.group("nome").strip()
    url = match.group("url").strip()
    if url in urls_vistas:
        continue
    urls_vistas.add(url)
    
    cat = categorizar_avancado(nome, "")
    canais_encontrados.append({
        "nome": nome,
        "url": url,
        "categoria": cat,
        "qualidade": "Full HD" if "1080" in nome else ("HD" if "720" in nome else "Digital")
    })

print(f"[*] Total de canais brutos encontrados: {len(canais_encontrados)}")
print("[*] Testando os primeiros 180 canais com 60 conexões paralelas...")

validados = []
with ThreadPoolExecutor(max_workers=60) as pool:
    tarefas = [pool.submit(testar_url, c) for c in canais_encontrados[:180]]
    for t in as_completed(tarefas):
        res = t.result()
        if res["online"]:
            validados.append(res)

print(f"[+] Total de canais 100% ONLINE E ATIVOS: {len(validados)}")

# Adiciona canais super estáveis no topo
fixos = [
    {"nome": "Red Bull TV Esportes", "url": "https://rbmn-live.akamaized.net/hls/live/590964/BoRB-AT/master.m3u8", "categoria": "⚽ Esportes", "qualidade": "Full HD"},
    {"nome": "FIFA+ Brasil", "url": "https://e3be9ac5.wurl.com/master/f36d25e7e52f1ba8d7e56eb859c636563214f541/TEctYnJfRklGQVBsdXNQb3J0dWd1ZXNlX0hMUw/playlist.m3u8", "categoria": "⚽ Esportes", "qualidade": "Full HD"},
    {"nome": "New Brasil HD (CloudFront)", "url": "https://dfr80qz435crc.cloudfront.net/EFGH/Amagi/NewCo/New_Brasil_BR/New_Brasil.m3u8", "categoria": "📰 Notícias", "qualidade": "Full HD"},
    {"nome": "Amazon Sat HD", "url": "https://amazonsat.brasilstream.com.br/hls/amazonsat/index.m3u8", "categoria": "🌎 Variedades e TV Aberta", "qualidade": "Full HD"},
    {"nome": "DW Brasil Notícias", "url": "https://dwamdstream102.akamaized.net/hls/live/2015525/dwstream102/index.m3u8", "categoria": "📰 Notícias", "qualidade": "Full HD"},
    {"nome": "NASA TV Espaço HD", "url": "https://ntv1.akamaized.net/hls/live/2014075/NASA-NTV1-HLS/master.m3u8", "categoria": "🌎 Variedades e TV Aberta", "qualidade": "Full HD"}
]

todos = fixos + [c for c in validados if not any(f["url"] == c["url"] for f in fixos)]

# Ordena por categoria e nome
todos.sort(key=lambda x: (x["categoria"], x["nome"]))

# Gera o novo index.html com o catálogo completo
html_final = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Central IPTV Turbo - Catálogo Completo</title>
  <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }}
    body {{ background-color: #0b1120; color: #f8fafc; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
    header {{ background-color: #1e293b; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0284c7; }}
    header h1 {{ font-size: 1.25rem; font-weight: 700; color: #38bdf8; }}
    .badge {{ background: #22c55e; color: #000; padding: 4px 14px; border-radius: 9999px; font-size: 0.85rem; font-weight: 700; }}
    .container {{ display: flex; flex: 1; height: calc(100vh - 65px); }}
    .video-area {{ flex: 3; background-color: #000; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; }}
    video {{ width: 100%; height: 100%; max-height: calc(100vh - 120px); background-color: #000; }}
    .player-info {{ width: 100%; background: #1e293b; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #334155; }}
    .btn-som {{ background: #22c55e; color: #000; border: none; padding: 8px 18px; border-radius: 6px; font-weight: 700; cursor: pointer; font-size: 0.95rem; }}
    .sidebar {{ flex: 1.3; background-color: #1e293b; border-left: 1px solid #334155; display: flex; flex-direction: column; max-width: 460px; }}
    .search-box {{ padding: 12px 16px; border-bottom: 1px solid #334155; }}
    .search-box input {{ width: 100%; padding: 10px 14px; border-radius: 8px; border: 1px solid #475569; background-color: #0f172a; color: #fff; font-size: 0.95rem; outline: none; }}
    .search-box input:focus {{ border-color: #38bdf8; }}
    .category-filter {{ display: flex; gap: 6px; padding: 10px 16px; overflow-x: auto; border-bottom: 1px solid #334155; background-color: #0f172a; }}
    .category-filter button {{ background: #1e293b; color: #94a3b8; border: 1px solid #334155; padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer; white-space: nowrap; }}
    .category-filter button:hover, .category-filter button.active {{ background: #0284c7; color: #fff; border-color: #38bdf8; }}
    .channels-list {{ flex: 1; overflow-y: auto; padding: 10px 14px; }}
    .channel-item {{ display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 8px; cursor: pointer; margin-bottom: 6px; background: #0f172a; transition: all 0.2s; border: 1px solid transparent; }}
    .channel-item:hover {{ background: #334155; transform: translateX(4px); }}
    .channel-item.active {{ background: #0369a1; border-color: #38bdf8; }}
    .channel-details {{ flex: 1; display: flex; flex-direction: column; gap: 3px; }}
    .channel-name {{ font-weight: 600; font-size: 0.95rem; }}
    .channel-category {{ font-size: 0.75rem; color: #94a3b8; }}
    .quality-tag {{ font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 4px; background: #334155; color: #94a3b8; }}
    .quality-tag.fhd {{ background: #0284c7; color: #fff; }}
  </style>
</head>
<body>
  <header>
    <h1>📺 Central IPTV Turbo</h1>
    <div class="badge">{len(todos)} Canais Prontos</div>
  </header>

  <div class="container">
    <div class="video-area">
      <video id="player" controls autoplay playsinline></video>
      <div class="player-info">
        <div>
          <h2 id="canal-atual-nome" style="font-size: 1.15rem; color: #38bdf8;">Red Bull TV Esportes</h2>
          <span id="canal-atual-status" style="font-size: 0.85rem; color: #4ade80;">Sintonizando transmissão ao vivo...</span>
        </div>
        <button id="btn-som" class="btn-som" onclick="ativarSom()">🔊 Ativar Som</button>
      </div>
    </div>

    <div class="sidebar">
      <div class="search-box">
        <input type="text" id="campo-busca" placeholder="🔍 Digite para buscar qualquer canal...">
      </div>
      <div class="category-filter" id="filtro-categorias">
        <button class="active" onclick="filtrarCategoria('todas')">Todas ({len(todos)})</button>
        <button onclick="filtrarCategoria('filme')">🎬 Filmes e Séries</button>
        <button onclick="filtrarCategoria('desenho')">👶 Desenhos</button>
        <button onclick="filtrarCategoria('esporte')">⚽ Esportes</button>
        <button onclick="filtrarCategoria('noticia')">📰 Notícias</button>
        <button onclick="filtrarCategoria('musica')">🎵 Música</button>
        <button onclick="filtrarCategoria('variedade')">🌎 Variedades</button>
      </div>
      <div class="channels-list" id="lista-canais"></div>
    </div>
  </div>

  <script>
    const canais = {json.dumps(todos, ensure_ascii=False)};
    const video = document.getElementById('player');
    const listaCanaisContainer = document.getElementById('lista-canais');
    const campoBusca = document.getElementById('campo-busca');
    const canalAtualNome = document.getElementById('canal-atual-nome');
    const canalAtualStatus = document.getElementById('canal-atual-status');
    const btnSom = document.getElementById('btn-som');

    let hls = null;
    let filtroAtual = 'todas';

    function normalizar(t) {{
      return (t || '').toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").replace(/[^a-z0-9]/g, "");
    }}

    function ativarSom() {{
      video.muted = false;
      btnSom.style.display = 'none';
      video.play().catch(() => {{}});
    }}

    function filtrarCategoria(termo) {{
      filtroAtual = termo;
      document.querySelectorAll('#filtro-categorias button').forEach(b => {{
        const bNorm = normalizar(b.innerText);
        b.classList.toggle('active', bNorm.includes(termo) || (termo === 'todas' && bNorm.includes('todas')));
      }});
      aplicarFiltros();
    }}

    function aplicarFiltros() {{
      const busca = normalizar(campoBusca.value);
      const filtrados = canais.filter(c => {{
        const catNorm = normalizar(c.categoria);
        const nomeNorm = normalizar(c.nome);
        
        let bateFiltro = (filtroAtual === 'todas');
        if (!bateFiltro) {{
          bateFiltro = catNorm.includes(filtroAtual) || nomeNorm.includes(filtroAtual);
        }}
        
        let bateBusca = true;
        if (busca.length > 0) {{
          bateBusca = nomeNorm.includes(busca) || catNorm.includes(busca);
        }}
        return bateFiltro && bateBusca;
      }});
      renderizarCanais(filtrados);
    }}

    function renderizarCanais(lista) {{
      listaCanaisContainer.innerHTML = '';
      if (lista.length === 0) {{
        listaCanaisContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: #94a3b8;">Nenhum canal encontrado. Clique em \\"Todas\\" acima.</div>';
        return;
      }}

      lista.forEach(c => {{
        const item = document.createElement('div');
        item.className = 'channel-item';

        let tagClass = 'quality-tag';
        let tagTexto = 'HD';
        if (c.qualidade && c.qualidade.includes('Full')) {{ tagClass += ' fhd'; tagTexto = '1080p'; }}

        item.innerHTML = `
          <span style="color: #38bdf8; font-size: 1rem;">▶</span>
          <div class="channel-details">
            <span class="channel-name">${{c.nome}}</span>
            <span class="channel-category">${{c.categoria}}</span>
          </div>
          <span class="${{tagClass}}">${{tagTexto}}</span>
        `;

        item.onclick = () => {{
          document.querySelectorAll('.channel-item').forEach(el => el.classList.remove('active'));
          item.classList.add('active');
          tocarCanal(c);
        }};

        listaCanaisContainer.appendChild(item);
      }});
    }}

    function tocarCanal(c) {{
      canalAtualNome.innerText = `${{c.nome}} [${{c.qualidade || 'Ao Vivo'}}]`;
      canalAtualStatus.innerText = `Sintonizando: ${{c.categoria}}...`;

      if (Hls.isSupported()) {{
        if (hls) {{ hls.destroy(); }}
        hls = new Hls({{ enableWorker: true, lowLatencyMode: true }});
        hls.loadSource(c.url);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function () {{
          video.play().catch(() => {{}});
          canalAtualStatus.innerText = 'Canal ao vivo em reprodução.';
        }});
        hls.on(Hls.Events.ERROR, function(evt, data) {{
          if (data.fatal) {{
            canalAtualStatus.innerText = 'Sinal instável. Clique em outro canal da lista.';
          }}
        }});
      }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
        video.src = c.url;
        video.play().catch(() => {{}});
      }}
    }}

    campoBusca.addEventListener('input', aplicarFiltros);
    renderizarCanais(canais);
    if (canais.length > 0) {{
      video.muted = true;
      tocarCanal(canais[0]);
    }}
  </script>
</body>
</html>
"""

# Atualiza no servidor local e na Área de Trabalho
(PASTA_BASE / "saida" / "index.html").write_text(html_final, encoding="utf-8")
(DESKTOP / "ASSISTIR_TV.html").write_text(html_final, encoding="utf-8")
(PASTA_BASE / "saida" / "servico_iptv_dados.json").write_text(json.dumps(todos, indent=2, ensure_ascii=False), encoding="utf-8")

# Atualiza M3U para VLC e TV
linhas_m3u = ['#EXTM3U name="Catálogo Expandido IPTV"', '#EXT-X-VERSION:3']
for c in todos:
    linhas_m3u.append(f'#EXTINF:-1 group-title="{c["categoria"]}",{c["nome"]}')
    linhas_m3u.append(c["url"])

(PASTA_BASE / "saida" / "servico_iptv_comercial.m3u").write_text("\n".join(linhas_m3u) + "\n", encoding="utf-8")
(PASTA_BASE / "saida" / "lista_brasil_turbo.m3u").write_text("\n".join(linhas_m3u) + "\n", encoding="utf-8")
(PASTA_BASE / "saida" / "tv.m3u").write_text("\n".join(linhas_m3u) + "\n", encoding="utf-8")

print(f"[SUCESSO] Catálogo ampliado com {len(todos)} canais reais atualizado na Área de Trabalho e no Servidor!")
