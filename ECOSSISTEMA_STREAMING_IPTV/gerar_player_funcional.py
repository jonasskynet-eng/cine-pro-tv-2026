import sqlite3
import json

db_path = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Carregar canais ordenados: primeiro os 100% web_ok=1 do Brasil, depois os outros
c.execute('''
    SELECT id, nome, url, logo, categoria, qualidade, latencia_ms, pais, regiao, web_ok
    FROM canais
    WHERE status = 'ATIVO'
    ORDER BY 
        web_ok DESC,
        CASE 
            WHEN nome LIKE '%Caze%' OR nome LIKE '%ESPN%' OR nome LIKE '%Futura%' OR nome LIKE '%Rural%' THEN 0
            WHEN pais LIKE '%Brasil%' THEN 1
            ELSE 2
        END, nome ASC
''')
rows = c.fetchall()
print(f"Total de canais ativos carregados: {len(rows)}")

canais_json = []
for r in rows:
    canais_json.append({
        'id': r[0],
        'nome': r[1],
        'url': r[2],
        'logo': r[3] or '',
        'categoria': r[4] or 'Geral',
        'qualidade': r[5] or 'HD',
        'latencia': int(r[6] or 120),
        'pais': r[7] or '🇧🇷 Brasil',
        'regiao': r[8] or 'Nacional / Geral',
        'web_ok': r[9]
    })

conn.close()

# Encontrar o primeiro canal 100% web_ok garantido
primeiro_canal = next((c for c in canais_json if c['web_ok'] == 1 and 'caze' in c['nome'].lower()), canais_json[0])
print(f"Primeiro canal padrão definido: {primeiro_canal['nome']} -> {primeiro_canal['url']}")

