import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
DB_PATH = BASE_DIR / "saida" / "banco_iptv.db"
DESKTOP_DIR = Path(r"C:\Users\jonas\Desktop")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Canais Discovery 100% M3U8 (compatíveis nativamente com Hls.js)
canais_discovery_m3u8 = [
    {
        "nome": "Discovery Channel (Digital HLS)",
        "url": "http://hls1.sua.tv:80/live/discoverychannelfhd/s.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-channel-br.png",
        "categoria": "🔬 Documentários",
        "qualidade": "Digital",
        "latencia": 45,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Kids (Digital HLS)",
        "url": "http://181.224.200.5:2277/play/a00o/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-kids-br.png",
        "categoria": "🧸 Infantis",
        "qualidade": "Digital",
        "latencia": 40,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Turbo (Digital HLS)",
        "url": "http://38.134.250.110:8000/play/a01y/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-turbo-br.png",
        "categoria": "🚗 Motores",
        "qualidade": "Digital",
        "latencia": 50,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Home & Health (Digital HLS)",
        "url": "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/39.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-home-and-health-br.png",
        "categoria": "🏠 Estilo de Vida",
        "qualidade": "Digital",
        "latencia": 55,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Animal Planet (Digital HLS)",
        "url": "http://190.128.214.97:64333/play/a01n/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/animal-planet-br.png",
        "categoria": "🦁 Natureza",
        "qualidade": "Digital",
        "latencia": 48,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Investigation Discovery ID (Digital HLS)",
        "url": "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/41.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/investigation-discovery-br.png",
        "categoria": "🔍 Investigação",
        "qualidade": "Digital",
        "latencia": 60,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Science (Digital HLS)",
        "url": "http://45.171.64.30:6060/play/a007/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-science-br.png",
        "categoria": "🔬 Ciência",
        "qualidade": "Digital",
        "latencia": 52,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Theater (Digital HLS)",
        "url": "http://181.224.200.5:2277/play/a0bj/index.m3u8",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-theater-br.png",
        "categoria": "🎬 Cultura",
        "qualidade": "Digital",
        "latencia": 50,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    }
]

# Desativar links velhos de .ts do rtv30t
c.execute("UPDATE canais SET status = 'INATIVO' WHERE url LIKE '%rtv30t.com%'")
conn.commit()

