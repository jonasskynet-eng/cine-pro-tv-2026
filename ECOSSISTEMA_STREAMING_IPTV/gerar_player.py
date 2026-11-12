import json
from pathlib import Path

json_path = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\canais_leves.json")
with open(json_path, "r", encoding="utf-8") as f:
    canais_data = json.load(f)

json_str = json.dumps(canais_data, ensure_ascii=False)

html_template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CENTRAL DE TV DIGITAL - Modo Leve 2026</title>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <style>
        :root {
            --bg-base: #0a0f1d;
            --bg-surface: #111827;
            --bg-card: #1e293b;
            --bg-card-hover: #334155;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --emerald: #10b981;
            --amber: #f59e0b;
            --rose: #e11d48;
            --gold: #fbbf24;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            background: var(--bg-base);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: background 0.3s;
        }
        /* MODO CINEMA */
        body.cinema-mode header,
        body.cinema-mode .sidebar-channels {
            opacity: 0.08;
            transition: opacity 0.3s ease;
        }
        body.cinema-mode header:hover,
        body.cinema-mode .sidebar-channels:hover {
            opacity: 1;
        }
        header {
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border);
            padding: 10px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            z-index: 20;
            transition: opacity 0.2s;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .brand-logo {
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, #10b981, #059669);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
        }
        .brand-text h1 {
            font-size: 16px;
            font-weight: 800;
            letter-spacing: -0.3px;
            color: #fff;
        }
        .brand-text span {
            font-size: 11px;
            color: var(--emerald);
            display: flex;
            align-items: center;
            gap: 4px;
            font-weight: 600;
        }
        .search-container {
            flex: 1;
            max-width: 440px;
            position: relative;
        }
        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            font-size: 14px;
            pointer-events: none;
        }
        .search-box {
            width: 100%;
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 9px 12px 9px 36px;
            border-radius: 8px;
            color: var(--text-main);
            font-size: 13px;
            outline: none;
            transition: all 0.2s;
        }
        .search-box:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25);
        }
        .header-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .btn-header {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 7px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }
        .btn-header:hover {
            background: var(--bg-card-hover);
            border-color: var(--primary);
        }
        .stage {
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 390px;
            overflow: hidden;
        }
        .cinema-player {
            display: flex;
            flex-direction: column;
            background: #000;
            position: relative;
        }
        .screen-frame {
            position: relative;
            flex: 1;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        video {
            width: 100%;
            height: 100%;
            object-fit: contain;
            outline: none;
            cursor: pointer;
        }
        /* HUD FLUTUANTE DE COMANDOS */
        .hud-feedback {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.85);
            background: rgba(15, 23, 42, 0.92);
            border: 1px solid var(--primary);
            color: #fff;
            padding: 14px 28px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 10px;
            pointer-events: none;
            opacity: 0;
            z-index: 100;
            transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
        }
        .hud-feedback.show {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }
        .play-overlay {
            position: absolute;
            inset: 0;
            background: rgba(0, 0, 0, 0.78);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 16px;
            cursor: pointer;
            z-index: 50;
            transition: all 0.2s ease;
            backdrop-filter: blur(3px);
        }
        .play-overlay:hover .pulse-circle {
            transform: scale(1.12);
            box-shadow: 0 0 45px rgba(37, 99, 235, 1);
        }
        .pulse-circle {
            width: 86px;
            height: 86px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 32px rgba(37, 99, 235, 0.75);
            transition: all 0.25s ease;
        }
        .play-overlay-text {
            text-align: center;
            color: #fff;
        }
        .overlay-main-text {
            font-size: 19px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .overlay-sub-text {
            font-size: 13px;
            color: #cbd5e1;
            margin-top: 5px;
        }
        .badge-unmute {
            position: absolute;
            top: 16px;
            right: 16px;
            background: var(--rose);
            color: #fff;
            border: none;
            padding: 9px 18px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            z-index: 60;
            display: none;
            align-items: center;
            gap: 6px;
            box-shadow: 0 4px 18px rgba(225, 29, 72, 0.65);
            animation: pulse-red 2s infinite;
        }
        @keyframes pulse-red {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.06); }
        }
        .toast-status {
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background: rgba(17, 24, 39, 0.95);
            border: 1px solid var(--border);
            padding: 10px 16px;
            border-radius: 8px;
            display: none;
            align-items: center;
            justify-content: space-between;
            color: var(--text-main);
            font-size: 13px;
            z-index: 40;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }
        .toast-status.active {
            display: flex;
        }
        .toast-btn {
            background: var(--primary);
            color: #fff;
            border: none;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
        }
        .player-bar {
            background: var(--bg-surface);
            border-top: 1px solid var(--border);
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }
        .channel-header {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }
        .channel-title-row {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .current-channel-title {
            font-size: 16px;
            font-weight: 800;
            color: var(--text-main);
        }
        .btn-fav-current {
            background: transparent;
            border: none;
            font-size: 17px;
            cursor: pointer;
            color: var(--text-muted);
            transition: all 0.2s;
        }
        .btn-fav-current.active {
            color: var(--gold);
            transform: scale(1.15);
        }
        .current-channel-sub {
            font-size: 12px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .epg-badge {
            background: rgba(37, 99, 235, 0.2);
            color: #60a5fa;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
        }
        .live-dot {
            width: 8px;
            height: 8px;
            background: var(--emerald);
            border-radius: 50%;
            display: inline-block;
        }
        .player-controls {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .btn-ctrl {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }
        .btn-ctrl:hover {
            background: var(--bg-card-hover);
            border-color: var(--primary);
        }
        .sidebar-channels {
            background: var(--bg-surface);
            border-left: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow: hidden;
            transition: opacity 0.2s;
        }
        .nav-tabs {
            display: flex;
            background: var(--bg-base);
            padding: 8px;
            gap: 6px;
            border-bottom: 1px solid var(--border);
            overflow-x: auto;
        }
        .nav-tab {
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 7px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
        }
        .nav-tab.active {
            background: var(--primary);
            color: #fff;
        }
        .channel-stream-list {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .stream-card {
            background: var(--bg-card);
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 10px 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .stream-card:hover {
            background: var(--bg-card-hover);
            border-color: var(--border);
        }
        .stream-card.active {
            background: rgba(37, 99, 235, 0.18);
            border-color: var(--primary);
        }
        .card-main {
            display: flex;
            flex-direction: column;
            gap: 2px;
            overflow: hidden;
        }
        .card-title-row {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .card-title {
            font-size: 13px;
            font-weight: 700;
            color: var(--text-main);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .card-meta {
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .card-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .btn-fav-card {
            background: transparent;
            border: none;
            color: #64748b;
            font-size: 15px;
            cursor: pointer;
            padding: 2px 4px;
            transition: all 0.2s;
        }
        .btn-fav-card:hover, .btn-fav-card.active {
            color: var(--gold);
            transform: scale(1.2);
        }
        .card-badge {
            background: rgba(16, 185, 129, 0.15);
            color: var(--emerald);
            font-size: 10px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 4px;
            text-transform: uppercase;
        }
        /* MODAL DE ATALHOS */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(4px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 200;
        }
        .modal-overlay.open {
            display: flex;
        }
        .modal-card {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            width: 90%;
            max-width: 520px;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.8);
        }
        .modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }
        .modal-header h2 {
            font-size: 18px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .modal-close {
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 22px;
            cursor: pointer;
        }
        .shortcut-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 14px;
        }
        .shortcut-item {
            background: var(--bg-card);
            padding: 8px 12px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 12px;
        }
        kbd {
            background: #0f172a;
            border: 1px solid var(--border);
            color: #38bdf8;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 800;
            font-family: monospace;
        }
        @media (max-width: 900px) {
            .stage {
                grid-template-columns: 1fr;
                grid-template-rows: auto 1fr;
            }
            .cinema-player {
                height: 45vh;
            }
        }
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-logo">⚡</div>
            <div class="brand-text">
                <h1>CENTRAL DE TV DIGITAL</h1>
                <span>✓ Modo Ultraleve Ativado • Zero Travamentos</span>
            </div>
        </div>

        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" class="search-box" placeholder="Buscar canal (Discovery, Kids, Turbo, HBO)...">
        </div>

        <div class="header-actions">
            <button class="btn-header" onclick="toggleCinemaMode()">🎬 Modo Cinema [C]</button>
            <button class="btn-header" onclick="toggleModalAtalhos()">⌨️ Atalhos [?]</button>
        </div>
    </header>

    <div class="stage">
        
        <div class="cinema-player">
            <div class="screen-frame" id="screenFrame">
                <video id="mainVideo" controls playsinline></video>

                <!-- Feedback Visual de Comandos (HUD) -->
                <div id="hudFeedback" class="hud-feedback">
                    <span id="hudIcon">▶</span>
                    <span id="hudText">Reproduzindo</span>
                </div>

                <!-- Overlay de Play com Som Destravado -->
                <div id="playOverlay" class="play-overlay" onclick="destravarComSom()">
                    <div class="pulse-circle">
                        <svg width="44" height="44" viewBox="0 0 24 24" fill="#ffffff"><path d="M8 5v14l11-7z"/></svg>
                    </div>
                    <div class="play-overlay-text">
                        <div class="overlay-main-text">CLIQUE PARA ASSISTIR AGORA</div>
                        <div class="overlay-sub-text">Transmissão Digital ao vivo pronta • Áudio e Vídeo 100% Liberados</div>
                    </div>
                </div>

                <!-- Botão de Desmutar Flutuante -->
                <button id="btnDesmutar" class="badge-unmute" onclick="desmutarSom()">🔊 Ativar Som</button>

                <div id="toastStatus" class="toast-status">
                    <span id="toastMsg">Sintonizando canal...</span>
                    <button class="toast-btn" onclick="copiarLink()">Copiar Link</button>
                </div>
            </div>

            <div class="player-bar">
                <div class="channel-header">
                    <div class="channel-title-row">
                        <div class="current-channel-title" id="nowTitle">Carregando canal...</div>
                        <button id="btnFavCurrent" class="btn-fav-current" title="Favoritar Canal" onclick="toggleFavoritoAtual()">★</button>
                    </div>
                    <div class="current-channel-sub">
                        <span class="live-dot" id="liveDot"></span>
                        <span id="nowMeta">Iniciando transmissão digital...</span>
                        <span class="epg-badge" id="epgBadge">Ao Vivo</span>
                    </div>
                </div>

                <div class="player-controls">
                    <button class="btn-ctrl" onclick="copiarLink()" title="Copiar link do stream">📋 Copiar Link</button>
                    <button class="btn-ctrl" onclick="anteriorCanal()" title="Canal Anterior (Seta ↑)">⏮️ Anterior</button>
                    <button class="btn-ctrl" onclick="proximoCanal()" title="Próximo Canal (Seta ↓)">⏭️ Próximo</button>
                    <button class="btn-ctrl" onclick="toggleFullscreen()" title="Tela Cheia (Tecla F)">⛶ Tela Cheia</button>
                </div>
            </div>
        </div>

        <div class="sidebar-channels">
            <div class="nav-tabs">
                <button class="nav-tab active" data-filter="digital">⚡ Só Digital (Mais Leve)</button>
                <button class="nav-tab" data-filter="discovery">🌟 Discovery (8)</button>
                <button class="nav-tab" data-filter="favoritos">⭐ Favoritos (<span id="favCount">0</span>)</button>
                <button class="nav-tab" data-filter="br">🇧🇷 Brasil Aberta</button>
                <button class="nav-tab" data-filter="todos">Todos (__TOTAL__)</button>
            </div>

            <div class="channel-stream-list" id="channelList"></div>
        </div>

    </div>

    <!-- MODAL DE ATALHOS DE TECLADO -->
    <div id="modalAtalhos" class="modal-overlay" onclick="fecharModalSeForFora(event)">
        <div class="modal-card">
            <div class="modal-header">
                <h2>⌨️ Controle Remoto de Teclado</h2>
                <button class="modal-close" onclick="toggleModalAtalhos()">&times;</button>
            </div>
            <p style="font-size: 13px; color: var(--text-muted);">Você pode controlar a Central de TV diretamente pelo teclado como um controle remoto de televisão:</p>
            
            <div class="shortcut-grid">
                <div class="shortcut-item"><span>Próximo Canal</span> <kbd>↓</kbd></div>
                <div class="shortcut-item"><span>Canal Anterior</span> <kbd>↑</kbd></div>
                <div class="shortcut-item"><span>Pausar / Retomar</span> <kbd>Espaço</kbd></div>
                <div class="shortcut-item"><span>Tela Cheia</span> <kbd>F</kbd></div>
                <div class="shortcut-item"><span>Mutar / Desmutar</span> <kbd>M</kbd></div>
                <div class="shortcut-item"><span>Modo Cinema</span> <kbd>C</kbd></div>
                <div class="shortcut-item"><span>Aumentar Volume</span> <kbd>→</kbd></div>
                <div class="shortcut-item"><span>Diminuir Volume</span> <kbd>←</kbd></div>
                <div class="shortcut-item"><span>Discovery Kids</span> <kbd>1</kbd></div>
                <div class="shortcut-item"><span>Discovery Channel</span> <kbd>2</kbd></div>
                <div class="shortcut-item"><span>Discovery Turbo</span> <kbd>3</kbd></div>
                <div class="shortcut-item"><span>Animal Planet</span> <kbd>4</kbd></div>
            </div>
        </div>
    </div>

    <script>
        // Redirecionamento se aberto como arquivo local para usar o proxy HTTP
        if (window.location.protocol === 'file:') {
            fetch('http://localhost:8080/index.html', { mode: 'no-cors' })
                .then(() => { window.location.href = 'http://localhost:8080/'; })
                .catch(() => { console.log('Servidor proxy local rodando.'); });
        }

        const CANAIS = __CANAIS_JSON__;

        let hls = null;
        let canalAtual = null;
        let filtroAtivo = 'digital';
        let termoBusca = '';
        let favoritos = JSON.parse(localStorage.getItem('tv_favoritos') || '[]');

        const video = document.getElementById('mainVideo');
        const playOverlay = document.getElementById('playOverlay');
        const btnDesmutar = document.getElementById('btnDesmutar');
        const toast = document.getElementById('toastStatus');
        const toastMsg = document.getElementById('toastMsg');
        const liveDot = document.getElementById('liveDot');
        const hud = document.getElementById('hudFeedback');
        const hudIcon = document.getElementById('hudIcon');
        const hudText = document.getElementById('hudText');
        const epgBadge = document.getElementById('epgBadge');
        const btnFavCurrent = document.getElementById('btnFavCurrent');

        function atualizarContadorFav() {
            document.getElementById('favCount').textContent = favoritos.length;
        }
        atualizarContadorFav();

        function mostrarHud(icon, texto) {
            hudIcon.textContent = icon;
            hudText.textContent = texto;
            hud.classList.add('show');
            clearTimeout(window._hudTimer);
            window._hudTimer = setTimeout(() => {
                hud.classList.remove('show');
            }, 1200);
        }

        function resolverUrl(url) {
            return 'http://localhost:8080/proxy?url=' + encodeURIComponent(url);
        }

        function destravarComSom() {
            video.muted = false;
            video.play().then(() => {
                playOverlay.style.display = 'none';
                btnDesmutar.style.display = 'none';
                mostrarHud('🔊', 'Áudio e Vídeo Ativos');
            }).catch(err => {
                console.log('Play com som requer mute prévio:', err);
                video.muted = true;
                video.play();
                playOverlay.style.display = 'none';
                btnDesmutar.style.display = 'flex';
                mostrarHud('🔇', 'Modo Mudo (Clique para Ativar Som)');
            });
        }

        function desmutarSom() {
            video.muted = false;
            btnDesmutar.style.display = 'none';
            mostrarHud('🔊', 'Som Ativado');
        }

        function toggleFavorito(id, event) {
            if (event) event.stopPropagation();
            const idx = favoritos.indexOf(id);
            if (idx === -1) {
                favoritos.push(id);
                mostrarHud('⭐', 'Adicionado aos Favoritos');
            } else {
                favoritos.splice(idx, 1);
                mostrarHud('☆', 'Removido dos Favoritos');
            }
            localStorage.setItem('tv_favoritos', JSON.stringify(favoritos));
            atualizarContadorFav();
            renderizar();
            atualizarBotaoFavAtual();
        }

        function toggleFavoritoAtual() {
            if (canalAtual) toggleFavorito(canalAtual.id);
        }

        function atualizarBotaoFavAtual() {
            if (!canalAtual) return;
            if (favoritos.includes(canalAtual.id)) {
                btnFavCurrent.classList.add('active');
                btnFavCurrent.textContent = '★';
            } else {
                btnFavCurrent.classList.remove('active');
                btnFavCurrent.textContent = '☆';
            }
        }

        function calcularGradeHoraria() {
            const h = new Date().getHours();
            if (h >= 6 && h < 12) return '🌅 Grade Matutina • Programação Educativa & Infantil';
            if (h >= 12 && h < 18) return '☀️ Grade Vespertina • Natureza, Aventura & Séries';
            if (h >= 18 && h < 23) return '🌙 Horário Nobre • Especiais em Alta Definição';
            return '🌌 Sessão Corujão • Motores & Grandes Maratonas';
        }

        video.addEventListener('playing', () => {
            playOverlay.style.display = 'none';
            liveDot.style.background = 'var(--emerald)';
            if (video.muted) {
                btnDesmutar.style.display = 'flex';
            } else {
                btnDesmutar.style.display = 'none';
            }
        });

        video.addEventListener('pause', () => {
            if (video.currentTime === 0 || video.ended) {
                playOverlay.style.display = 'flex';
            }
        });

        function sintonizar(c) {
            canalAtual = c;
            toastMsg.textContent = 'Sintonizando ' + c.nome + '...';
            toast.classList.add('active');
            liveDot.style.background = 'var(--amber)';

            document.getElementById('nowTitle').textContent = c.nome;
            document.getElementById('nowMeta').textContent = `${c.regiao} • ${c.categoria} • Latência: ${c.latencia}ms • Digital Leve`;
            epgBadge.textContent = calcularGradeHoraria();
            atualizarBotaoFavAtual();

            document.querySelectorAll('.stream-card').forEach(el => el.classList.remove('active'));
            const card = document.getElementById('card-' + c.id);
            if (card) {
                card.classList.add('active');
                card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }

            if (hls) {
                hls.destroy();
                hls = null;
            }
            video.pause();
            video.removeAttribute('src');
            video.load();

            const targetUrl = resolverUrl(c.url);

            if (Hls.isSupported()) {
                hls = new Hls({
                    enableWorker: true,
                    lowLatencyMode: false,
                    liveSyncDurationCount: 3,
                    maxBufferLength: 20,
                    maxMaxBufferLength: 40
                });
                hls.loadSource(targetUrl);
                hls.attachMedia(video);

                hls.on(Hls.Events.MANIFEST_PARSED, function () {
                    toast.classList.remove('active');
                    const prom = video.play();
                    if (prom !== undefined) {
                        prom.then(() => {
                            playOverlay.style.display = 'none';
                        }).catch(() => {
                            console.log('Autoplay bloqueado pelo navegador.');
                            playOverlay.style.display = 'flex';
                            video.muted = true;
                            video.play().then(() => {
                                btnDesmutar.style.display = 'flex';
                            }).catch(e => console.log('Erro play mudo:', e));
                        });
                    }
                });

                hls.on(Hls.Events.ERROR, function (evt, data) {
                    if (data.fatal) {
                        switch (data.type) {
                            case Hls.ErrorTypes.NETWORK_ERROR:
                                hls.startLoad();
                                break;
                            case Hls.ErrorTypes.MEDIA_ERROR:
                                hls.recoverMediaError();
                                break;
                            default:
                                if (hls) hls.destroy();
                                break;
                        }
                    }
                });
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = targetUrl;
                video.play().catch(() => { playOverlay.style.display = 'flex'; });
            }
        }

        function normalizar(t) {
            return t.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
        }

        function renderizar() {
            const list = document.getElementById('channelList');
            list.innerHTML = '';

            const filtrados = CANAIS.filter(c => {
                const nomeNorm = normalizar(c.nome);
                const buscaNorm = normalizar(termoBusca);
                if (buscaNorm && !nomeNorm.includes(buscaNorm)) return false;

                if (filtroAtivo === 'favoritos') {
                    return favoritos.includes(c.id);
                } else if (filtroAtivo === 'discovery') {
                    return nomeNorm.includes('discovery') || nomeNorm.includes('animal planet');
                } else if (filtroAtivo === 'digital') {
                    return c.qualidade === 'Digital';
                } else if (filtroAtivo === 'br') {
                    return c.pais.includes('Brasil') && !nomeNorm.includes('discovery');
                }
                return true;
            });

            if (filtrados.length === 0) {
                list.innerHTML = '<div style="text-align:center; padding:30px; color:var(--text-muted); font-size:13px;">Nenhum canal encontrado neste filtro.</div>';
                return;
            }

            filtrados.forEach(c => {
                const div = document.createElement('div');
                div.className = 'stream-card' + (canalAtual && canalAtual.id === c.id ? ' active' : '');
                div.id = 'card-' + c.id;
                div.onclick = () => sintonizar(c);

                const isFav = favoritos.includes(c.id);

                div.innerHTML = `
                    <div class="card-main">
                        <div class="card-title-row">
                            <span class="card-title">${c.nome}</span>
                        </div>
                        <div class="card-meta">
                            <span>${c.regiao}</span>
                            <span>•</span>
                            <span>${c.categoria}</span>
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="btn-fav-card ${isFav ? 'active' : ''}" title="Favoritar" onclick="toggleFavorito(${c.id}, event)">★</button>
                        <div class="card-badge">Digital</div>
                    </div>
                `;
                list.appendChild(div);
            });
        }

        document.getElementById('searchInput').addEventListener('input', (e) => {
            termoBusca = e.target.value;
            renderizar();
        });

        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                filtroAtivo = tab.getAttribute('data-filter');
                renderizar();
            });
        });

        function copiarLink() {
            if (!canalAtual) return alert('Selecione um canal!');
            navigator.clipboard.writeText(canalAtual.url).then(() => {
                mostrarHud('📋', 'Link Copiado');
            });
        }

        function proximoCanal() {
            if (!canalAtual) return;
            const idx = CANAIS.findIndex(c => c.id === canalAtual.id);
            if (idx !== -1 && idx + 1 < CANAIS.length) {
                sintonizar(CANAIS[idx + 1]);
                mostrarHud('⏭️', CANAIS[idx + 1].nome);
            }
        }

        function anteriorCanal() {
            if (!canalAtual) return;
            const idx = CANAIS.findIndex(c => c.id === canalAtual.id);
            if (idx > 0) {
                sintonizar(CANAIS[idx - 1]);
                mostrarHud('⏮️', CANAIS[idx - 1].nome);
            }
        }

        function toggleFullscreen() {
            const frame = document.getElementById('screenFrame');
            if (!document.fullscreenElement) {
                frame.requestFullscreen().catch(() => {});
                mostrarHud('⛶', 'Tela Cheia');
            } else {
                document.exitFullscreen().catch(() => {});
                mostrarHud('🗗', 'Janela');
            }
        }

        function toggleCinemaMode() {
            document.body.classList.toggle('cinema-mode');
            if (document.body.classList.contains('cinema-mode')) {
                mostrarHud('🎬', 'Modo Cinema Ativado');
            } else {
                mostrarHud('💡', 'Modo Normal');
            }
        }

        function toggleModalAtalhos() {
            document.getElementById('modalAtalhos').classList.toggle('open');
        }

        function fecharModalSeForFora(e) {
            if (e.target.id === 'modalAtalhos') {
                toggleModalAtalhos();
            }
        }

        // CONTROLE REMOTO COMPLETO POR TECLADO
        window.addEventListener('keydown', (e) => {
            // Se estiver digitando na busca, ignora atalhos de controle
            if (document.activeElement === document.getElementById('searchInput')) {
                if (e.key === 'Escape') document.getElementById('searchInput').blur();
                return;
            }

            switch (e.key) {
                case ' ':
                    e.preventDefault();
                    if (video.paused) {
                        video.play();
                        mostrarHud('▶', 'Reproduzindo');
                    } else {
                        video.pause();
                        mostrarHud('⏸️', 'Pausado');
                    }
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    proximoCanal();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    anteriorCanal();
                    break;
                case 'f':
                case 'F':
                    e.preventDefault();
                    toggleFullscreen();
                    break;
                case 'm':
                case 'M':
                    e.preventDefault();
                    video.muted = !video.muted;
                    mostrarHud(video.muted ? '🔇' : '🔊', video.muted ? 'Mudo' : 'Som Ativado');
                    btnDesmutar.style.display = video.muted ? 'flex' : 'none';
                    break;
                case 'c':
                case 'C':
                    e.preventDefault();
                    toggleCinemaMode();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    video.volume = Math.min(1, video.volume + 0.1);
                    video.muted = false;
                    mostrarHud('🔊', `Volume ${Math.round(video.volume * 100)}%`);
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    video.volume = Math.max(0, video.volume - 0.1);
                    mostrarHud('🔉', `Volume ${Math.round(video.volume * 100)}%`);
                    break;
                case '?':
                    e.preventDefault();
                    toggleModalAtalhos();
                    break;
                // Atalhos Numéricos para Canais VIP Discovery
                case '1':
                    sintonizar(CANAIS.find(c => c.id === 9001) || CANAIS[0]);
                    break;
                case '2':
                    sintonizar(CANAIS.find(c => c.id === 9002) || CANAIS[1]);
                    break;
                case '3':
                    sintonizar(CANAIS.find(c => c.id === 9003) || CANAIS[2]);
                    break;
                case '4':
                    sintonizar(CANAIS.find(c => c.id === 9008) || CANAIS[3]);
                    break;
                case '5':
                    sintonizar(CANAIS.find(c => c.id === 9005) || CANAIS[4]);
                    break;
            }
        });

        // Inicializar com Discovery Kids
        renderizar();
        const inicial = CANAIS.find(c => c.id === 9001) || CANAIS[0];
        if (inicial) {
            sintonizar(inicial);
        }
    </script>
</body>
</html>
"""

html_final = html_template.replace("__TOTAL__", str(len(canais_data))).replace("__CANAIS_JSON__", json_str)

caminho_saida = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\index.html")
caminho_desktop = Path(r"C:\Users\jonas\Desktop\ASSISTIR_TV.html")

with open(caminho_saida, "w", encoding="utf-8") as f:
    f.write(html_final)

with open(caminho_desktop, "w", encoding="utf-8") as f:
    f.write(html_final)

print("CENTRAL DE TV DIGITAL ATUALIZADA COM SUCESSO!")
