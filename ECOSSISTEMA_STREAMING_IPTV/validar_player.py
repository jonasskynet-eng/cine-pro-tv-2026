import urllib.request

req = urllib.request.Request('http://localhost:8080/index.html')
content = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
print("Verificando correções:")
print("1. type mpegts presente?:", "type: 'mpegts'" in content)
print("2. type mse ausente?:", "type: 'mse'" not in content)
print("3. muted presente para autoplay?:", "muted" in content)
