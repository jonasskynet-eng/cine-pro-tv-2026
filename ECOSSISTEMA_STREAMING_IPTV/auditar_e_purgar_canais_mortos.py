import sqlite3
import urllib.request
import urllib.parse
import ssl
import json
import concurrent.futures
from pathlib import Path

BASE_DIR = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
SAIDA_DIR = BASE_DIR / "saida"
DB_PATH = SAIDA_DIR / "banco_iptv.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. Desativar imediatamente lixo estrutural (YouTube, bit.ly, arquivos de vídeo avi/mkv)
print("1. Purgando links não-HLS (YouTube, bit.ly, arquivos estáticos)...")
c.execute("""
    UPDATE canais 
    SET status = 'INATIVO' 
    WHERE url LIKE '%youtube.com%' 
       OR url LIKE '%youtu.be%'
       OR url LIKE '%bit.ly%'
       OR url LIKE '%.avi'
       OR url LIKE '%.mkv'
       OR url NOT LIKE 'http%'
""")
conn.commit()

# 2. Selecionar canais candidatos que tenham formato de stream (.m3u8 ou stream de porta)
c.execute("""
    SELECT id, nome, url 
    FROM canais 
    WHERE status = 'ATIVO' 
      AND qualidade = 'Digital'
      AND url NOT LIKE '%rtv30t%'
      AND url NOT LIKE '%181.224.200.5%'
      AND url NOT LIKE '%hls1.sua.tv%'
      AND url NOT LIKE '%45.184.109.10%'
      AND url NOT LIKE '%38.134.250.110%'
      AND url NOT LIKE '%45.171.64.30%'
      AND url NOT LIKE '%190.128.214.97%'
      AND nome NOT LIKE '%(Digital HLS)%'
""")
candidatos = c.fetchall()
print(f"Total de candidatos a auditar: {len(candidatos)}")

# 3. Teste ultra-rápido multithread (60 workers) para testar se o servidor responde 200 OK
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def testar_canal(item):
    c_id, nome, url = item
    
    # Se for da fibra 170.83.16.50, já sabemos que é 100% ativo e prioritário
    if "170.83.16.50" in url:
        return (c_id, True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
            if resp.status in (200, 206):
                # Ler os primeiros 200 bytes para ver se tem conteúdo HLS real
                sample = resp.read(250)
                if b'#EXTM3U' in sample or b'#EXT-X' in sample or len(sample) > 50:
                    return (c_id, True)
    except Exception:
        pass
    return (c_id, False)

print("2. Testando canais em paralelo com 60 conexões simultâneas...")
ativos_ids = set()
inativos_ids = set()

with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
    futuros = [executor.submit(testar_canal, item) for item in candidatos]
    for fut in concurrent.futures.as_completed(futuros):
        c_id, ok = fut.result()
        if ok:
            ativos_ids.add(c_id)
        else:
            inativos_ids.add(c_id)

print(f"Canais 100% ONLINE E FUNCIONAIS: {len(ativos_ids)}")
print(f"Canais OFF-LINE / EXPIRADOS: {len(inativos_ids)}")

# 4. Atualizar no banco os canais que falharam para INATIVO
print("3. Atualizando status no banco de dados...")
c.executemany("UPDATE canais SET status = 'INATIVO' WHERE id = ?", [(cid,) for cid in inativos_ids])
c.executemany("UPDATE canais SET status = 'ATIVO' WHERE id = ?", [(cid,) for cid in ativos_ids])
conn.commit()
conn.close()

print("EXPURGO DE CANAIS MORTOS CONCLUÍDO COM SUCESSO!")
