"""
SERVIDOR LOCAL DE TRANSMISSÃO E DISTRIBUIÇÃO M3U
Disponibiliza a lista higienizada de alta velocidade para players da rede local (TV Box, Celular, my-tv, VLC).
"""

import http.server
import socketserver
import os
from pathlib import Path

PORTA = 8080
PASTA_SAIDA = Path(__file__).parent / "saida"

class ManipuladorRequisicoesIPTV(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PASTA_SAIDA), **kwargs)

    def end_headers(self):
        # Permite conexões CORS para qualquer player web ou TV inteligente
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

def iniciar_servidor():
    os.chdir(PASTA_SAIDA)
    with socketserver.ThreadingTCPServer(("", PORTA), ManipuladorRequisicoesIPTV) as servidor:
        print(f"\n=======================================================")
        print(f"📡 SERVIDOR IPTV LOCAL ATIVO NA PORTA {PORTA}")
        print(f"=======================================================")
        print(f"-> Endereço local da lista: http://localhost:{PORTA}/lista_ultra_rapida.m3u")
        print(f"-> Métricas e Telemetria:   http://localhost:{PORTA}/metricas_performance.json")
        print(f"-> Pressione Ctrl + C para encerrar o servidor.")
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("\n[!] Servidor encerrado com sucesso.")

if __name__ == "__main__":
    iniciar_servidor()
