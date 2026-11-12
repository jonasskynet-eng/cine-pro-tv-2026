import urllib.request
import urllib.parse

lista = [
    ("Discovery Turbo", "http://38.134.250.110:8000/play/a01y/index.m3u8"),
    ("Discovery Science", "http://45.171.64.30:6060/play/a007/index.m3u8"),
    ("Discovery H&H", "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/39.m3u8"),
    ("Animal Planet", "http://190.128.214.97:64333/play/a01n/index.m3u8"),
    ("Investigation ID", "http://45.184.109.10/live/69393EAE6ADBC65A68F942022362A202/41.m3u8"),
    ("Discovery Theater", "http://181.224.200.5:2277/play/a0bj/index.m3u8")
]

for nome, target in lista:
    proxy_url = "http://localhost:8080/proxy?url=" + urllib.parse.quote(target)
    try:
        with urllib.request.urlopen(proxy_url, timeout=3) as resp:
            content = resp.read().decode('utf-8')
            linhas = [l for l in content.splitlines() if l.startswith('/proxy?url=')]
            if linhas:
                with urllib.request.urlopen("http://localhost:8080" + linhas[0], timeout=3) as r2:
                    print(f"[OK 100%] {nome} -> Chunk Status: {r2.status}")
            else:
                print(f"[AVISO] {nome} -> Sem linhas de chunk")
    except Exception as e:
        print(f"[ERRO] {nome} -> {e}")
