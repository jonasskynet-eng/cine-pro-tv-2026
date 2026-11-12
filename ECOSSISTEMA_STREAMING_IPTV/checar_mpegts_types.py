import urllib.request
import re

url = 'https://cdn.jsdelivr.net/npm/mpegts.js@latest/dist/mpegts.js'
content = urllib.request.urlopen(url).read().decode('utf-8')

# Procurar por createPlayer ou supported types
matches = re.findall(r'case\s+[\'"][a-zA-Z0-9_-]+[\'"]:', content)
print("Tipos ou cases encontrados em mpegts.js:")
print(set(matches[:30]))

for m in re.finditer(r'createPlayer\s*=\s*function|function createPlayer', content):
    idx = m.start()
    print("--- createPlayer snippet ---")
    print(content[idx:idx+800])
