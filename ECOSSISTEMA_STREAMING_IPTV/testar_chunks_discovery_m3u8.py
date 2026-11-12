import urllib.request
import urllib.parse

urls = [
    "http://hls1.sua.tv:80/live/discoverychannelfhd/s.m3u8",
    "http://181.224.200.5:2277/play/a00o/index.m3u8"
]

for target in urls:
    proxy_url = "http://localhost:8080/proxy?url=" + urllib.parse.quote(target)
    try:
        with urllib.request.urlopen(proxy_url, timeout=4) as resp:
            content = resp.read().decode('utf-8')
            print(f"\nManifest de {target[:40]}:")
            linhas = [l for l in content.splitlines() if l.startswith('/proxy?url=')]
            if linhas:
                print("Primeiro chunk reescrito:", linhas[0][:80])
                # Testar o chunk
                with urllib.request.urlopen("http://localhost:8080" + linhas[0], timeout=4) as r2:
                    print("Status do chunk:", r2.status, "Bytes lidos:", len(r2.read(5000)))
            else:
                print("Nenhum chunk com /proxy?url=. Linhas:", content.splitlines()[:5])
    except Exception as e:
        print(f"Erro ao testar {target}: {e}")
