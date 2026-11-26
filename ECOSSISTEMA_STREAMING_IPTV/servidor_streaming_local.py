import http.server
import socketserver
import urllib.request
import urllib.parse
import ssl
import sys
import os
import re
import socket
import json
import threading
import gzip
import zlib
import time
from pathlib import Path

def decodificar_manifesto(raw_bytes, content_encoding=''):
    """Decodifica bytes de playlist HLS tratando gzip/deflate quando presentes."""
    enc = (content_encoding or '').lower()
    if raw_bytes[:2] == b'\x1f\x8b' or 'gzip' in enc:
        try:
            raw_bytes = gzip.decompress(raw_bytes)
        except Exception:
            pass
    elif 'deflate' in enc:
        try:
            raw_bytes = zlib.decompress(raw_bytes)
        except Exception:
            try:
                raw_bytes = zlib.decompress(raw_bytes, -zlib.MAX_WBITS)
            except Exception:
                pass
    return raw_bytes.decode('utf-8', errors='ignore')

PORT = int(os.environ.get("PORT", "8080"))
CINEPRO_MODO = os.environ.get("CINEPRO_MODO", "LOCAL").strip().upper()
CINEPRO_VIP_TOKEN = os.environ.get("CINEPRO_VIP_TOKEN", "").strip()
VIP_M3U_URL = os.environ.get("VIP_M3U_URL", "").strip()

_BASE_SCRIPT = Path(__file__).resolve().parent
_STATIC_ENV = os.environ.get("CINEPRO_STATIC_DIR", "").strip()
if _STATIC_ENV and Path(_STATIC_ENV).exists():
    DIRETORIO_SAIDA = Path(_STATIC_ENV)
elif (_BASE_SCRIPT.parent / "docs").exists():
    DIRETORIO_SAIDA = _BASE_SCRIPT.parent / "docs"
else:
    DIRETORIO_SAIDA = _BASE_SCRIPT / "saida"

DIRETORIO_VIP = Path(os.environ.get("CINEPRO_VIP_DIR", str(_BASE_SCRIPT / "vip_privado")))
DIRETORIO_VIP.mkdir(parents=True, exist_ok=True)

_CACHE_VIP = {
    "assinatura_arquivos": None,
    "url_remota": "",
    "expira_remoto": 0.0,
    "canais": []
}

def _classificar_tags_vip(nome: str, grupo: str):
    texto = f"{nome} {grupo}".lower()
    tags = ["vip"]
    mapa = [
        ("esportes", ["esport", "sport", "premiere", "combate", "espn", "fox sports", "caze", "futebol", "nba", "ufc"]),
        ("filmes", ["filme", "movie", "cine", "hbo", "telecine", "megapix", "tnt", "space", "cinemax", "paramount"]),
        ("series", ["serie", "série", "series", "warner", "axn", "sony", "universal", "star channel", "fx"]),
        ("infantil", ["kids", "infantil", "desenho", "cartoon", "disney", "discovery kids", "gloob", "nick"]),
        ("noticias", ["noticia", "notícia", "news", "cnn", "globonews", "bandnews", "jovem pan"]),
        ("aberta", ["globo", "sbt", "record", "band", "redetv", "cultura"]),
        ("comedia", ["comedia", "comédia", "comedy", "humor", "multishow"]),
        ("musica", ["music", "música", "mtv", "show", "bis", "radio", "rádio"]),
    ]
    for tag, termos in mapa:
        if any(t in texto for t in termos):
            tags.append(tag)
    return tags

def _parse_conteudo_m3u_vip(conteudo: str, canais_out: list, urls_vistas: set):
    nome_atual = ""
    grupo_atual = "⭐ Pacote VIP"
    logo_atual = ""
    for linha in conteudo.splitlines():
        l = linha.strip()
        if not l:
            continue
        if l.startswith("#EXTINF"):
            m_logo = re.search(r'tvg-logo="([^"]*)"', l, re.I)
            m_grupo = re.search(r'group-title="([^"]*)"', l, re.I)
            logo_atual = m_logo.group(1).strip() if m_logo else ""
            grupo_atual = (m_grupo.group(1).strip() if m_grupo else "") or "⭐ Pacote VIP"
            nome_atual = l.split(",")[-1].strip() if "," in l else "Canal VIP"
        elif l.startswith("http://") or l.startswith("https://"):
            if l not in urls_vistas:
                urls_vistas.add(l)
                idx = len(canais_out)
                nome_final = nome_atual or f"Canal VIP {idx + 1}"
                num = 1001 + idx
                canais_out.append({
                    "id": 90001 + idx,
                    "numero": num,
                    "numero_str": str(num),
                    "nome": nome_final,
                    "url": l,
                    "logo": logo_atual,
                    "categoria": grupo_atual,
                    "pais": "🇧🇷 Brasil",
                    "pais_codigo": "BR",
                    "idioma_badge": "👑 VIP",
                    "tags": _classificar_tags_vip(nome_final, grupo_atual),
                    "cors": 0
                })
            nome_atual = ""
            grupo_atual = "⭐ Pacote VIP"
            logo_atual = ""

