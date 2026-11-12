import sqlite3
import json

db_path = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\banco_iptv.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Selecionar todos os canais ativos (excluindo os Geo-blocked)
c.execute('''
    SELECT id, nome, url, logo, categoria, qualidade, latencia_ms, pais, regiao, cors_star
    FROM canais
    WHERE status = 'ATIVO' AND LOWER(nome) NOT LIKE '%geo-blocked%'
    ORDER BY 
        cors_star DESC,
        CASE 
            WHEN nome LIKE '%Discovery Kids%' OR nome LIKE '%Discovery Channel%' OR nome LIKE '%Animal Planet%' THEN 0
            WHEN nome LIKE '%Amazon Sat%' OR nome LIKE '%Boas Novas%' OR nome LIKE '%Comedy Central%' THEN 1
            ELSE 2
        END, nome ASC
''')
rows = c.fetchall()
conn.close()

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
        'cors_star': r[9]
    })

print(f"Total de canais ativos limpos: {len(canais_json)}")

html_code = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CENTRAL DE TV & STREAMING 2026</title>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0a0e17;
            --surface: #121826;
            --surface-hover: #1e293b;
            --primary: #2563eb;
            --primary-glow: rgba(37, 99, 235, 0.35);
            --emerald: #10b981;
            --amber: #f59e0b;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --border-subtle: rgba(255, 255, 255, 0.08);
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, sans-serif;
        }}
        body {{
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        header {{
            background: rgba(10, 14, 23, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border-subtle);
            padding: 16px 36px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .brand-logo {{
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, #3b82f6, #10b981);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 4px 16px var(--primary-glow);
        }}
        .brand-text h1 {{
            font-size: 1.1rem;
            font-weight: 700;
        }}
        .brand-text span {{
            font-size: 0.75rem;
            color: var(--emerald);
            font-weight: 600;
        }}

        .search-container {{
            flex: 0 1 450px;
            position: relative;
        }}
        .search-box {{
            width: 100%;
            background: var(--surface);
            border: 1px solid var(--border-subtle);
            padding: 10px 16px 10px 40px;
            border-radius: 20px;
            color: #fff;
            font-size: 0.88rem;
            outline: none;
            transition: all 0.2s ease;
        }}
        .search-box:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px var(--primary-glow);
            background: #172033;
        }}
        .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-dim);
            font-size: 0.9rem;
        }}

        .stage {{
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 28px;
            padding: 24px 36px;
            flex: 1;
            max-width: 1800px;
            margin: 0 auto;
            width: 100%;
        }}

        .cinema-player {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .screen-frame {{
            width: 100%;
            aspect-ratio: 16/9;
            background: #000;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
            border: 1px solid var(--border-subtle);
            position: relative;
        }}
        video {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            background: #000;
        }}

        .toast-status {{
            position: absolute;
            bottom: 14px;
            left: 14px;
            right: 14px;
            background: rgba(18, 24, 38, 0.92);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            padding: 10px 16px;
            border-radius: 10px;
            display: none;
            align-items: center;
            justify-content: space-between;
            font-size: 0.82rem;
            z-index: 20;
        }}
        .toast-status.active {{
            display: flex;
        }}
        .toast-btn {{
            background: var(--primary);
            color: #fff;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
        }}

        .player-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--surface);
            padding: 16px 20px;
            border-radius: 12px;
            border: 1px solid var(--border-subtle);
        }}
        .current-channel-title {{
            font-size: 1.25rem;
            font-weight: 700;
        }}
        .current-channel-sub {{
            font-size: 0.82rem;
            color: var(--text-dim);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .live-dot {{
            width: 8px;
            height: 8px;
            background: var(--emerald);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 10px var(--emerald);
        }}

        .player-controls {{
            display: flex;
            gap: 10px;
        }}
        .btn-ctrl {{
            background: var(--surface-hover);
            border: 1px solid var(--border-subtle);
            color: #fff;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn-ctrl:hover {{
            background: var(--primary);
            border-color: var(--primary);
        }}

        .sidebar-channels {{
            background: var(--surface);
            border-radius: 16px;
            border: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            height: calc(100vh - 120px);
            position: sticky;
            top: 96px;
        }}

        .nav-tabs {{
            display: flex;
            padding: 8px;
            gap: 6px;
            background: rgba(10, 14, 23, 0.4);
            border-bottom: 1px solid var(--border-subtle);
            overflow-x: auto;
        }}
        .nav-tab {{
            flex: 1;
            text-align: center;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-dim);
            cursor: pointer;
            border: none;
            background: transparent;
            white-space: nowrap;
            transition: all 0.2s;
        }}
        .nav-tab.active {{
            background: var(--primary);
            color: #fff;
            box-shadow: 0 2px 8px var(--primary-glow);
        }}

        .channel-stream-list {{
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .stream-card {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid transparent;
            padding: 12px 14px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .stream-card:hover {{
            background: var(--surface-hover);
            border-color: var(--border-subtle);
            transform: translateX(2px);
        }}
        .stream-card.active {{
            background: rgba(37, 99, 235, 0.15);
            border-color: var(--primary);
        }}
        .stream-name {{
            font-size: 0.88rem;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .stream-sub {{
            font-size: 0.72rem;
            color: var(--text-dim);
            display: flex;
            gap: 6px;
            align-items: center;
        }}
        .tag-web {{
            color: var(--emerald);
            font-weight: 700;
        }}
        .tag-res {{
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.08);
            color: #e2e8f0;
            font-weight: 700;
        }}

        .stream-hubs-footer {{
            padding: 24px 36px 36px;
            max-width: 1800px;
            margin: 0 auto;
            width: 100%;
        }}
        .hub-label {{
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--amber);
            margin-bottom: 12px;
        }}
        .hub-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            gap: 10px;
        }}
        .hub-pill {{
            background: var(--surface);
            border: 1px solid var(--border-subtle);
            padding: 10px 14px;
            border-radius: 10px;
            text-decoration: none;
            color: var(--text-main);
            font-size: 0.8rem;
            font-weight: 600;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .hub-pill:hover {{
            background: var(--surface-hover);
            border-color: var(--primary);
            transform: translateY(-2px);
        }}
        .hub-pill span {{
            color: var(--emerald);
            font-size: 0.65rem;
        }}
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-logo">📺</div>
            <div class="brand-text">
                <h1>CENTRAL DE TV & STREAMING</h1>
                <span>Sinal Oficial • 100% Legal</span>
            </div>
        </div>

        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" class="search-box" placeholder="Buscar canal rápido (Discovery, Kids, Animal Planet, Turbo, ESPN)...">
        </div>
    </header>

    <div class="stage">
        
        <div class="cinema-player">
            <div class="screen-frame">
                <video id="mainVideo" controls autoplay playsinline></video>
                <div id="toastStatus" class="toast-status">
                    <span id="toastMsg">Sintonizando sinal...</span>
                    <button class="toast-btn" onclick="copiarLink()">Copiar Link</button>
                </div>
            </div>

            <div class="player-bar">
                <div class="channel-header">
                    <div class="current-channel-title" id="nowTitle">Carregando canal...</div>
                    <div class="current-channel-sub">
                        <span class="live-dot" id="liveDot"></span>
                        <span id="nowMeta">Iniciando transmissão...</span>
                    </div>
                </div>

                <div class="player-controls">
                    <button class="btn-ctrl" onclick="copiarLink()">📋 Copiar Link</button>
                    <button class="btn-ctrl" onclick="proximoCanal()">⏭️ Próximo Canal</button>
                </div>
            </div>
        </div>

        <div class="sidebar-channels">
            <div class="nav-tabs">
                <button class="nav-tab active" data-filter="discovery">🦁 Discovery</button>
                <button class="nav-tab" data-filter="direto">🟢 Tocam Direto</button>
                <button class="nav-tab" data-filter="br">🇧🇷 Brasil</button>
                <button class="nav-tab" data-filter="sp">SP / RJ</button>
                <button class="nav-tab" data-filter="sul">Sul</button>
                <button class="nav-tab" data-filter="todos">Todos</button>
            </div>

            <div class="channel-stream-list" id="channelList"></div>
        </div>

    </div>

    <div class="stream-hubs-footer">
        <div class="hub-label">🍿 Central dos 12 Streamings Oficiais e Gratuitos (Nerd Sem Querer 2026)</div>
        <div class="hub-bar">
            <a href="https://pluto.tv" target="_blank" class="hub-pill">Pluto TV <span>100+ Ch</span></a>
            <a href="https://www.netmovies.com.br" target="_blank" class="hub-pill">NetMovies <span>Filmes</span></a>
            <a href="https://www.runtime.tv" target="_blank" class="hub-pill">Runtime TV <span>Ao Vivo</span></a>
            <a href="https://mais.sbt.com.br" target="_blank" class="hub-pill">+SBT <span>Novelas</span></a>
            <a href="https://www.redbull.com/br-pt/discover" target="_blank" class="hub-pill">Red Bull TV <span>Radical</span></a>
            <a href="https://www.plex.tv/watch-free/" target="_blank" class="hub-pill">Plex TV <span>FAST</span></a>
            <a href="https://www.viki.com" target="_blank" class="hub-pill">Rakuten Viki <span>Doramas</span></a>
            <a href="https://www.crunchyroll.com" target="_blank" class="hub-pill">Crunchyroll <span>Animes</span></a>
            <a href="https://vix.com" target="_blank" class="hub-pill">ViX Cine & TV <span>Séries</span></a>
            <a href="https://www.soultv.com.br" target="_blank" class="hub-pill">Soul TV <span>Brasil</span></a>
            <a href="https://spcineplay.com.br" target="_blank" class="hub-pill">SPcine Play <span>Cinema</span></a>
            <a href="https://libreflix.org" target="_blank" class="hub-pill">Libreflix <span>Livre</span></a>
        </div>
    </div>

    <script>
        const CANAIS = {json.dumps(canais_json, ensure_ascii=False)};
        let canalAtual = null;
        let filtroAtivo = 'discovery';
        let termoBusca = '';

        const video = document.getElementById('mainVideo');
        const toast = document.getElementById('toastStatus');
        const toastMsg = document.getElementById('toastMsg');
        const liveDot = document.getElementById('liveDot');
        let hls = null;

        function sintonizar(c) {{
            canalAtual = c;
            toast.classList.remove('active');
            liveDot.style.background = 'var(--emerald)';

            document.getElementById('nowTitle').textContent = c.nome;
            document.getElementById('nowMeta').textContent = `${{c.regiao}} • ${{c.categoria}} • ${{c.qualidade}} • Latência: ${{c.latencia}}ms`;

            document.querySelectorAll('.stream-card').forEach(el => el.classList.remove('active'));
            const card = document.getElementById('card-' + c.id);
            if (card) card.classList.add('active');

            // Resolver URL inteligente com proxy local se estiver rodando em localhost
            let finalUrl = c.url;
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {{
                if (c.cors_star !== 1) {{
                    finalUrl = '/proxy?url=' + encodeURIComponent(c.url);
                }}
            }}

            if (Hls.isSupported()) {{
                if (hls) hls.destroy();
                hls = new Hls({{
                    enableWorker: true,
                    lowLatencyMode: true,
                    backBufferLength: 60
                }});
                hls.loadSource(finalUrl);
                hls.attachMedia(video);

                hls.on(Hls.Events.MANIFEST_PARSED, function () {{
                    video.play().catch(e => console.log('Autoplay:', e));
                }});

                hls.on(Hls.Events.ERROR, function (evt, data) {{
                    if (data.fatal) {{
                        console.warn('Erro de reprodução HLS:', data);
                        // Se não estiver em localhost, tenta rodar o proxy ou dá aviso claro
                        if (window.location.protocol === 'file:') {{
                            toastMsg.textContent = 'Canal de TV a cabo com trava de segurança do navegador. Abra o arquivo INICIAR_TV_TOTAL.bat na Área de Trabalho para desbloquear!';
                            toast.classList.add('active');
                            liveDot.style.background = '#f59e0b';
                        }} else {{
                            // Tenta carregar pelo proxy local automaticamente
                            hls.loadSource('/proxy?url=' + encodeURIComponent(c.url));
                        }}
                    }}
                }});
            }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                video.src = finalUrl;
                video.play().catch(e => console.log('Autoplay:', e));
            }}
        }}

        function normalizar(t) {{
            return (t || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
        }}

        function renderizar() {{
            const lista = document.getElementById('channelList');
            lista.innerHTML = '';
            const busca = normalizar(termoBusca);

            const filtrados = CANAIS.filter(c => {{
                if (filtroAtivo === 'discovery') {{
                    const n = normalizar(c.nome);
                    const cat = normalizar(c.categoria);
                    if (!n.includes('discovery') && !n.includes('animal planet') && !n.includes('turbo') && !n.includes('food network') && !n.includes('tlc') && !n.includes('hgtv') && !cat.includes('discovery')) return false;
                }} else if (filtroAtivo === 'direto' && c.cors_star !== 1) return false;
                else if (filtroAtivo === 'br' && !normalizar(c.pais).includes('brasil')) return false;
                else if (filtroAtivo === 'sp' && !normalizar(c.regiao).includes('sao paulo') && !normalizar(c.regiao).includes('rio de janeiro')) return false;
                else if (filtroAtivo === 'sul' && !normalizar(c.regiao).includes('sul')) return false;

                if (busca) {{
                    const mNome = normalizar(c.nome).includes(busca);
                    const mReg = normalizar(c.regiao).includes(busca);
                    const mCat = normalizar(c.categoria).includes(busca);
                    if (!mNome && !mReg && !mCat) return false;
                }}
                return true;
            }});

            if (filtrados.length === 0) {{
                lista.innerHTML = '<div style="color:var(--text-dim); padding:20px; text-align:center; font-size:0.85rem;">Nenhum canal encontrado.</div>';
                return;
            }}

            filtrados.slice(0, 200).forEach(c => {{
                const el = document.createElement('div');
                el.className = 'stream-card' + (canalAtual && canalAtual.id === c.id ? ' active' : '');
                el.id = 'card-' + c.id;
                el.onclick = () => sintonizar(c);

                el.innerHTML = `
                    <div class="stream-meta-info">
                        <div class="stream-name">${{c.nome}}</div>
                        <div class="stream-sub">
                            ${{c.cors_star === 1 ? '<span class="tag-web">🟢 Direto</span> • ' : ''}}
                            <span>${{c.regiao}}</span>
                        </div>
                    </div>
                    <span class="tag-res">${{c.qualidade}}</span>
                `;
                lista.appendChild(el);
            }});
        }}

        document.getElementById('searchInput').addEventListener('input', (e) => {{
            termoBusca = e.target.value;
            renderizar();
        }});

        document.querySelectorAll('.nav-tab').forEach(tab => {{
            tab.addEventListener('click', () => {{
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                filtroAtivo = tab.getAttribute('data-filter');
                renderizar();
            }});
        }});

        function copiarLink() {{
            if (!canalAtual) return alert('Selecione um canal!');
            navigator.clipboard.writeText(canalAtual.url).then(() => {{
                alert('Link do stream copiado com sucesso!\\n' + canalAtual.url);
            }});
        }}

        function proximoCanal() {{
            if (!canalAtual) return;
            const idx = CANAIS.findIndex(c => c.id === canalAtual.id);
            if (idx !== -1 && idx + 1 < CANAIS.length) {{
                sintonizar(CANAIS[idx + 1]);
            }}
        }}

        renderizar();
        const inicial = CANAIS.find(c => c.cors_star === 1 && c.nome.toLowerCase().includes('amazon sat')) || CANAIS[0];
        if (inicial) {{
            sintonizar(inicial);
        }}
    </script>
</body>
</html>
'''

# Gravar nos arquivos
desktop_html = r'C:\Users\jonas\Desktop\ASSISTIR_TV.html'
with open(desktop_html, 'w', encoding='utf-8') as f:
    f.write(html_code)

projeto_html = r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\index.html'
with open(projeto_html, 'w', encoding='utf-8') as f:
    f.write(html_code)

print("ASSISTIR_TV.html e index.html atualizados com aba exclusiva Discovery e remoção dos geo-blocked!")
