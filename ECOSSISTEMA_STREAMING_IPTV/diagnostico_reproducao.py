import urllib.request
import urllib.parse

# Testar URL direta do Discovery Kids Leve
url_direta = "http://rtv30t.com:80/Wintvx/Wtv1020/71874.ts"
print("Testando URL direta:", url_direta)
try:
    req = urllib.request.Request(url_direta, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("Direta Status:", resp.status)
        print("Direta Headers:", resp.headers)
        data = resp.read(5000)
        print("Direta Bytes lidos:", len(data))
except Exception as e:
    print("Erro na direta:", e)

# Testar via proxy local
url_proxy = "http://localhost:8080/proxy?url=" + urllib.parse.quote(url_direta)
print("\nTestando via Proxy Local:", url_proxy)
try:
    req2 = urllib.request.Request(url_proxy)
    with urllib.request.urlopen(req2, timeout=5) as resp2:
        print("Proxy Status:", resp2.status)
        print("Proxy Headers:", resp2.headers)
        data2 = resp2.read(5000)
        print("Proxy Bytes lidos:", len(data2))
except Exception as e:
    print("Erro no proxy:", e)
