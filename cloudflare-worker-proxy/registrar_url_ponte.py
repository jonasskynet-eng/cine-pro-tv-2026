import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(r"c:\Users\jonas\Downloads\projeto de estudo")
GERADOR = ROOT / "ECOSSISTEMA_STREAMING_IPTV" / "atualizar_central_pro.py"


def main():
    if len(sys.argv) < 2:
        print("Uso: python registrar_url_ponte.py <https://sua-ponte.workers.dev>")
        sys.exit(1)

    url = sys.argv[1].strip().rstrip("/")
    if not url.startswith("https://"):
        print(f"ERRO: URL inválida ({url})")
        sys.exit(1)

    print(f"1. Testando ponte ao vivo em {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        txt = resp.read().decode("utf-8", errors="ignore")
        if '"ok":true' not in txt.replace(" ", ""):
            print(f"AVISO: resposta inesperada: {txt}")

    print("2. Gravando URL da ponte no CinePro TV ...")
    conteudo = GERADOR.read_text(encoding="utf-8")
    novo_conteudo, n = re.subn(
        r"const DEFAULT_CLOUDFLARE_PROXY_URL = '[^']*';",
        f"const DEFAULT_CLOUDFLARE_PROXY_URL = '{url}';",
        conteudo,
        count=1,
    )
    if n != 1:
        print("ERRO: marcador DEFAULT_CLOUDFLARE_PROXY_URL não encontrado.")
        sys.exit(1)
    GERADOR.write_text(novo_conteudo, encoding="utf-8")

    print("3. Regerando site e enviando para o GitHub Pages ...")
    subprocess.run([sys.executable, "-W", "error", str(GERADOR)], check=True)
    subprocess.run(
        ["git", "-C", str(ROOT), "add", "ECOSSISTEMA_STREAMING_IPTV/atualizar_central_pro.py", "docs/index.html", "ECOSSISTEMA_STREAMING_IPTV/saida/index.html"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(ROOT), "commit", "-m", f"feat(proxy): conectar ponte Cloudflare Workers ({url})"],
        check=False,
    )
    subprocess.run(["git", "-C", str(ROOT), "push", "origin", "main"], check=True)
    print(f"SUCESSO! Ponte {url} conectada e enviada ao GitHub Pages!")


if __name__ == "__main__":
    main()
