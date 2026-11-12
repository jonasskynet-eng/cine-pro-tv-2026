import http.server
import socketserver
import urllib.request
import urllib.parse
import ssl

PORT = 8080

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/proxy?url='):
            raw_url = self.path.split('/proxy?url=')[1]
            target_url = urllib.parse.unquote(raw_url)
            
            # Cabeçalhos inteligentes
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            if 'pluto.tv' in target_url:
                headers['Origin'] = 'https://pluto.tv'
                headers['Referer'] = 'https://pluto.tv/'

            req = urllib.request.Request(target_url, headers=headers)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            try:
                with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                    content_type = resp.headers.get('Content-Type', 'application/vnd.apple.mpegurl')
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self.end_headers()
                    self.wfile.write(resp.read())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Erro no Proxy: {e}".encode('utf-8'))
        else:
            super().do_GET()

print("Servidor Proxy pronto para rodar na porta 8080.")
