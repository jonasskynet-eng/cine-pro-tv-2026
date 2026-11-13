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
from pathlib import Path

PORT = 8080
DIRETORIO_SAIDA = Path(__file__).parent / "saida"

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

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Expose-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
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
                    
                    # 1. Se for playlist M3U8, reescrevemos segmentos e tags #EXT-X-MAP / #EXT-X-KEY
                    if 'mpegurl' in content_type.lower() or target_url.endswith('.m3u8') or '.m3u8?' in target_url or final_url.endswith('.m3u8') or '.m3u8?' in final_url:
                        manifest = resp.read().decode('utf-8', errors='ignore')

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
                                        manifest = resp_sub.read().decode('utf-8', errors='ignore')
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
                    
                    # 2. Se for arquivo de chave criptográfica AES-128 (.key)
                    elif target_url.endswith('.key') or '.key?' in target_url or 'keyfile' in target_url or final_url.endswith('.key'):
                        key_data = resp.read()
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/octet-stream')
                        self.send_header('Content-Length', str(len(key_data)))
                        self.end_headers()
                        self.wfile.write(key_data)

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