def carregar_canais_vip_extras():
    """Carrega listas VIP (.m3u/.m3u8) da pasta privada e de VIP_M3U_URL com cache em memória."""
    arquivos = sorted(
        list(DIRETORIO_VIP.glob("*.m3u")) + list(DIRETORIO_VIP.glob("*.m3u8")),
        key=lambda p: p.name.lower()
    )
    assinatura = tuple((str(p), p.stat().st_mtime) for p in arquivos)
    agora = time.monotonic()
    remoto_valido = (not VIP_M3U_URL) or (
        _CACHE_VIP["url_remota"] == VIP_M3U_URL and agora < _CACHE_VIP["expira_remoto"]
    )
    if _CACHE_VIP["assinatura_arquivos"] == assinatura and remoto_valido:
        return _CACHE_VIP["canais"]

    canais = []
    urls_vistas = set()
    for arq in arquivos:
        try:
            texto = arq.read_text(encoding="utf-8", errors="ignore")
            _parse_conteudo_m3u_vip(texto, canais, urls_vistas)
        except Exception:
            pass

    if VIP_M3U_URL:
        try:
            ctx_vip = ssl.create_default_context()
            ctx_vip.check_hostname = False
            ctx_vip.verify_mode = ssl.CERT_NONE
            req_vip = urllib.request.Request(VIP_M3U_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_vip, context=ctx_vip, timeout=12) as resp_vip:
                texto_remoto = decodificar_manifesto(
                    resp_vip.read(),
                    resp_vip.headers.get("Content-Encoding", "")
                )
                _parse_conteudo_m3u_vip(texto_remoto, canais, urls_vistas)
        except Exception:
            pass

    _CACHE_VIP["assinatura_arquivos"] = assinatura
    _CACHE_VIP["url_remota"] = VIP_M3U_URL
    _CACHE_VIP["expira_remoto"] = agora + 900.0
    _CACHE_VIP["canais"] = canais
    return canais

# Fila sincronizada de comandos remotos (Celular -> TV)
LOCK_COMANDOS = threading.Lock()
COMANDOS_PENDENTES = []
STATUS_TV = {
    "canal_numero": 1,
    "canal_nome": "SBT Nacional HD",
    "pausado": False,
    "volume": 100,
    "mudo": False
}

