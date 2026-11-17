"""
Robô de Manutenção Diária do CinePro TV (compatível com Windows e GitHub Actions Linux).
1. Atualiza a curadoria aberta brasileira (iptv-org BR, Free-TV BR e extras HTTPS) testando ao vivo.
2. Verifica canais HTTPS ativos no banco SQLite e desativa apenas links mortos definitivos (404/410).
3. Regera docs/index.html e saida/canais_leves.json com os canais saudáveis no topo.
"""

import concurrent.futures
import pathlib
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request

BASE_DIR = pathlib.Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "saida" / "banco_iptv.db"


def verificar_link_https(registro):
    c_id, nome, url = registro
    # Preservar IPs locais de fibra (170.83.x) pois servidores fora do Brasil podem sofrer bloqueio regional
    if not url.startswith("https://"):
        return None
    inicio = time.monotonic()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            lat_ms = int((time.monotonic() - inicio) * 1000)
            cors = 1 if resp.headers.get("Access-Control-Allow-Origin", "").strip() == "*" else 0
            body = resp.read(200).decode("utf-8", errors="ignore")
            if resp.status == 200 and ("#EXTM3U" in body or "audio" in resp.headers.get("Content-Type", "").lower()):
                return ("OK", c_id, lat_ms, cors)
    except urllib.error.HTTPError as err:
        code = err.code
        err.close()
        if code in (404, 410):
            return ("MORTO", c_id, code, 0)
    except Exception:
        return None
    return None


def main():
    print("=== [1/3] Atualizando curadoria de listas abertas ao vivo ===")
    subprocess.run([sys.executable, str(BASE_DIR / "curadoria_youtube_br.py")], check=True)

    print("=== [2/3] Auditando canais HTTPS do banco de dados ===")
    conn = sqlite3.connect(DB_PATH)
    ativos_https = conn.execute(
        "SELECT id, nome, url FROM canais WHERE status='ATIVO' AND url LIKE 'https://%'"
    ).fetchall()
    desativados = 0
    atualizados = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
        for res in pool.map(verificar_link_https, ativos_https):
            if not res:
                continue
            estado, c_id, val, cors = res
            if estado == "MORTO":
                conn.execute("UPDATE canais SET status='INATIVO' WHERE id=?", (c_id,))
                desativados += 1
            elif estado == "OK":
                conn.execute(
                    "UPDATE canais SET latencia_ms=?, cors_star=? WHERE id=?",
                    (val, cors, c_id),
                )
                atualizados += 1

    conn.commit()
    conn.close()
    print(f"Auditoria concluída: {atualizados} atualizados | {desativados} links mortos (404/410) desativados.")

    print("=== [3/3] Regerando Central CinePro TV (docs/index.html) ===")
    subprocess.run([sys.executable, "-W", "error", str(BASE_DIR / "atualizar_central_pro.py")], check=True)
    print("Manutenção diária finalizada com sucesso!")


if __name__ == "__main__":
    main()
