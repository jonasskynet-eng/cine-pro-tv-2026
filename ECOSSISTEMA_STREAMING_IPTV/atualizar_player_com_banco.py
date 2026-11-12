import json
import sqlite3
from pathlib import Path

PASTA_BASE = Path(r"C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
CAMINHO_BANCO = PASTA_BASE / "saida" / "banco_iptv.db"
DESKTOP = Path(r"C:\Users\jonas\Desktop")

conn = sqlite3.connect(CAMINHO_BANCO)
cur = conn.cursor()
cur.execute("""
    SELECT nome, url, logo, categoria, qualidade, latencia_ms
    FROM canais
    WHERE status = 'ATIVO'
    ORDER BY categoria, latencia_ms ASC;
""")
linhas = cur.fetchall()
conn.close()

todos = []
for r in linhas:
    todos.append({
        "nome": r[0],
        "url": r[1],
        "logo": r[2],
        "categoria": r[3],
        "qualidade": r[4],
        "latencia_ms": r[5]
    })

# Lê o template base existente e injeta os 143 canais
template_atual = (PASTA_BASE / "saida" / "index.html").read_text(encoding="utf-8")
import re
# Substitui o array de canais no script
novo_html = re.sub(r'const canais = \[.*?\];', f'const canais = {json.dumps(todos, ensure_ascii=False)};', template_atual, flags=re.DOTALL)
novo_html = re.sub(r'<div class="badge">.*?</div>', f'<div class="badge">{len(todos)} Canais Prontos</div>', novo_html)
novo_html = re.sub(r'<button class="active" onclick="filtrarCategoria\(\'todas\'\)">.*?</button>', f'<button class="active" onclick="filtrarCategoria(\'todas\')">Todas ({len(todos)})</button>', novo_html)

(PASTA_BASE / "saida" / "index.html").write_text(novo_html, encoding="utf-8")
(DESKTOP / "ASSISTIR_TV.html").write_text(novo_html, encoding="utf-8")
print(f"[+] Player sincronizado com {len(todos)} canais ativos no banco de dados!")
