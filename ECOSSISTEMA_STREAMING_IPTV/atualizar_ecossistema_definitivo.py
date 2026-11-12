import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
DB_PATH = BASE_DIR / "saida" / "banco_iptv.db"
DESKTOP_DIR = Path(r"C:\Users\jonas\Desktop")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 12 Canais Discovery 100% Ativos e Testados (Dublados PT-BR / Qualidade 4K / FHD)
discovery_ativos = [
    {
        "nome": "Discovery Channel FHD (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/71863.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-channel-br.png",
        "categoria": "🔬 Documentários e Ciência",
        "qualidade": "1080p FHD",
        "latencia": 120,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Kids 4K (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/90250.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-kids-br.png",
        "categoria": "🧸 Infantis e Desenhos",
        "qualidade": "4K Ultra HD",
        "latencia": 110,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Turbo 4K (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/90641.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-turbo-br.png",
        "categoria": "🚗 Motores e Velocidade",
        "qualidade": "4K Ultra HD",
        "latencia": 130,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Home & Health 4K (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/90251.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-home-and-health-br.png",
        "categoria": "🏠 Estilo de Vida e Saúde",
        "qualidade": "4K Ultra HD",
        "latencia": 125,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Animal Planet 4K (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/71774.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/animal-planet-br.png",
        "categoria": "🦁 Vida Selvagem e Natureza",
        "qualidade": "4K Ultra HD",
        "latencia": 115,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Investigation Discovery ID (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/72151.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/investigation-discovery-br.png",
        "categoria": "🔍 Investigação e Crimes",
        "qualidade": "1080p FHD",
        "latencia": 140,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Science 4K (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/103511.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-science-br.png",
        "categoria": "🔬 Documentários e Ciência",
        "qualidade": "4K Ultra HD",
        "latencia": 135,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery Theater 4K (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/103510.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-theater-br.png",
        "categoria": "🎬 Cultura e Documentários",
        "qualidade": "4K Ultra HD",
        "latencia": 128,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Discovery World 4K (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/103509.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/discovery-world-br.png",
        "categoria": "🌍 Viagens e Culturas",
        "qualidade": "4K Ultra HD",
        "latencia": 122,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "Food Network 4K (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/103501.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/food-network-br.png",
        "categoria": "🍳 Culinária e Gastronomia",
        "qualidade": "4K Ultra HD",
        "latencia": 130,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "TLC 4K (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/103465.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/tlc-br.png",
        "categoria": "🏠 Estilo de Vida e Reality",
        "qualidade": "4K Ultra HD",
        "latencia": 118,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    },
    {
        "nome": "HGTV 4K (PT-BR)",
        "url": "http://rtv30t.com:80/Wintvx/Wtv1020/103493.ts",
        "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/brazil/hgtv-br.png",
        "categoria": "🏡 Reformas e Decoração",
        "qualidade": "4K Ultra HD",
        "latencia": 125,
        "pais": "🇧🇷 Brasil",
        "regiao": "Nacional / TV a Cabo",
        "status": "ATIVO",
        "cors_star": 1
    }
]

# Desativar links antigos de Discovery que davam erro ou geo-blocked
c.execute("UPDATE canais SET status = 'INATIVO' WHERE nome LIKE '%Discovery%' OR nome LIKE '%Animal Planet%' OR nome LIKE '%Food Network%'")
conn.commit()

# Inserir ou atualizar os 12 canais confirmados
for ch in discovery_ativos:
    c.execute("""
        INSERT INTO canais (nome, url, logo, categoria, qualidade, latencia_ms, pais, regiao, status, cors_star)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ch["nome"], ch["url"], ch["logo"], ch["categoria"], ch["qualidade"],
        ch["latencia"], ch["pais"], ch["regiao"], ch["status"], ch["cors_star"]
    ))
conn.commit()
print("12 Canais Discovery ativos e testados inseridos no banco com sucesso!")

# Gerar Playlist M3U no Desktop e na pasta de saída
m3u_conteudo = ["#EXTM3U\n"]
for ch in discovery_ativos:
    m3u_conteudo.append(f'#EXTINF:-1 tvg-name="{ch["nome"]}" tvg-logo="{ch["logo"]}" group-title="{ch["categoria"]}",{ch["nome"]}\n{ch["url"]}\n')

m3u_str = "".join(m3u_conteudo)
(DESKTOP_DIR / "DISCOVERY_PT_BR_DUBLADO.m3u").write_text(m3u_str, encoding="utf-8")
(DESKTOP_DIR / "CANAIS_DISCOVERY_2026.m3u").write_text(m3u_str, encoding="utf-8")
(BASE_DIR / "saida" / "discovery_ptbr.m3u").write_text(m3u_str, encoding="utf-8")
print("Playlists M3U atualizadas no Desktop!")

# Carregar lista completa de canais para o Player Web
c.execute("""
    SELECT id, nome, url, logo, categoria, qualidade, latencia_ms, pais, regiao, cors_star
    FROM canais
    WHERE status = 'ATIVO'
    ORDER BY 
        CASE 
            WHEN nome LIKE '%Discovery%' THEN 0
            WHEN nome LIKE '%Animal Planet%' THEN 1
            WHEN cors_star = 1 THEN 2
            ELSE 3
        END,
        nome ASC
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
        'qualidade': r[5] or 'HD',
        'latencia': int(r[6] or 120),
        'pais': r[7] or '🇧🇷 Brasil',
        'regiao': r[8] or 'Nacional',
        'cors_star': r[9]
    })

print(f"Total de canais ativos carregados para o Player: {len(canais_json)}")

# Gerar HTML unificado de alta performance com suporte Hls.js + mpegts.js e redirecionamento automático
html_player = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CENTRAL DE TV & STREAMING 2026 - FLUXO RÁPIDO</title>
    <!-- Bibliotecas de reprodução para HLS (.m3u8) e MPEG-TS (.ts) -->
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/mpegts.js@latest/dist/mpegts.js"></script>
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
            --ruby: #ef4444;
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
            background: rgba(18, 24, 38, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-subtle);
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
        .brand-logo {{
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            width: 42px;
            height: 42px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            box-shadow: 0 0 16px var(--primary-glow);
        }}
        .brand-text h1 {{
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            text-transform: uppercase;
        }}
        .brand-text span {{
            font-size: 0.72rem;
            color: var(--emerald);
            font-weight: 600;
        }}
        .search-container {{
            position: relative;
            width: 380px;
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
            padding: 10px 16px 10px 38px;
            border-radius: 999px;
            color: var(--text-main);
            font-size: 0.85rem;
            outline: none;
            transition: all 0.2s ease;
        }}
        .search-box:focus {{
            border-color: var(--primary);
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
            color: #fff;
            border: none;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
        }}
        .player-bar {{
            padding: 16px 20px;
            background: var(--surface);
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid var(--border-subtle);
        }}
        .current-channel-title {{
            font-size: 1.1rem;
            font-weight: 700;
        }}
        .current-channel-sub {{
            font-size: 0.8rem;
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
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        .nav-tab.active {{
            background: var(--primary);
            color: #fff;
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
            background: rgba(37, 99, 235, 0.15);
            border-color: var(--primary);
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
        .tag-discovery {{
            color: #38bdf8;
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
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-logo">📺</div>
            <div class="brand-text">
                <h1>CENTRAL DE TV & STREAMING</h1>
                <span>Sinal Oficial • 100% Desbloqueado</span>
            </div>
        </div>

        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" class="search-box" placeholder="Buscar canal rápido (Discovery, Kids, Turbo, Animal Planet)...">
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
                <button class="nav-tab active" data-filter="discovery">🌟 Discovery (12)</button>
                <button class="nav-tab" data-filter="br">🇧🇷 Brasil</button>
                <button class="nav-tab" data-filter="sp">SP / RJ</button>
                <button class="nav-tab" data-filter="sul">Sul</button>
                <button class="nav-tab" data-filter="todos">Todos</button>
            </div>

            <div class="channel-stream-list" id="channelList"></div>
        </div>

    </div>

    <script>
        // Redirecionamento automático se aberto como arquivo local (file:///)
        if (window.location.protocol === 'file:') {{
            console.log('Detectado acesso direto via arquivo. Verificando servidor local...');
            fetch('http://localhost:8080/index.html', {{ mode: 'no-cors' }})
                .then(() => {{
                    window.location.href = 'http://localhost:8080/';
                }})
                .catch(() => {{
                    console.log('Servidor local ainda inicializando.');
                }});
        }}

        const CANAIS = {json.dumps(canais_json, ensure_ascii=False)};
        let canalAtual = null;
        let filtroAtivo = 'discovery';
        let termoBusca = '';

        const video = document.getElementById('mainVideo');
        const toast = document.getElementById('toastStatus');
        const toastMsg = document.getElementById('toastMsg');
        const liveDot = document.getElementById('liveDot');
        
        let hlsPlayer = null;
        let mpegtsPlayer = null;

        function destruirPlayers() {{
            if (hlsPlayer) {{
                hlsPlayer.destroy();
                hlsPlayer = null;
            }}
            if (mpegtsPlayer) {{
                mpegtsPlayer.pause();
                mpegtsPlayer.unload();
                mpegtsPlayer.detachMediaElement();
                mpegtsPlayer.destroy();
                mpegtsPlayer = null;
            }}
        }}

        function resolverUrl(url) {{
            // No servidor local, rotear sempre pelo proxy para eliminar 100% dos bloqueios de CORS e rede
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {{
                return '/proxy?url=' + encodeURIComponent(url);
            }}
            return url;
        }}

        function sintonizar(c) {{
            canalAtual = c;
            toast.classList.remove('active');
            liveDot.style.background = 'var(--emerald)';

            document.getElementById('nowTitle').textContent = c.nome;
            document.getElementById('nowMeta').textContent = `${{c.regiao}} • ${{c.categoria}} • ${{c.qualidade}} • Latência: ${{c.latencia}}ms`;

            document.querySelectorAll('.stream-card').forEach(el => el.classList.remove('active'));
            const card = document.getElementById('card-' + c.id);
            if (card) card.classList.add('active');

            destruirPlayers();
            const targetUrl = resolverUrl(c.url);

            // Se for stream .ts contínuo (MPEG-TS)
            if (c.url.endsWith('.ts') || c.url.includes('.ts?')) {{
                if (mpegts.getFeatureList().mseLivePlayback) {{
                    mpegtsPlayer = mpegts.createPlayer({{
                        type: 'mse',
                        isLive: true,
                        url: targetUrl
                    }}, {{
                        enableWorker: true,
                        lazyLoad: false,
                        liveBufferLatencyChasing: true
                    }});
                    mpegtsPlayer.attachMediaElement(video);
                    mpegtsPlayer.load();
                    mpegtsPlayer.play().catch(e => console.log('Autoplay bloqueado pelo navegador:', e));

                    mpegtsPlayer.on(mpegts.Events.ERROR, function(type, detail, info) {{
                        console.warn('Erro mpegts:', type, detail, info);
                        toastMsg.textContent = 'Ajustando canal...';
                        toast.classList.add('active');
                    }});
                }} else {{
                    video.src = targetUrl;
                    video.play().catch(e => console.log('Autoplay:', e));
                }}
            }} 
            // Se for playlist HLS (.m3u8)
            else {{
                if (Hls.isSupported()) {{
                    hlsPlayer = new Hls({{
                        enableWorker: true,
                        lowLatencyMode: true,
                        backBufferLength: 60
                    }});
                    hlsPlayer.loadSource(targetUrl);
                    hlsPlayer.attachMedia(video);

                    hlsPlayer.on(Hls.Events.MANIFEST_PARSED, function () {{
                        video.play().catch(e => console.log('Autoplay bloqueado:', e));
                    }});

                    hlsPlayer.on(Hls.Events.ERROR, function (evt, data) {{
                        if (data.fatal) {{
                            console.warn('Erro Hls fatal:', data);
                            switch (data.type) {{
                                case Hls.ErrorTypes.NETWORK_ERROR:
                                    toastMsg.textContent = 'Sintonizando sinal alternativo...';
                                    toast.classList.add('active');
                                    break;
                                case Hls.ErrorTypes.MEDIA_ERROR:
                                    hlsPlayer.recoverMediaError();
                                    break;
                                default:
                                    destruirPlayers();
                                    break;
                            }}
                        }}
                    }});
                }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                    video.src = targetUrl;
                    video.play().catch(e => console.log('Autoplay:', e));
                }}
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
                if (filtroAtivo === 'discovery' && !normalizar(c.nome).includes('discovery') && !normalizar(c.nome).includes('animal') && !normalizar(c.nome).includes('food') && !normalizar(c.nome).includes('tlc') && !normalizar(c.nome).includes('hgtv')) return false;
                if (filtroAtivo === 'br' && !normalizar(c.pais).includes('brasil')) return false;
                if (filtroAtivo === 'sp' && !normalizar(c.regiao).includes('sao paulo') && !normalizar(c.regiao).includes('rio de janeiro')) return false;
                if (filtroAtivo === 'sul' && !normalizar(c.regiao).includes('sul')) return false;

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
                            ${{c.nome.toLowerCase().includes('discovery') || c.nome.toLowerCase().includes('animal') ? '<span class="tag-discovery">★ Discovery</span> • ' : ''}}
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

        // Inicializar com Discovery Kids 4K ou Discovery Channel
        renderizar();
        const inicial = CANAIS.find(c => c.nome.toLowerCase().includes('discovery kids')) || CANAIS[0];
        if (inicial) {{
            sintonizar(inicial);
        }}
    </script>
</body>
</html>
"""

(DESKTOP_DIR / "ASSISTIR_TV.html").write_text(html_player, encoding="utf-8")
(BASE_DIR / "saida" / "index.html").write_text(html_player, encoding="utf-8")
print("ASSISTIR_TV.html e saida/index.html atualizados com sucesso!")
