"""
Micro-servidor DNS UDP leve em Python puro para redirecionar programas doadores
de Smart TV Samsung (ex.: smart-stb, ottplayer) para o servidor CinePro TV VIP.
Uso recomendado em servidor Linux/VPS na porta 53 com a variavel CINEPRO_SERVER_IP.
"""

import os
import socket
import struct

PORTA_DNS = int(os.environ.get("DNS_PORT", "53"))
IP_SERVIDOR = os.environ.get("CINEPRO_SERVER_IP", "192.168.100.210").strip()
DNS_UPSTREAM = os.environ.get("DNS_UPSTREAM", "1.1.1.1").strip()
DOMINIOS_PORTAL = (
    "smart-stb.net",
    "ottplayer.tv",
    "ivi.ru",
    "tvigle.ru",
    "divan.tv",
)


def extrair_nome_dns(pacote: bytes):
    idx = 12
    partes = []
    while idx < len(pacote):
        tam = pacote[idx]
        if tam == 0:
            idx += 1
            break
        if (tam & 0xC0) == 0xC0:
            idx += 2
            break
        idx += 1
        partes.append(pacote[idx:idx + tam].decode("ascii", errors="ignore"))
        idx += tam
    qtype = struct.unpack("!H", pacote[idx:idx + 2])[0] if idx + 4 <= len(pacote) else 1
    return ".".join(partes).lower(), qtype, idx + 4


def montar_resposta_a(consulta: bytes, fim_q: int, ip_alvo: str) -> bytes:
    txid = consulta[:2]
    flags = b"\x81\x80"
    cabecalho = txid + flags + consulta[4:6] + b"\x00\x01\x00\x00\x00\x00"
    pergunta = consulta[12:fim_q]
    resposta = b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04" + socket.inet_aton(ip_alvo)
    return cabecalho + pergunta + resposta


def encaminhar_upstream(consulta: bytes) -> bytes:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_up:
        s_up.settimeout(3.0)
        s_up.sendto(consulta, (DNS_UPSTREAM, 53))
        resp, _ = s_up.recvfrom(4096)
        return resp


def iniciar_dns():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PORTA_DNS))
    print(f"Servidor DNS Samsung ativo na porta {PORTA_DNS} -> {IP_SERVIDOR}")
    while True:
        try:
            dados, addr = sock.recvfrom(4096)
            dominio, qtype, fim_q = extrair_nome_dns(dados)
            eh_portal = any(dominio == d or dominio.endswith("." + d) for d in DOMINIOS_PORTAL)
            if eh_portal and qtype == 1:
                sock.sendto(montar_resposta_a(dados, fim_q, IP_SERVIDOR), addr)
            else:
                sock.sendto(encaminhar_upstream(dados), addr)
        except Exception:
            pass


if __name__ == "__main__":
    iniciar_dns()
