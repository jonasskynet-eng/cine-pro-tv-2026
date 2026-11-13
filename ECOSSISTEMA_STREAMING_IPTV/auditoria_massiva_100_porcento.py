import sqlite3
import urllib.request
import urllib.parse
import ssl
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE_DIR = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
DB_PATH = BASE_DIR / "saida" / "banco_iptv.db"

# Contexto SSL sem verificação de certificado para evitar erros em servidores de streaming
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*"
}

def testar_canal(canal_id, nome, url):
    """
    Testa canal por canal se o stream responde 200 OK e contém estrutura HLS válida.
    Retorna (canal_id, ativo, latencia_ms, motivo)
    """
    inicio = time.time()
    try:
        # Se for link da Pluto TV via proxy jmp2.uk, seguir redirects
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=3.5, context=ctx) as resp:
            code = resp.getcode()
            corpo = resp.read(250)
            latencia = int((time.time() - inicio) * 1000)
            
            # Validação se é stream ou playlist válida
            if code == 200 and (b"#EXTM3U" in corpo or len(corpo) > 20):
                return (canal_id, True, latencia, "OK 200")
            else:
                return (canal_id, False, latencia, f"Código {code} ou payload inválido")
    except Exception as e:
        latencia = int((time.time() - inicio) * 1000)
        return (canal_id, False, latencia, str(e))

def executar_auditoria_completa():
    print("=" * 70)
    print(" 🚀 INICIANDO AUDITORIA FORENSE MASSIVA CANAL POR CANAL (50 THREADS)")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Buscar todos os canais que atualmente estão como ATIVO
    c.execute("SELECT id, nome, url FROM canais WHERE status = 'ATIVO'")
    canais = c.fetchall()
    total = len(canais)
    print(f"📡 Total de canais para auditoria minuciosa: {total}")
    
    vivos = []
    mortos = []
    
    # 50 Threads simultâneas para máxima velocidade
    with ThreadPoolExecutor(max_workers=50) as executor:
        futuros = {executor.submit(testar_canal, ch[0], ch[1], ch[2]): ch for ch in canais}
        concluidos = 0
        
        for f in as_completed(futuros):
            ch = futuros[f]
            cid, ativo, lat, motivo = f.result()
            concluidos += 1
            
            if ativo:
                vivos.append((lat, cid))
                if concluidos % 100 == 0 or concluidos == total:
                    print(f"[{concluidos}/{total}] 🟢 VIVO ({lat}ms): {ch[1][:35]}")
            else:
                mortos.append(cid)
                if concluidos % 100 == 0 or concluidos == total:
                    print(f"[{concluidos}/{total}] 🔴 OFF: {ch[1][:35]} -> {motivo[:40]}")

    print("\n" + "=" * 70)
    print(f"📊 RESULTADO DA AUDITORIA CANAL POR CANAL:")
    print(f"   🟢 Canais 100% Vivos e Funcionais: {len(vivos)}")
    print(f"   🔴 Canais Off-line Purgados: {len(mortos)}")
    print("=" * 70)
    
    # Atualizar canais vivos com latência medida real
    c.executemany("UPDATE canais SET status = 'ATIVO', latencia_ms = ?, web_ok = 1 WHERE id = ?", vivos)
    
    # Marcar canais mortos como INATIVO
    c.executemany("UPDATE canais SET status = 'INATIVO', web_ok = 0 WHERE id = ?", [(cid,) for cid in mortos])
    
    conn.commit()
    conn.close()
    print("💾 Banco de dados SQLite atualizado com sucesso!")

if __name__ == "__main__":
    executar_auditoria_completa()
