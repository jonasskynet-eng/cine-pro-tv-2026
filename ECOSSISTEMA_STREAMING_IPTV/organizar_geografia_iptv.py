"""
ORGANIZADOR GEOGRÁFICO DE CANAIS (PAÍS E REGIÃO)
1. Adiciona colunas 'pais' e 'regiao' na tabela 'canais' do SQLite banco_iptv.db.
2. Analisa os 914 canais e classifica geograficamente (Brasil, Portugal, Internacional, etc.).
3. Para o Brasil, categoriza por Regiões e Estados (Nacional, SP, RJ, Sul, Nordeste, Norte/Centro-Oeste).
4. Atualiza a interface gráfica visual (ASSISTIR_TV.html) com abas de países com bandeiras e regiões.
"""

import sqlite3
import re
import json
from pathlib import Path

PASTA_BASE = Path(r"C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
CAMINHO_BANCO = PASTA_BASE / "saida" / "banco_iptv.db"
DESKTOP = Path(r"C:\Users\jonas\Desktop")

def classificar_geografia(nome: str, url: str) -> tuple:
    n = nome.lower()
    u = url.lower()

    # 1. PORTUGAL / LUSÓFONOS
    if any(k in n or k in u for k in ["portugal", "rtp", "sic", "tvi", "euronews portugal", "euronews pt", ".pt/", "angola", "moçambique"]):
        return ("🇵🇹 Portugal / Lusófonos", "Europa")

    # 2. INTERNACIONAL (ESPANHOL / AMÉRICA LATINA)
    if any(k in n or k in u for k in ["latin america", "español", "espanha", "colombia", "argentina", "mexico", "chile", "panregional"]):
        return ("🌎 América Latina / Internacional", "América Latina")

    # 3. INTERNACIONAL (INGLÊS / GLOBAL)
    if any(k in n or k in u for k in ["nasa", "bloomberg", "dw", "euronews germany", "al jazeera", "red bull", "global (index)"]):
        return ("🌐 Internacional / Global", "Mundo")

    # 4. BRASIL (ESTADOS E REGIÕES)
    # São Paulo
    if any(k in n or k in u for k in ["sp", "são paulo", "sao paulo", "gazeta", "band sp", "globo sp", "sbt sp", "record sp", "plena"]):
        return ("🇧🇷 Brasil", "São Paulo (SP)")
    
    # Rio de Janeiro
    if any(k in n or k in u for k in ["rj", "rio de janeiro", "globo rj", "band rj"]):
        return ("🇧🇷 Brasil", "Rio de Janeiro (RJ)")

    # Sul (Paraná, Santa Catarina, Rio Grande do Sul)
    if any(k in n or k in u for k in ["paraná", "parana", "catve", "rs", "tve rs", "sc", "santa catarina", "curitiba", "porto alegre", "sul"]):
        return ("🇧🇷 Brasil", "Região Sul (PR/SC/RS)")

    # Nordeste (Bahia, Pernambuco, Ceará, etc.)
    if any(k in n or k in u for k in ["aratu", "bahia", "ba", "pe", "recife", "ceará", "ceara", "fortaleza", "fdr", "nordeste"]):
        return ("🇧🇷 Brasil", "Região Nordeste")

    # Norte e Centro-Oeste
    if any(k in n or k in u for k in ["amazon sat", "amazonia", "go", "sbt go", "goiás", "goias", "brasília", "brasilia", "df"]):
        return ("🇧🇷 Brasil", "Norte / Centro-Oeste")

    # Brasil Nacional (Filmes dublados, notícias gerais, canais abertos nacionais)
    return ("🇧🇷 Brasil", "Nacional / Geral")

def executar_organizacao():
    conn = sqlite3.connect(CAMINHO_BANCO)
    cur = conn.cursor()

    # Adiciona colunas se não existirem
    try:
        cur.execute("ALTER TABLE canais ADD COLUMN pais TEXT DEFAULT '🇧🇷 Brasil'")
    except:
        pass
    try:
        cur.execute("ALTER TABLE canais ADD COLUMN regiao TEXT DEFAULT 'Nacional / Geral'")
    except:
        pass

    cur.execute("CREATE INDEX IF NOT EXISTS idx_pais_regiao ON canais(pais, regiao);")

    cur.execute("SELECT id, nome, url FROM canais WHERE status = 'ATIVO'")
    canais = cur.fetchall()

    print(f"[*] Classificando geograficamente {len(canais)} canais...")

    contadores_pais = {}
    contadores_regiao = {}

    for id_canal, nome, url in canais:
        pais, regiao = classificar_geografia(nome, url)
        cur.execute("UPDATE canais SET pais = ?, regiao = ? WHERE id = ?", (pais, regiao, id_canal))
        
        contadores_pais[pais] = contadores_pais.get(pais, 0) + 1
        if pais == "🇧🇷 Brasil":
            contadores_regiao[regiao] = contadores_regiao.get(regiao, 0) + 1

    conn.commit()

    print("\n==================================================================")
    print("📍 DISTRIBUIÇÃO CONSOLIDADA POR PAÍS:")
    print("==================================================================")
    for p, qtd in sorted(contadores_pais.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {p:<35} : {qtd} canais")

    print("\n📍 DISTRIBUIÇÃO DOS CANAIS DO BRASIL POR REGIÃO:")
    print("==================================================================")
    for r, qtd in sorted(contadores_regiao.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {r:<30} : {qtd} canais")

    # Gera o banco atualizado ordenado por País, Região, Categoria e Nome
    cur.execute("""
        SELECT nome, url, logo, categoria, qualidade, latencia_ms, pais, regiao
        FROM canais
        WHERE status = 'ATIVO'
        ORDER BY 
            CASE WHEN pais LIKE '%Brasil%' THEN 1 ELSE 2 END,
            pais, regiao, categoria, nome;
    """)
    linhas = cur.fetchall()
    conn.close()

    todos_sinc = []
    for r in linhas:
        todos_sinc.append({
            "nome": r[0],
            "url": r[1],
            "logo": r[2],
            "categoria": r[3],
            "qualidade": r[4],
            "latencia_ms": r[5],
            "pais": r[6],
            "regiao": r[7]
        })

    # Atualiza o arquivo de dados JSON
    (PASTA_BASE / "saida" / "servico_iptv_dados.json").write_text(
        json.dumps(todos_sinc, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Cria o novo Player com Filtros Geográficos Avançados
    html_geografico = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Central IPTV Turbo - Organização por País e Região</title>
  <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }}
    body {{ background-color: #0b1120; color: #f8fafc; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
    header {{ background-color: #1e293b; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0284c7; }}
    header h1 {{ font-size: 1.25rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px; }}
    .badge {{ background: #22c55e; color: #000; padding: 4px 14px; border-radius: 9999px; font-size: 0.85rem; font-weight: 700; }}
    .container {{ display: flex; flex: 1; height: calc(100vh - 65px); }}
    .video-area {{ flex: 3; background-color: #000; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; }}
    video {{ width: 100%; height: 100%; max-height: calc(100vh - 120px); background-color: #000; }}
    .player-info {{ width: 100%; background: #1e293b; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #334155; }}
    .btn-som {{ background: #22c55e; color: #000; border: none; padding: 8px 18px; border-radius: 6px; font-weight: 700; cursor: pointer; font-size: 0.95rem; }}
    .sidebar {{ flex: 1.35; background-color: #1e293b; border-left: 1px solid #334155; display: flex; flex-direction: column; max-width: 480px; }}
    
    .filter-section {{
      padding: 10px 14px;
      border-bottom: 1px solid #334155;
      background-color: #0f172a;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .filter-label {{
      font-size: 0.75rem;
      font-weight: 700;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .pill-group {{
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 2px;
    }}
    .pill-group button {{
      background: #1e293b;
      color: #94a3b8;
      border: 1px solid #334155;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
    }}
    .pill-group button:hover, .pill-group button.active {{
      background: #0284c7;
      color: #fff;
      border-color: #38bdf8;
    }}
    .search-box {{
      padding: 10px 14px;
      border-bottom: 1px solid #334155;
    }}
    .search-box input {{
      width: 100%;
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid #475569;
      background-color: #0f172a;
      color: #fff;
      font-size: 0.95rem;
      outline: none;
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
    .channel-tags {{
      display: flex;
      gap: 6px;
      font-size: 0.72rem;
      color: #94a3b8;
    }}
    .tag-geo {{
      background: #1e293b;
      padding: 1px 6px;
      border-radius: 3px;
      color: #38bdf8;
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
    <h1>📺 Central IPTV Turbo <span>(Por País e Região)</span></h1>
    <div class="badge" id="badge-total">{len(todos_sinc)} Canais Prontos</div>
  </header>

  <div class="container">
    <div class="video-area">
      <video id="player" controls autoplay playsinline></video>
      <div class="player-info">
        <div>
          <h2 id="canal-atual-nome" style="font-size: 1.15rem; color: #38bdf8;">Selecione um canal na lateral</h2>
          <span id="canal-atual-status" style="font-size: 0.85rem; color: #4ade80;">Sintonizando transmissão ao vivo...</span>
        </div>
        <button id="btn-som" class="btn-som" onclick="ativarSom()">🔊 Ativar Som</button>
      </div>
    </div>

    <div class="sidebar">
      <!-- 1. FILTRO DE PAÍS -->
      <div class="filter-section">
        <span class="filter-label">🌍 Selecionar País</span>
        <div class="pill-group" id="filtro-pais">
          <button class="active" onclick="filtrarPais('todos')">Todos ({len(todos_sinc)})</button>
          <button onclick="filtrarPais('brasil')">🇧🇷 Brasil ({contadores_pais.get('🇧🇷 Brasil', 0)})</button>
          <button onclick="filtrarPais('portugal')">🇵🇹 Portugal ({contadores_pais.get('🇵🇹 Portugal / Lusófonos', 0)})</button>
          <button onclick="filtrarPais('internacional')">🌐 Internacional</button>
        </div>
      </div>

      <!-- 2. FILTRO DE REGIÃO (BRASIL) -->
      <div class="filter-section" id="secao-regiao">
        <span class="filter-label">📍 Regiões do Brasil</span>
        <div class="pill-group" id="filtro-regiao">
          <button class="active" onclick="filtrarRegiao('todas')">Todas as Regiões</button>
          <button onclick="filtrarRegiao('são paulo')">São Paulo</button>
          <button onclick="filtrarRegiao('rio de janeiro')">Rio de Janeiro</button>
          <button onclick="filtrarRegiao('sul')">Região Sul</button>
          <button onclick="filtrarRegiao('nordeste')">Nordeste</button>
          <button onclick="filtrarRegiao('nacional')">Nacional</button>
        </div>
      </div>

      <!-- 3. FILTRO DE GÊNERO -->
      <div class="filter-section">
        <span class="filter-label">🎬 Gênero</span>
        <div class="pill-group" id="filtro-categoria">
          <button class="active" onclick="filtrarCategoria('todas')">Todos os Gêneros</button>
          <button onclick="filtrarCategoria('filme')">Filmes & Séries</button>
          <button onclick="filtrarCategoria('desenho')">Desenhos 24h</button>
          <button onclick="filtrarCategoria('esporte')">Esportes</button>
          <button onclick="filtrarCategoria('noticia')">Notícias</button>
          <button onclick="filtrarCategoria('musica')">Música</button>
        </div>
      </div>

      <!-- 4. BUSCA -->
      <div class="search-box">
        <input type="text" id="campo-busca" placeholder="🔍 Buscar por canal, estado ou cidade...">
      </div>

      <div class="channels-list" id="lista-canais"></div>
    </div>
  </div>

  <script>
    const canais = {json.dumps(todos_sinc, ensure_ascii=False)};
    const video = document.getElementById('player');
    const listaCanaisContainer = document.getElementById('lista-canais');
    const campoBusca = document.getElementById('campo-busca');
    const canalAtualNome = document.getElementById('canal-atual-nome');
    const canalAtualStatus = document.getElementById('canal-atual-status');
    const btnSom = document.getElementById('btn-som');
    const badgeTotal = document.getElementById('badge-total');

    let hls = null;
    let filtroPais = 'todos';
    let filtroRegiao = 'todas';
    let filtroCat = 'todas';

    function normalizar(t) {{
      return (t || '').toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").replace(/[^a-z0-9]/g, "");
    }}

    function ativarSom() {{
      video.muted = false;
      btnSom.style.display = 'none';
      video.play().catch(() => {{}});
    }}

    function filtrarPais(pais) {{
      filtroPais = pais;
      document.querySelectorAll('#filtro-pais button').forEach(b => {{
        const bNorm = normalizar(b.innerText);
        b.classList.toggle('active', bNorm.includes(pais) || (pais === 'todos' && bNorm.includes('todos')));
      }});
      // Mostra ou esconde as regiões do Brasil
      const secaoRegiao = document.getElementById('secao-regiao');
      if (pais !== 'brasil' && pais !== 'todos') {{
        secaoRegiao.style.display = 'none';
        filtroRegiao = 'todas';
      }} else {{
        secaoRegiao.style.display = 'flex';
      }}
      aplicarFiltros();
    }}

    function filtrarRegiao(regiao) {{
      filtroRegiao = regiao;
      document.querySelectorAll('#filtro-regiao button').forEach(b => {{
        const bNorm = normalizar(b.innerText);
        b.classList.toggle('active', bNorm.includes(regiao) || (regiao === 'todas' && bNorm.includes('todas')));
      }});
      aplicarFiltros();
    }}

    function filtrarCategoria(cat) {{
      filtroCat = cat;
      document.querySelectorAll('#filtro-categoria button').forEach(b => {{
        const bNorm = normalizar(b.innerText);
        b.classList.toggle('active', bNorm.includes(cat) || (cat === 'todas' && bNorm.includes('todos')));
      }});
      aplicarFiltros();
    }}

    function aplicarFiltros() {{
      const busca = normalizar(campoBusca.value);
      const filtrados = canais.filter(c => {{
        const paisNorm = normalizar(c.pais);
        const regNorm = normalizar(c.regiao);
        const catNorm = normalizar(c.categoria);
        const nomeNorm = normalizar(c.nome);

        // Filtro País
        let batePais = (filtroPais === 'todos') || paisNorm.includes(filtroPais);

        // Filtro Região
        let bateRegiao = (filtroRegiao === 'todas') || regNorm.includes(filtroRegiao);

        // Filtro Gênero
        let bateCat = (filtroCat === 'todas') || catNorm.includes(filtroCat) || nomeNorm.includes(filtroCat);

        // Filtro Busca
        let bateBusca = true;
        if (busca.length > 0) {{
          bateBusca = nomeNorm.includes(busca) || regNorm.includes(busca) || paisNorm.includes(busca);
        }}

        return batePais && bateRegiao && bateCat && bateBusca;
      }});

      renderizarCanais(filtrados);
      badgeTotal.innerText = `${{filtrados.length}} Canais Filtrados`;
    }}

    function renderizarCanais(lista) {{
      listaCanaisContainer.innerHTML = '';
      if (lista.length === 0) {{
        listaCanaisContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: #94a3b8;">Nenhum canal encontrado com estes filtros. Clique em \\"Todos\\" acima.</div>';
        return;
      }}

      lista.forEach((c, idx) => {{
        const item = document.createElement('div');
        item.className = 'channel-item' + (idx === 0 ? ' active' : '');

        let tagClass = 'quality-tag';
        let tagTexto = 'HD';
        if (c.qualidade && c.qualidade.includes('Full')) {{ tagClass += ' fhd'; tagTexto = '1080p'; }}

        item.innerHTML = `
          <span style="color: #38bdf8; font-size: 1rem;">▶</span>
          <div class="channel-details">
            <span class="channel-name">${{c.nome}}</span>
            <div class="channel-tags">
              <span class="tag-geo">${{c.pais}}</span>
              <span class="tag-geo">${{c.regiao}}</span>
              <span>${{c.categoria}}</span>
            </div>
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
      canalAtualNome.innerText = `${{c.nome}} [${{c.pais}} • ${{c.regiao}}]`;
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

    (PASTA_BASE / "saida" / "index.html").write_text(html_geografico, encoding="utf-8")
    (DESKTOP / "ASSISTIR_TV.html").write_text(html_geografico, encoding="utf-8")

    # Atualiza também o arquivo M3U para agrupar por País e Região
    m3u_linhas = ['#EXTM3U name="Canais Organizados por Pais e Regiao"', '#EXT-X-VERSION:3']
    for c in todos_sinc:
        grupo_geo = f"{c['pais']} - {c['regiao']}"
        m3u_linhas.append(f'#EXTINF:-1 tvg-logo="{c["logo"]}" group-title="{grupo_geo}",{c["nome"]}')
        m3u_linhas.append(c["url"])

    (PASTA_BASE / "saida" / "servico_iptv_comercial.m3u").write_text("\n".join(m3u_linhas) + "\n", encoding="utf-8")
    (PASTA_BASE / "saida" / "tv.m3u").write_text("\n".join(m3u_linhas) + "\n", encoding="utf-8")
    (PASTA_BASE / "saida" / "lista_brasil_turbo.m3u").write_text("\n".join(m3u_linhas) + "\n", encoding="utf-8")

    print("[+] Concluído! O banco SQLite e o visual agora estão 100% organizados por País e Região!")

if __name__ == "__main__":
    executar_organizacao()