def obter_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class ServidorMultithreadStreaming(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRETORIO_SAIDA), **kwargs)

    def log_message(self, format, *args):
        # Evita AttributeError quando executado em segundo plano via pythonw.exe (sys.stderr=None)
        if sys.stderr is not None:
            try:
                super().log_message(format, *args)
            except Exception:
                pass

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Expose-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_HEAD(self):
        rota = urllib.parse.urlparse(self.path).path
        if rota in ('/', '/index.html', '/healthz', '/api/status_servidor'):
            self.send_response(200)
            ctype = 'application/json' if rota in ('/healthz', '/api/status_servidor') else 'text/html; charset=utf-8'
            self.send_header('Content-Type', ctype)
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        parsed_req = urllib.parse.urlparse(self.path)
        rota_req = parsed_req.path

        if rota_req == '/healthz':
            payload = json.dumps({
                "status": "ok",
                "modo": CINEPRO_MODO,
                "porta": PORT
            }).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if rota_req == '/api/status_servidor':
            canais_vip = carregar_canais_vip_extras()
            payload = json.dumps({
                "ativo": True,
                "modo": CINEPRO_MODO,
                "docker": (CINEPRO_MODO == "VIP_DOCKER"),
                "requer_chave": bool(CINEPRO_VIP_TOKEN),
                "qtd_vip_extras": len(canais_vip),
                "versao": "2026.4-VIP"
            }, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if rota_req == '/api/canais_vip':
            params_vip = urllib.parse.parse_qs(parsed_req.query)
            chave_enviada = (params_vip.get('chave', [''])[0] or self.headers.get('X-Vip-Token', '')).strip()
            if CINEPRO_VIP_TOKEN and chave_enviada != CINEPRO_VIP_TOKEN:
                payload = json.dumps({
                    "ok": False,
                    "requer_chave": True,
                    "erro": "Chave VIP inválida. Solicite no WhatsApp (11) 96670-7293."
                }, ensure_ascii=False).encode('utf-8')
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            canais_vip = carregar_canais_vip_extras()
            payload = json.dumps({
                "ok": True,
                "canais": canais_vip
            }, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # 1. API DE COMANDOS REMOTOS (CELULAR -> TV)
        if self.path.startswith('/api/comando'):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            cmd = params.get('cmd', [''])[0]
            val = params.get('val', [''])[0]
            with LOCK_COMANDOS:
                COMANDOS_PENDENTES.append({"cmd": cmd, "val": val})
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return

        elif self.path == '/api/ouvir_comandos':
            with LOCK_COMANDOS:
                cmds = list(COMANDOS_PENDENTES)
                COMANDOS_PENDENTES.clear()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(cmds).encode('utf-8'))
            return

        elif self.path.startswith('/api/status_tv'):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            for k, v in params.items():
                STATUS_TV[k] = v[0]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(STATUS_TV).encode('utf-8'))
            return

        elif self.path == '/api/obter_status_tv':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(STATUS_TV).encode('utf-8'))
            return

        elif self.path == '/api/ip_local':
            ip = obter_ip_local()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "ip": ip,
                "porta": PORT,
                "url_controle": f"http://{ip}:{PORT}/controle.html"
            }).encode('utf-8'))
            return

        # 2. PROXY DE STREAMING HLS
        if self.path.startswith('/proxy?url='):
            raw_url = self.path.split('/proxy?url=')[1]
            target_url = urllib.parse.unquote(raw_url)

            parsed_target = urllib.parse.urlparse(target_url)
            base_url = target_url.rsplit('/', 1)[0] + '/'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept-Encoding': 'identity',
                'Referer': base_url,
                'Origin': f"{parsed_target.scheme}://{parsed_target.netloc}"
            }
            if any(k in target_url.lower() for k in ['pluto.tv', 'plutotv.net', 'jmp2.uk', 'pluto']):
                headers['Origin'] = 'https://pluto.tv'
                headers['Referer'] = 'https://pluto.tv/'

            # Repassar cabeçalho de Range caso enviado pelo player
            if 'Range' in self.headers:
                headers['Range'] = self.headers['Range']

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            try:
                req = urllib.request.Request(target_url, headers=headers)
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    resp_status = resp.status if hasattr(resp, 'status') else 200
                    content_type = resp.headers.get('Content-Type', 'video/mp2t')
                    
                    # Pegar a URL FINAL após redirecionamentos (ex: jmp2.uk -> ipv4.pluto.tv)
                    final_url = resp.geturl()
                    parsed_final = urllib.parse.urlparse(final_url)
                    base_url = final_url.rsplit('/', 1)[0] + '/'

                    # Se a URL final for Pluto TV, garantir headers corretos para sub-requisições
                    if any(k in final_url.lower() for k in ['pluto.tv', 'plutotv.net']):
                        headers['Origin'] = 'https://pluto.tv'
                        headers['Referer'] = 'https://pluto.tv/'
                    
                    # 1. Se for arquivo de chave criptográfica AES-128 (.key), devolver bytes puros antes de qualquer parser de M3U8
                    eh_chave_aes = (
                        target_url.lower().endswith('.key')
                        or '.key?' in target_url.lower()
                        or 'keyfile' in target_url.lower()
                        or final_url.lower().endswith('.key')
                        or '.key?' in final_url.lower()
                    )
                    if eh_chave_aes:
                        key_data = resp.read()
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/octet-stream')
                        self.send_header('Content-Length', str(len(key_data)))
                        self.end_headers()
                        self.wfile.write(key_data)

                    # 2. Se for playlist M3U8, reescrevemos segmentos e tags #EXT-X-MAP / #EXT-X-KEY
                    elif 'mpegurl' in content_type.lower() or target_url.endswith('.m3u8') or '.m3u8?' in target_url or final_url.endswith('.m3u8') or '.m3u8?' in final_url:
                        raw_bytes = resp.read()
                        manifest = decodificar_manifesto(raw_bytes, resp.headers.get('Content-Encoding', ''))
                        if '#EXTM3U' not in manifest:
                            self.send_response(resp_status)
                            self.send_header('Content-Type', 'application/octet-stream')
                            self.send_header('Content-Length', str(len(raw_bytes)))
                            self.end_headers()
                            self.wfile.write(raw_bytes)
                            return

                        # Se for Master Playlist simples (#EXT-X-STREAM-INF sem áudio demuxado nem Pluto TV), achatamos para a sub-playlist ativa
                        if '#EXT-X-STREAM-INF' in manifest and '#EXT-X-MEDIA:' not in manifest and 'pluto' not in final_url.lower():
                            sub_cands = [l.strip() for l in manifest.splitlines() if l.strip() and not l.startswith('#')]
                            if sub_cands:
                                sub_target = sub_cands[0]
                                if not sub_target.startswith('http'):
                                    sub_target = urllib.parse.urljoin(base_url, sub_target)
                                try:
                                    req_sub = urllib.request.Request(sub_target, headers=headers)
                                    with urllib.request.urlopen(req_sub, context=ctx, timeout=8) as resp_sub:
                                        final_sub_url = resp_sub.geturl()
                                        sub_manifest = decodificar_manifesto(resp_sub.read(), resp_sub.headers.get('Content-Encoding', ''))
                                        if '#EXTM3U' in sub_manifest:
                                            manifest = sub_manifest
                                            base_url = final_sub_url.rsplit('/', 1)[0] + '/'
                                            parsed_final = urllib.parse.urlparse(final_sub_url)
                                except Exception:
                                    pass
                        
                        def resolver_link(link):
                            if link.startswith('http://') or link.startswith('https://'):
                                return '/proxy?url=' + urllib.parse.quote(link, safe='')
                            elif link.startswith('/'):
                                abs_u = f"{parsed_final.scheme}://{parsed_final.netloc}{link}"
                                return '/proxy?url=' + urllib.parse.quote(abs_u, safe='')
                            else:
                                abs_u = urllib.parse.urljoin(base_url, link)
                                return '/proxy?url=' + urllib.parse.quote(abs_u, safe='')

                        linhas_novas = []
                        for linha in manifest.splitlines():
                            l_strip = linha.strip()
                            if not l_strip:
                                continue
                            
                            # Tratar qualquer tag HLS com atributo URI="..." (#EXT-X-MEDIA, #EXT-X-MAP, #EXT-X-KEY, etc.)
                            if l_strip.startswith('#') and 'URI="' in l_strip:
                                l_strip = re.sub(r'URI="([^"]+)"', lambda m: f'URI="{resolver_link(m.group(1))}"', l_strip)
                                linhas_novas.append(l_strip)
                            elif not l_strip.startswith('#'):
                                linhas_novas.append(resolver_link(l_strip))
                            else:
                                linhas_novas.append(l_strip)
                                
                        body_modificado = '\n'.join(linhas_novas).encode('utf-8')
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/vnd.apple.mpegurl')
                        self.send_header('Content-Length', str(len(body_modificado)))
                        self.end_headers()
                        self.wfile.write(body_modificado)

                    # 3. Stream contínuo (.ts / mp4 / chunks de vídeo) em blocos com Keep-Alive
                    else:
                        self.send_response(resp_status)
                        self.send_header('Content-Type', content_type)
                        content_length = resp.headers.get('Content-Length')
                        if content_length:
                            self.send_header('Content-Length', content_length)
                        content_range = resp.headers.get('Content-Range')
                        if content_range:
                            self.send_header('Content-Range', content_range)
                        self.end_headers()
                        try:
                            while True:
                                chunk = resp.read(64 * 1024)
                                if not chunk:
                                    break
                                self.wfile.write(chunk)
                                self.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError):
                            pass
            except Exception as e:
                try:
                    self.send_response(502)
                    self.end_headers()
                    self.wfile.write(f"Erro Proxy: {e}".encode('utf-8'))
                except:
                    pass
        else:
            if self.path == '/' or self.path.startswith('/?'):
                self.path = '/index.html'
            super().do_GET()

# Servidor Threading (não trava com múltiplos requests simultâneos)
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == '__main__':
    try:
        httpd = ThreadingHTTPServer(("", PORT), ServidorMultithreadStreaming)
        print(f"Servidor Multithread Ativo na porta {PORT}")
        httpd.serve_forever()
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