# Inserir ou atualizar os canais HLS M3U8
for ch in canais_discovery_m3u8:
    c.execute("""
        INSERT OR REPLACE INTO canais (nome, url, logo, categoria, qualidade, latencia_ms, pais, regiao, status, cors_star)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ch["nome"], ch["url"], ch["logo"], ch["categoria"], ch["qualidade"],
        ch["latencia"], ch["pais"], ch["regiao"], ch["status"], ch["cors_star"]
    ))
conn.commit()
print("Canais Discovery M3U8 ativos inseridos com sucesso!")

# Atualizar playlists M3U na Área de Trabalho
m3u_linhas = ["#EXTM3U\n"]
for ch in canais_discovery_m3u8:
    m3u_linhas.append(f'#EXTINF:-1 tvg-name="{ch["nome"]}" tvg-logo="{ch["logo"]}" group-title="{ch["categoria"]}",{ch["nome"]}\n{ch["url"]}\n')

m3u_str = "".join(m3u_linhas)
(DESKTOP_DIR / "DISCOVERY_PT_BR_DUBLADO.m3u").write_text(m3u_str, encoding="utf-8")
(DESKTOP_DIR / "CANAIS_DISCOVERY_2026.m3u").write_text(m3u_str, encoding="utf-8")
print("Playlists M3U no Desktop atualizadas para M3U8!")

# Selecionar todos os canais ativos para o Player
c.execute("""
    SELECT id, nome, url, logo, categoria, qualidade, latencia_ms, pais, regiao, cors_star
    FROM canais
    WHERE status = 'ATIVO' AND url LIKE '%.m3u8%'
    ORDER BY 
        CASE 
            WHEN nome LIKE '%Discovery%' THEN 0
            WHEN nome LIKE '%Amazon Sat%' THEN 1
            WHEN cors_star = 1 THEN 2
            ELSE 3
        END,
        latencia_ms ASC
""")
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
        'qualidade': r[5] or 'Digital',
        'latencia': int(r[6] or 60),
        'pais': r[7] or '🇧🇷 Brasil',
        'regiao': r[8] or 'Nacional',
        'cors_star': r[9]
    })

print(f"Total de canais M3U8 puros carregados: {len(canais_json)}")

# Gerar HTML 100% HLS.JS PURO (Zero travamentos, Zero conflitos MSE)
html_puro = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CENTRAL DE TV DIGITAL 2026 - FLUXO RÁPIDO</title>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0a0e17;
            --surface: #121826;
            --surface-hover: #1e293b;
            --primary: #10b981;
            --primary-glow: rgba(16, 185, 129, 0.35);
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
            overflow-x: hidden;
        }}
        header {{
            background: rgba(18, 24, 38, 0.9);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-subtle);
            padding: 12px 28px;
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
        .brand-logo {{
            background: linear-gradient(135deg, #10b981, #059669);
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            box-shadow: 0 0 16px var(--primary-glow);
        }}
        .brand-text h1 {{
            font-size: 1.1rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            text-transform: uppercase;
        }}
        .brand-text span {{
            font-size: 0.72rem;
            color: var(--emerald);
            font-weight: 700;
        }}
        .badge-status {{
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--emerald);
            color: var(--emerald);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 700;
        }}
        .search-container {{
            position: relative;
            width: 360px;
        }}
        .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-dim);
            font-size: 0.9rem;
        }}
        .search-box {{
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-subtle);
            padding: 9px 16px 9px 38px;
            border-radius: 999px;
            color: var(--text-main);
            font-size: 0.85rem;
            outline: none;
            transition: all 0.2s ease;
        }}
        .search-box:focus {{
            border-color: var(--emerald);
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 12px var(--primary-glow);
        }}
        .stage {{
            display: grid;
            grid-template-columns: 1fr 420px;
            gap: 20px;
            padding: 20px 28px;
            flex: 1;
            max-width: 1920px;
            margin: 0 auto;
            width: 100%;
        }}
        .cinema-player {{
            background: #000;
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid var(--border-subtle);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
        }}
        .screen-frame {{
            position: relative;
            width: 100%;
            background: #000;
            aspect-ratio: 16 / 9;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        video {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            outline: none;
            cursor: pointer;
        }}
        .toast-status {{
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(18, 24, 38, 0.95);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 10px 18px;
            border-radius: 30px;
            font-size: 0.82rem;
            color: #f8fafc;
            display: none;
            align-items: center;
            gap: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            z-index: 10;
        }}
        .toast-status.active {{
            display: flex;
        }}
        .toast-btn {{
            background: var(--primary);
            color: #000;
            border: none;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            cursor: pointer;
        }}
        .player-bar {{
            padding: 14px 20px;
            background: var(--surface);
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid var(--border-subtle);
        }}
        .current-channel-title {{
            font-size: 1.05rem;
            font-weight: 700;
        }}
        .current-channel-sub {{
            font-size: 0.78rem;
            color: var(--text-dim);
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 4px;
        }}
        .live-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--emerald);
            display: inline-block;
            box-shadow: 0 0 8px var(--emerald);
        }}
        .player-controls {{
            display: flex;
            gap: 10px;
        }}
        .btn-ctrl {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-subtle);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn-ctrl:hover {{
            background: var(--surface-hover);
            border-color: var(--emerald);
        }}
        .sidebar-channels {{
            background: var(--surface);
            border-radius: 16px;
            border: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            height: calc(100vh - 110px);
        }}
        .nav-tabs {{
            display: flex;
            background: rgba(0, 0, 0, 0.2);
            padding: 8px;
            gap: 6px;
            border-bottom: 1px solid var(--border-subtle);
            overflow-x: auto;
        }}
        .nav-tab {{
            background: transparent;
            border: none;
            color: var(--text-dim);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.76rem;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        .nav-tab.active {{
            background: var(--emerald);
            color: #000;
            font-weight: 800;
            box-shadow: 0 0 12px var(--primary-glow);
        }}
        .channel-stream-list {{
            overflow-y: auto;
            flex: 1;
            padding: 8px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .stream-card {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid transparent;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .stream-card:hover {{
            background: var(--surface-hover);
            border-color: rgba(255, 255, 255, 0.1);
        }}
        .stream-card.active {{
            background: rgba(16, 185, 129, 0.15);
            border-color: var(--emerald);
        }}
        .stream-name {{
            font-size: 0.88rem;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 250px;
        }}
        .stream-sub {{
            font-size: 0.72rem;
            color: var(--text-dim);
            display: flex;
            gap: 6px;
            align-items: center;
        }}
        .tag-digital {{
            color: var(--emerald);
            font-weight: 700;
        }}
        .tag-res {{
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 4px;
            background: rgba(16, 185, 129, 0.15);
            color: var(--emerald);
            font-weight: 700;
        }}
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-logo">📺</div>
            <div class="brand-text">
                <h1>CENTRAL DE TV DIGITAL</h1>
                <span>Motor HLS Puro • Zero Travamentos</span>
            </div>
            <div class="badge-status">✓ Conexão Ativa</div>
        </div>

        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" class="search-box" placeholder="Buscar canal rápido (Discovery, Kids, Turbo, Band)...">
        </div>
    </header>

    <div class="stage">
        
        <div class="cinema-player">
            <div class="screen-frame">
                <video id="mainVideo" controls autoplay playsinline muted></video>
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
                        <span id="nowMeta">Iniciando transmissão digital...</span>
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
                <button class="nav-tab active" data-filter="discovery">🌟 Discovery HLS (8)</button>
                <button class="nav-tab" data-filter="digital">⚡ Só Digital (Mais Leve)</button>
                <button class="nav-tab" data-filter="br">🇧🇷 Brasil Digital</button>
                <button class="nav-tab" data-filter="todos">Todos os Canais</button>
            </div>

            <div class="channel-stream-list" id="channelList"></div>
        </div>

    </div>

    <script>
        // Redirecionamento automático se aberto como arquivo
        if (window.location.protocol === 'file:') {{
            fetch('http://localhost:8080/index.html', {{ mode: 'no-cors' }})
                .then(() => {{ window.location.href = 'http://localhost:8080/'; }})
                .catch(() => {{ console.log('Servidor aguardando.'); }});
        }}

        const CANAIS = {json.dumps(canais_json, ensure_ascii=False)};
        let canalAtual = null;
        let filtroAtivo = 'discovery';
        let termoBusca = '';

        const video = document.getElementById('mainVideo');
        const toast = document.getElementById('toastStatus');
        const toastMsg = document.getElementById('toastMsg');
        const liveDot = document.getElementById('liveDot');
        
        let hls = null;

        // Ativar áudio no primeiro clique do usuário
        document.body.addEventListener('click', function () {{
            if (video.muted) {{
                video.muted = false;
                console.log('Áudio ativado com sucesso pelo clique!');
            }}
        }}, {{ once: true }});

        function resolverUrl(url) {{
            // Roteia SEMPRE pelo proxy local na porta 8080 para remover 100% de travas de CORS
            return 'http://localhost:8080/proxy?url=' + encodeURIComponent(url);
        }}

        function sintonizar(c) {{
            canalAtual = c;
            toastMsg.textContent = 'Sintonizando ' + c.nome + '...';
            toast.classList.add('active');
            liveDot.style.background = 'var(--amber)';

            document.getElementById('nowTitle').textContent = c.nome;
            document.getElementById('nowMeta').textContent = `${{c.regiao}} • ${{c.categoria}} • Latência: ${{c.latencia}}ms • HLS Puro`;

            document.querySelectorAll('.stream-card').forEach(el => el.classList.remove('active'));
            const card = document.getElementById('card-' + c.id);
            if (card) card.classList.add('active');

            // Destruir player anterior e limpar MediaSource completamente
            if (hls) {{
                hls.destroy();
                hls = null;
            }}
            video.pause();
            video.removeAttribute('src');
            video.load();

            const targetUrl = resolverUrl(c.url);

            if (Hls.isSupported()) {{
                hls = new Hls({{
                    enableWorker: true,
                    lowLatencyMode: true,
                    backBufferLength: 30,
                    maxBufferLength: 10
                }});
                hls.loadSource(targetUrl);
                hls.attachMedia(video);

                hls.on(Hls.Events.MANIFEST_PARSED, function () {{
                    video.play().catch(e => console.log('Autoplay:', e));
                }});

                video.onplaying = function () {{
                    toast.classList.remove('active');
                    liveDot.style.background = 'var(--emerald)';
                    console.log('Reproduzindo com sucesso!');
                }};

                hls.on(Hls.Events.ERROR, function (evt, data) {{
                    if (data.fatal) {{
                        console.warn('Erro Hls recuperável:', data);
                        switch (data.type) {{
                            case Hls.ErrorTypes.NETWORK_ERROR:
                                hls.startLoad();
                                break;
                            case Hls.ErrorTypes.MEDIA_ERROR:
                                hls.recoverMediaError();
                                break;
                            default:
                                if (hls) hls.destroy();
                                break;
                        }}
                    }}
                }});
            }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                video.src = targetUrl;
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
                    if (!normalizar(c.nome).includes('discovery') && !normalizar(c.nome).includes('animal')) return false;
                }}
                if (filtroAtivo === 'digital') {{
                    if (c.qualidade !== 'Digital' && c.qualidade !== 'HD') return false;
                }}
                if (filtroAtivo === 'br') {{
                    if (!normalizar(c.pais).includes('brasil')) return false;
                }}

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

            filtrados.slice(0, 150).forEach(c => {{
                const el = document.createElement('div');
                el.className = 'stream-card' + (canalAtual && canalAtual.id === c.id ? ' active' : '');
                el.id = 'card-' + c.id;
                el.onclick = () => sintonizar(c);

                el.innerHTML = `
                    <div class="stream-meta-info">
                        <div class="stream-name">${{c.nome}}</div>
                        <div class="stream-sub">
                            <span class="tag-digital">⚡ HLS</span> •
                            <span>${{c.categoria.split(' ')[1] || c.categoria}}</span>
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

        // Inicializar com canal ultra-rápido instantâneo (Discovery Channel HLS)
        renderizar();
        const inicial = CANAIS.find(c => c.nome.toLowerCase().includes('discovery channel (digital hls)')) || CANAIS[0];
        if (inicial) {{
            sintonizar(inicial);
        }}
    </script>
</body>
</html>
"""

(BASE_DIR / "saida" / "index.html").write_text(html_puro, encoding="utf-8")
(DESKTOP_DIR / "ASSISTIR_TV.html").write_text(html_puro, encoding="utf-8")
print("Novo ecossistema 100% HLS puro gerado com sucesso!")