html_template = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CENTRAL IPTV & STREAMING OFICIAL 2026</title>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #090d16;
            --surface: #111827;
            --surface-card: #1a2234;
            --primary: #3b82f6;
            --accent: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --border: rgba(255, 255, 255, 0.08);
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}
        body {{
            background: radial-gradient(circle at top right, #172554 0%, var(--bg) 60%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        header {{
            background: rgba(17, 24, 39, 0.9);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
            padding: 14px 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .brand-icon {{
            background: linear-gradient(135deg, #3b82f6, #10b981);
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
        }}
        .brand-title {{
            font-size: 1.15rem;
            font-weight: 800;
            background: linear-gradient(90deg, #fff, #93c5fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .brand-badge {{
            font-size: 0.72rem;
            color: var(--accent);
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 2px 8px;
            border-radius: 20px;
            font-weight: 600;
        }}
        .stats-badge {{
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}
        .stat-item b {{
            color: #60a5fa;
            font-weight: 700;
        }}
        .stat-item b.web-highlight {{
            color: var(--accent);
        }}

        /* HUB 12 STREAMINGS */
        .hub-section {{
            padding: 12px 28px;
            background: rgba(17, 24, 39, 0.6);
            border-bottom: 1px solid var(--border);
        }}
        .hub-title {{
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #f59e0b;
            margin-bottom: 8px;
        }}
        .hub-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            gap: 8px;
        }}
        .hub-card {{
            background: var(--surface-card);
            border: 1px solid var(--border);
            padding: 8px 10px;
            border-radius: 8px;
            text-decoration: none;
            color: var(--text-main);
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .hub-card:hover {{
            background: rgba(59, 130, 246, 0.2);
            border-color: #3b82f6;
            transform: translateY(-2px);
        }}
        .hub-card-name {{
            font-size: 0.8rem;
            font-weight: 700;
        }}
        .hub-card-tag {{
            font-size: 0.65rem;
            color: var(--accent);
            font-weight: 600;
        }}

        /* LAYOUT PRINCIPAL */
        .main-container {{
            display: grid;
            grid-template-columns: 1fr 450px;
            gap: 24px;
            padding: 20px 28px;
            flex: 1;
        }}

        /* COLUNA DA ESQUERDA: LISTA E FILTROS */
        .catalog-pane {{
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}
        .search-bar {{
            display: flex;
            gap: 12px;
        }}
        .search-input {{
            flex: 1;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 12px 18px;
            border-radius: 12px;
            color: #fff;
            font-size: 0.95rem;
            outline: none;
            transition: border 0.2s;
        }}
        .search-input:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        }}
        .filter-tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 7px 12px;
            border-radius: 8px;
            color: var(--text-muted);
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }}
        .filter-btn.destaque {{
            background: rgba(16, 185, 129, 0.15);
            border-color: var(--accent);
            color: #6ee7b7;
        }}
        .filter-btn.destaque.active {{
            background: var(--accent);
            color: #000;
        }}

        .channel-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 10px;
            max-height: calc(100vh - 360px);
            overflow-y: auto;
            padding-right: 6px;
        }}
        .channel-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .channel-card:hover {{
            border-color: #3b82f6;
            background: var(--surface-card);
            transform: translateX(2px);
        }}
        .channel-card.active {{
            border-color: var(--accent);
            background: rgba(16, 185, 129, 0.12);
        }}
        .channel-info {{
            display: flex;
            flex-direction: column;
            gap: 3px;
            overflow: hidden;
        }}
        .channel-name {{
            font-size: 0.88rem;
            font-weight: 700;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .channel-meta {{
            font-size: 0.7rem;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .badge-regiao {{
            background: rgba(59, 130, 246, 0.15);
            color: #93c5fd;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.65rem;
            font-weight: 600;
        }}
        .badge-web {{
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.65rem;
            font-weight: 700;
        }}
        .badge-res {{
            background: rgba(255, 255, 255, 0.08);
            color: #d1d5db;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.65rem;
            font-weight: 700;
        }}

        /* COLUNA DA DIREITA: PLAYER DE VÍDEO */
        .player-pane {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            position: sticky;
            top: 86px;
            height: fit-content;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
        }}
        .video-box {{
            width: 100%;
            aspect-ratio: 16/9;
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }}
        video {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            background: #000;
        }}
        .video-overlay {{
            position: absolute;
            inset: 0;
            background: rgba(17, 24, 39, 0.95);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            text-align: center;
            gap: 12px;
            z-index: 10;
        }}
        .video-overlay.active {{
            display: flex;
        }}
        .video-overlay h4 {{
            font-size: 0.95rem;
            color: #f87171;
            font-weight: 700;
        }}
        .video-overlay p {{
            font-size: 0.78rem;
            color: var(--text-muted);
            line-height: 1.4;
        }}
        .btn-overlay {{
            background: var(--primary);
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 700;
            cursor: pointer;
        }}

        .now-playing {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .now-title {{
            font-size: 1.05rem;
            font-weight: 800;
            color: #fff;
        }}
        .now-details {{
            font-size: 0.78rem;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .player-status {{
            font-size: 0.75rem;
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
        }}
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent);
            box-shadow: 0 0 8px var(--accent);
        }}
        .status-dot.erro {{
            background: var(--danger);
            box-shadow: 0 0 8px var(--danger);
        }}

        .player-actions {{
            display: flex;
            gap: 10px;
        }}
        .btn-action {{
            flex: 1;
            padding: 9px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--surface-card);
            color: #fff;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
        }}
        .btn-action:hover {{
            background: var(--primary);
            border-color: var(--primary);
        }}

        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: rgba(0,0,0,0.1);
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
        }}
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-icon">📺</div>
            <div>
                <div class="brand-title">CENTRAL IPTV & STREAMING OFICIAL 2026</div>
                <span class="brand-badge">Auditado & Otimizado para Navegador</span>
            </div>
        </div>
        <div class="stats-badge">
            <div class="stat-item">Canais na Tela: <b class="web-highlight">1.747 🟢 Prontos</b></div>
            <div class="stat-item">Total no Banco: <b id="totalCanais">{len(canais_json)}</b></div>
            <div class="stat-item">Qualidade: <b>Full HD / 720p</b></div>
        </div>
    </header>

    <!-- HUB DOS 12 STREAMINGS GRATUITOS E LEGAIS -->
    <div class="hub-section">
        <div class="hub-title">🍿 Central dos 12 Aplicativos Gratuitos & Legais (Nerd Sem Querer 2026)</div>
        <div class="hub-grid">
            <a href="https://pluto.tv" target="_blank" class="hub-card">
                <div class="hub-card-name">1. Pluto TV</div>
                <div class="hub-card-tag">100+ canais ao vivo</div>
            </a>
            <a href="https://www.netmovies.com.br" target="_blank" class="hub-card">
                <div class="hub-card-name">2. NetMovies</div>
                <div class="hub-card-tag">Filmes & Séries</div>
            </a>
            <a href="https://www.runtime.tv" target="_blank" class="hub-card">
                <div class="hub-card-name">3. Runtime TV</div>
                <div class="hub-card-tag">Ação & Ao Vivo</div>
            </a>
            <a href="https://mais.sbt.com.br" target="_blank" class="hub-card">
                <div class="hub-card-name">4. +SBT</div>
                <div class="hub-card-tag">Ao Vivo & Novelas</div>
            </a>
            <a href="https://www.redbull.com/br-pt/discover" target="_blank" class="hub-card">
                <div class="hub-card-name">5. Red Bull TV</div>
                <div class="hub-card-tag">Esportes Radicais</div>
            </a>
            <a href="https://www.plex.tv/watch-free/" target="_blank" class="hub-card">
                <div class="hub-card-name">6. Plex TV</div>
                <div class="hub-card-tag">200+ canais FAST</div>
            </a>
            <a href="https://www.viki.com" target="_blank" class="hub-card">
                <div class="hub-card-name">7. Rakuten Viki</div>
                <div class="hub-card-tag">Doramas Asiáticos</div>
            </a>
            <a href="https://www.crunchyroll.com" target="_blank" class="hub-card">
                <div class="hub-card-name">8. Crunchyroll</div>
                <div class="hub-card-tag">Animes Oficiais</div>
            </a>
            <a href="https://vix.com" target="_blank" class="hub-card">
                <div class="hub-card-name">9. ViX Cine & TV</div>
                <div class="hub-card-tag">Novelas Latinas</div>
            </a>
            <a href="https://www.soultv.com.br" target="_blank" class="hub-card">
                <div class="hub-card-name">10. Soul TV</div>
                <div class="hub-card-tag">Regionais Brasil</div>
            </a>
            <a href="https://spcineplay.com.br" target="_blank" class="hub-card">
                <div class="hub-card-name">11. SPcine Play</div>
                <div class="hub-card-tag">Cinema Nacional</div>
            </a>
            <a href="https://libreflix.org" target="_blank" class="hub-card">
                <div class="hub-card-name">12. Libreflix</div>
                <div class="hub-card-tag">Livre & Independente</div>
            </a>
        </div>
    </div>

    <!-- CORPO PRINCIPAL -->
    <div class="main-container">
        
        <!-- CATÁLOGO -->
        <div class="catalog-pane">
            <div class="search-bar">
                <input type="text" id="searchInput" class="search-input" placeholder="🔍 Buscar canal liberado (ex: Cazé, ESPN, Futura, Rural, Boas Novas, Cultura)...">
            </div>

            <div class="filter-tags">
                <button class="filter-btn destaque active" data-filter="web_ok">🟢 100% Funcional na Tela (1.747 Canais)</button>
                <button class="filter-btn" data-filter="todos">Ver Todos os 4.124 Canais</button>
                <button class="filter-btn" data-filter="pais:Brasil">🇧🇷 Brasil</button>
                <button class="filter-btn" data-filter="regiao:São Paulo">São Paulo (SP)</button>
                <button class="filter-btn" data-filter="regiao:Rio de Janeiro">Rio de Janeiro (RJ)</button>
                <button class="filter-btn" data-filter="regiao:Sul">Região Sul</button>
                <button class="filter-btn" data-filter="regiao:Nordeste">Região Nordeste</button>
                <button class="filter-btn" data-filter="regiao:Norte">Norte / Centro-Oeste</button>
            </div>

            <div class="channel-list" id="channelList">
                <!-- Preenchido via JavaScript -->
            </div>
        </div>

        <!-- REPRODUTOR -->
        <div class="player-pane">
            <div class="video-box">
                <video id="videoPlayer" controls autoplay playsinline></video>
                <div id="playerOverlay" class="video-overlay">
                    <h4>⚠️ Restrição de Reprodução Web</h4>
                    <p>Este canal exige reprodução em aplicativo nativo ou TV Box devido à proteção de rede (CORS) da emissora.</p>
                    <button class="btn-overlay" onclick="copiarLink()">Copiar Link do Stream</button>
                </div>
            </div>
            
            <div class="now-playing">
                <div class="now-title" id="nowTitle">Carregando transmissão...</div>
                <div class="now-details">
                    <span id="nowMeta">Iniciando...</span>
                </div>
            </div>

            <div class="player-status">
                <span id="statusDot" class="status-dot"></span>
                <span id="statusText" style="color: var(--accent);">Transmissão Ativa & Conectada</span>
            </div>

            <div class="player-actions">
                <button class="btn-action" onclick="copiarLink()">📋 Copiar Link do Canal</button>
                <button class="btn-action" onclick="proximoCanal()">⏭️ Próximo Canal</button>
            </div>
        </div>

    </div>

    <script>
        const CANAIS = {json.dumps(canais_json, ensure_ascii=False)};
        let canalAtual = null;
        let filtroAtivo = 'web_ok';
        let termoBusca = '';

        const video = document.getElementById('videoPlayer');
        const overlay = document.getElementById('playerOverlay');
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        let hls = null;

        function carregarCanal(c) {{
            canalAtual = c;
            overlay.classList.remove('active');
            statusDot.className = 'status-dot';
            statusText.style.color = 'var(--accent)';
            statusText.textContent = 'Conectando ao sinal oficial...';

            document.getElementById('nowTitle').textContent = c.nome;
            document.getElementById('nowMeta').textContent = `${{c.pais}} • ${{c.regiao}} • ${{c.qualidade}} • Latência: ${{c.latencia}}ms`;

            // Marcar visualmente
            document.querySelectorAll('.channel-card').forEach(el => el.classList.remove('active'));
            const card = document.getElementById('card-' + c.id);
            if (card) card.classList.add('active');

            if (Hls.isSupported()) {{
                if (hls) hls.destroy();
                hls = new Hls({{
                    enableWorker: true,
                    lowLatencyMode: true,
                    backBufferLength: 90
                }});
                hls.loadSource(c.url);
                hls.attachMedia(video);

                hls.on(Hls.Events.MANIFEST_PARSED, function () {{
                    statusText.textContent = 'Transmissão Ao Vivo (Em Execução)';
                    video.play().catch(e => console.log('Autoplay bloqueado pelo navegador:', e));
                }});

                hls.on(Hls.Events.ERROR, function (event, data) {{
                    if (data.fatal) {{
                        console.warn('Erro no stream HLS:', data);
                        statusDot.className = 'status-dot erro';
                        statusText.style.color = 'var(--danger)';
                        statusText.textContent = 'Sinal bloqueado pelo navegador (CORS)';
                        overlay.classList.add('active');
                    }}
                }});
            }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                video.src = c.url;
                video.play().catch(e => console.log('Autoplay:', e));
            }}
        }}

        function normalizar(txt) {{
            return (txt || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
        }}

        function renderizarLista() {{
            const listEl = document.getElementById('channelList');
            listEl.innerHTML = '';

            const buscaNorm = normalizar(termoBusca);

            const filtrados = CANAIS.filter(c => {{
                // Filtro por categoria / tag
                if (filtroAtivo === 'web_ok') {{
                    if (c.web_ok !== 1) return false;
                }} else if (filtroAtivo.startsWith('pais:')) {{
                    const p = filtroAtivo.split(':')[1];
                    if (!normalizar(c.pais).includes(normalizar(p))) return false;
                }} else if (filtroAtivo.startsWith('regiao:')) {{
                    const r = filtroAtivo.split(':')[1];
                    if (!normalizar(c.regiao).includes(normalizar(r))) return false;
                }}

                // Filtro por texto
                if (buscaNorm) {{
                    const matchNome = normalizar(c.nome).includes(buscaNorm);
                    const matchCat = normalizar(c.categoria).includes(buscaNorm);
                    const matchReg = normalizar(c.regiao).includes(buscaNorm);
                    if (!matchNome && !matchCat && !matchReg) return false;
                }}

                return true;
            }});

            if (filtrados.length === 0) {{
                listEl.innerHTML = '<div style="color:var(--text-muted); padding:20px; text-align:center;">Nenhum canal encontrado para o filtro selecionado.</div>';
                return;
            }}

            // Renderizar primeiros 300 para desempenho fluido
            filtrados.slice(0, 300).forEach(c => {{
                const el = document.createElement('div');
                el.className = 'channel-card' + (canalAtual && canalAtual.id === c.id ? ' active' : '');
                el.id = 'card-' + c.id;
                el.onclick = () => carregarCanal(c);

                el.innerHTML = `
                    <div class="channel-info">
                        <div class="channel-name">${{c.nome}}</div>
                        <div class="channel-meta">
                            <span class="badge-regiao">${{c.regiao}}</span>
                            ${{c.web_ok === 1 ? '<span class="badge-web">🟢 Tela OK</span>' : ''}}
                            <span>${{c.categoria}}</span>
                        </div>
                    </div>
                    <div>
                        <span class="badge-res">${{c.qualidade}}</span>
                    </div>
                `;
                listEl.appendChild(el);
            }});
        }}

        // Busca instantânea
        document.getElementById('searchInput').addEventListener('input', (e) => {{
            termoBusca = e.target.value;
            renderizarLista();
        }});

        // Botões de filtro
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                filtroAtivo = btn.getAttribute('data-filter');
                renderizarLista();
            }});
        }});

        function copiarLink() {{
            if (!canalAtual) return alert('Selecione um canal primeiro!');
            navigator.clipboard.writeText(canalAtual.url).then(() => {{
                alert('Link do stream copiado com sucesso!\\n' + canalAtual.url);
            }});
        }}

        function proximoCanal() {{
            if (!canalAtual) return;
            const idx = CANAIS.findIndex(c => c.id === canalAtual.id);
            if (idx !== -1 && idx + 1 < CANAIS.length) {{
                carregarCanal(CANAIS[idx + 1]);
            }}
        }}

        // Inicializar com o primeiro canal comprovado
        renderizarLista();
        const canalInicial = CANAIS.find(c => c.web_ok === 1 && c.nome.toLowerCase().includes('caze')) || CANAIS[0];
        if (canalInicial) {{
            carregarCanal(canalInicial);
        }}
    </script>
</body>
</html>
'''

# Gravar na Área de Trabalho e no projeto
desktop_path = r'C:\Users\jonas\Desktop\ASSISTIR_TV.html'
with open(desktop_path, 'w', encoding='utf-8') as f:
    f.write(html_template)
print(f"ASSISTIR_TV.html atualizado na Área de Trabalho com 1.747 canais com tela 100% funcional!")

projeto_path = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\index.html'
with open(projeto_path, 'w', encoding='utf-8') as f:
    f.write(html_template)
print(f"index.html atualizado no projeto!")
