"""
Gera o arquivo autônomo ASSISTIR_TV.html na Área de Trabalho com os dados embutidos.
"""

import json
from pathlib import Path

PASTA_BASE = Path(r"C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
ARQUIVO_JSON = PASTA_BASE / "saida" / "servico_iptv_dados.json"
DESKTOP = Path(r"C:\Users\jonas\Desktop")

dados_canais = json.loads(ARQUIVO_JSON.read_text(encoding="utf-8"))

html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Central de TV - Ao Vivo</title>
  <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    }}
    body {{
      background-color: #0b1120;
      color: #f8fafc;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }}
    header {{
      background-color: #1e293b;
      padding: 14px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #0284c7;
    }}
    header h1 {{
      font-size: 1.3rem;
      font-weight: 700;
      color: #38bdf8;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .badge {{
      background: #0284c7;
      color: #fff;
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 700;
    }}
    .container {{
      display: flex;
      flex: 1;
      height: calc(100vh - 65px);
    }}
    .video-area {{
      flex: 3;
      background-color: #000;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      position: relative;
    }}
    video {{
      width: 100%;
      height: 100%;
      max-height: calc(100vh - 120px);
      background-color: #000;
    }}
    .player-info {{
      width: 100%;
      background: #1e293b;
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid #334155;
    }}
    .sidebar {{
      flex: 1.3;
      background-color: #1e293b;
      border-left: 1px solid #334155;
      display: flex;
      flex-direction: column;
      max-width: 440px;
    }}
    .search-box {{
      padding: 14px 16px;
      border-bottom: 1px solid #334155;
    }}
    .search-box input {{
      width: 100%;
      padding: 12px 14px;
      border-radius: 8px;
      border: 1px solid #475569;
      background-color: #0f172a;
      color: #fff;
      font-size: 1rem;
      outline: none;
    }}
    .search-box input:focus {{
      border-color: #38bdf8;
    }}
    .category-filter {{
      display: flex;
      gap: 6px;
      padding: 10px 16px;
      overflow-x: auto;
      border-bottom: 1px solid #334155;
      background-color: #0f172a;
    }}
    .category-filter button {{
      background: #1e293b;
      color: #94a3b8;
      border: 1px solid #334155;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
    }}
    .category-filter button:hover, .category-filter button.active {{
      background: #0284c7;
      color: #fff;
      border-color: #38bdf8;
    }}
    .channels-list {{
      flex: 1;
      overflow-y: auto;
      padding: 10px 14px;
    }}
    .channel-item {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border-radius: 8px;
      cursor: pointer;
      margin-bottom: 6px;
      background: #0f172a;
      transition: all 0.2s;
      border: 1px solid transparent;
    }}
    .channel-item:hover {{
      background: #334155;
      transform: translateX(4px);
    }}
    .channel-item.active {{
      background: #0369a1;
      border-color: #38bdf8;
    }}
    .channel-details {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    .channel-name {{
      font-weight: 600;
      font-size: 0.95rem;
    }}
    .channel-category {{
      font-size: 0.75rem;
      color: #94a3b8;
    }}
    .quality-tag {{
      font-size: 0.75rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      background: #334155;
      color: #94a3b8;
    }}
    .quality-tag.fhd {{
      background: #0284c7;
      color: #fff;
    }}
  </style>
</head>
<body>
  <header>
    <h1>📺 Minha TV ao Vivo</h1>
    <div class="badge">{len(dados_canais)} Canais Prontos</div>
  </header>

  <div class="container">
    <div class="video-area">
      <video id="player" controls autoplay playsinline></video>
      <div class="player-info">
        <div>
          <h2 id="canal-atual-nome" style="font-size: 1.15rem; color: #38bdf8;">Clique em qualquer canal para assistir</h2>
          <span id="canal-atual-status" style="font-size: 0.85rem; color: #94a3b8;">Aguardando seleção...</span>
        </div>
      </div>
    </div>

    <div class="sidebar">
      <div class="search-box">
        <input type="text" id="campo-busca" placeholder="🔍 Digite o nome do canal (Ex.: AXN, Cazé, Bob)...">
      </div>
      <div class="category-filter" id="filtro-categorias">
        <button class="active" onclick="filtrarCategoria('Todas')">Todas</button>
        <button onclick="filtrarCategoria('🎬 Filmes e Séries')">🎬 Filmes</button>
        <button onclick="filtrarCategoria('⚽ Esportes')">⚽ Esportes</button>
        <button onclick="filtrarCategoria('📰 Notícias')">📰 Notícias</button>
        <button onclick="filtrarCategoria('👶 Desenhos e Infantil')">👶 Desenhos</button>
        <button onclick="filtrarCategoria('🌎 Variedades e Cultura')">🌎 Variedades</button>
      </div>
      <div class="channels-list" id="lista-canais"></div>
    </div>
  </div>

  <script>
    const canais = {json.dumps(dados_canais, ensure_ascii=False)};
    const video = document.getElementById('player');
    const listaCanaisContainer = document.getElementById('lista-canais');
    const campoBusca = document.getElementById('campo-busca');
    const canalAtualNome = document.getElementById('canal-atual-nome');
    const canalAtualStatus = document.getElementById('canal-atual-status');

    let hls = null;
    let categoriaAtual = 'Todas';

    function filtrarCategoria(cat) {{
      categoriaAtual = cat;
      document.querySelectorAll('#filtro-categorias button').forEach(b => {{
        b.classList.toggle('active', b.innerText.includes(cat) || (cat === 'Todas' && b.innerText === 'Todas'));
      }});
      aplicarFiltros();
    }}

    function aplicarFiltros() {{
      const termo = campoBusca.value.toLowerCase();
      const filtrados = canais.filter(c => {{
        const bateCategoria = (categoriaAtual === 'Todas' || c.categoria === categoriaAtual);
        const bateTermo = c.nome.toLowerCase().includes(termo);
        return bateCategoria && bateTermo;
      }});
      renderizarCanais(filtrados);
    }}

    function renderizarCanais(lista) {{
      listaCanaisContainer.innerHTML = '';
      if (lista.length === 0) {{
        listaCanaisContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: #94a3b8;">Nenhum canal encontrado.</div>';
        return;
      }}

      lista.forEach(c => {{
        const item = document.createElement('div');
        item.className = 'channel-item';
        
        let tagClass = 'quality-tag';
        let tagTexto = 'HD';
        if (c.qualidade && c.qualidade.includes('1080p')) {{ tagClass += ' fhd'; tagTexto = '1080p'; }}

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
        hls = new Hls();
        hls.loadSource(c.url);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function () {{
          video.play().catch(() => {{}});
          canalAtualStatus.innerText = 'Canal ao vivo em reprodução.';
        }});
      }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
        video.src = c.url;
        video.play().catch(() => {{}});
        canalAtualStatus.innerText = 'Canal ao vivo em reprodução.';
      }}
    }}

    campoBusca.addEventListener('input', aplicarFiltros);
    renderizarCanais(canais);
    if (canais.length > 0) {{
      tocarCanal(canais[0]);
    }}
  </script>
</body>
</html>
"""

arquivo_destino = DESKTOP / "ASSISTIR_TV.html"
arquivo_destino.write_text(html_template, encoding="utf-8")
print(f"[+] Arquivo criado na Área de Trabalho: {arquivo_destino}")

# Cria também o atalho direto do VLC na Área de Trabalho
bat_vlc = DESKTOP / "ABRIR_NO_VLC.bat"
bat_vlc.write_text(
    f'@echo off\nstart "" "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" --playlist-tree "{PASTA_BASE}\\saida\\servico_iptv_comercial.m3u"\n',
    encoding="utf-8"
)
print(f"[+] Atalho VLC criado na Área de Trabalho: {bat_vlc}")
