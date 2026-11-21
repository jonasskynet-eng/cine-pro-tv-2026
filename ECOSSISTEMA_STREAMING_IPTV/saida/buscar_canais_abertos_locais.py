import os
import re

dir_proj = r"c:\Users\jonas\Downloads\projeto de estudo"
termos = ['globo', 'sbt', 'band', 'record', 'cultura', 'redetv']

encontrados = []

for root, dirs, files in os.walk(dir_proj):
    for f in files:
        if f.endswith(('.m3u', '.m3u8', '.txt', '.json')):
            full_path = os.path.join(root, f)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    lines = fp.readlines()
                    for i, l in enumerate(lines):
                        if l.startswith('#EXTINF') and any(t in l.lower() for t in termos):
                            # pegar a próxima linha de URL
                            if i + 1 < len(lines):
                                url_line = lines[i+1].strip()
                                if url_line.startswith('http'):
                                    encontrados.append((l.strip(), url_line, f))
            except Exception:
                pass

print(f"Total encontrados nas playlists locais: {len(encontrados)}")
# Mostrar amostras únicas por canal
canais_vistos = set()
for inf, u, arquivo in encontrados:
    # extrair nome
    nome = inf.split(',')[-1].strip()
    if nome not in canais_vistos:
        canais_vistos.add(nome)
        print(f"[{arquivo}] {nome} -> {u}")
