import http.server
import socketserver
import urllib.request
import urllib.parse
import ssl
import sys
import os
import re
import socket
import json
import threading
import gzip
import zlib
import time
import sqlite3
import random
from pathlib import Path

def decodificar_manifesto(raw_bytes, content_encoding=''):
    """Decodifica bytes de playlist HLS tratando gzip/deflate quando presentes."""
    enc = (content_encoding or '').lower()
    if raw_bytes[:2] == b'\x1f\x8b' or 'gzip' in enc:
        try:
            raw_bytes = gzip.decompress(raw_bytes)
        except Exception:
            pass
    elif 'deflate' in enc:
        try:
            raw_bytes = zlib.decompress(raw_bytes)
        except Exception:
            try:
                raw_bytes = zlib.decompress(raw_bytes, -zlib.MAX_WBITS)
            except Exception:
                pass
    return raw_bytes.decode('utf-8', errors='ignore')

PORT = int(os.environ.get("PORT", "8080"))
CINEPRO_MODO = os.environ.get("CINEPRO_MODO", "LOCAL").strip().upper()
CINEPRO_VIP_TOKEN = os.environ.get("CINEPRO_VIP_TOKEN", "").strip()
VIP_M3U_URL = os.environ.get("VIP_M3U_URL", "").strip()
CINEPRO_CLOUD_SYNC_URL = os.environ.get("CINEPRO_CLOUD_SYNC_URL", "").strip()
CINEPRO_CLOUD_SYNC_TOKEN = os.environ.get("CINEPRO_CLOUD_SYNC_TOKEN", "").strip()
PIX_WEBHOOK_SECRET = os.environ.get("PIX_WEBHOOK_SECRET", "").strip()

_BASE_SCRIPT = Path(__file__).resolve().parent
_STATIC_ENV = os.environ.get("CINEPRO_STATIC_DIR", "").strip()
if _STATIC_ENV and Path(_STATIC_ENV).exists():
    DIRETORIO_SAIDA = Path(_STATIC_ENV)
elif (_BASE_SCRIPT.parent / "docs").exists():
    DIRETORIO_SAIDA = _BASE_SCRIPT.parent / "docs"
else:
    DIRETORIO_SAIDA = _BASE_SCRIPT / "saida"

DIRETORIO_VIP = Path(os.environ.get("CINEPRO_VIP_DIR", str(_BASE_SCRIPT / "vip_privado")))
DIRETORIO_VIP.mkdir(parents=True, exist_ok=True)
ARQUIVO_CLIENTES_VIP = DIRETORIO_VIP / "clientes_vip.json"
ARQUIVO_BANCO_VIP = DIRETORIO_VIP / "banco_clientes_vip.db"
CINEPRO_ADMIN_PIN = os.environ.get("CINEPRO_ADMIN_PIN", "jonas2026").strip() or "jonas2026"
LOCK_CLIENTES = threading.Lock()
LOCK_SESSOES = threading.Lock()
_SESSOES_ATIVAS = {}

def _abrir_conexao_vip():
    conn = sqlite3.connect(str(ARQUIVO_BANCO_VIP), timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def _inicializar_banco_vip():
    with LOCK_CLIENTES:
        conn = _abrir_conexao_vip()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS planos_assinatura (
                    codigo TEXT PRIMARY KEY,
                    descricao TEXT NOT NULL,
                    duracao_horas REAL NOT NULL,
                    padrao_telas INTEGER NOT NULL DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    plano_codigo TEXT REFERENCES planos_assinatura(codigo),
                    expira_em INTEGER NOT NULL,
                    max_telas INTEGER NOT NULL DEFAULT 1,
                    ativo INTEGER NOT NULL DEFAULT 1,
                    criado_em INTEGER NOT NULL,
                    atualizado_em INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessoes_ativas (
                    usuario TEXT NOT NULL,
                    ip_cliente TEXT NOT NULL,
                    ultimo_acesso REAL NOT NULL,
                    PRIMARY KEY (usuario, ip_cliente)
                );

                CREATE TABLE IF NOT EXISTS config_sistema (
                    chave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS pendencias_roadmap (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ordem INTEGER NOT NULL,
                    titulo TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDENTE'
                );

                CREATE TABLE IF NOT EXISTS pagamentos_pix (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    txid TEXT UNIQUE NOT NULL,
                    provedor TEXT NOT NULL,
                    cliente_usuario TEXT NOT NULL,
                    valor REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL,
                    criado_em INTEGER NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_clientes_usuario ON clientes(usuario);
                CREATE INDEX IF NOT EXISTS idx_sessoes_ultimo_acesso ON sessoes_ativas(ultimo_acesso);
                CREATE INDEX IF NOT EXISTS idx_pagamentos_pix_usuario ON pagamentos_pix(cliente_usuario);

                CREATE TRIGGER IF NOT EXISTS trg_clientes_updated_at
                AFTER UPDATE ON clientes
                FOR EACH ROW
                BEGIN
                    UPDATE clientes SET atualizado_em = CAST(strftime('%s', 'now') AS INTEGER) WHERE id = NEW.id;
                END;
            """)

            planos_base = [
                ("TESTE_3H", "Teste Rápido 3 Horas", 3.0, 1),
                ("MENSAL_30D", "Mensal 30 Dias", 720.0, 1),
                ("VITALICIO", "Acesso Vitalício Casa", 999999.0, 5),
            ]
            conn.executemany(
                "INSERT OR IGNORE INTO planos_assinatura (codigo, descricao, duracao_horas, padrao_telas) VALUES (?, ?, ?, ?)",
                planos_base
            )
            conn.execute(
                "INSERT OR IGNORE INTO config_sistema (chave, valor) VALUES ('exigir_login_clientes', '0')"
            )
            conn.execute(
                "INSERT OR IGNORE INTO config_sistema (chave, valor) VALUES ('vip_m3u_url', '')")

            qtd_cli = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
            if qtd_cli == 0:
                agora = int(time.time())
                # Migra JSON anterior caso exista
                if ARQUIVO_CLIENTES_VIP.exists():
                    try:
                        dados_json = json.loads(ARQUIVO_CLIENTES_VIP.read_text(encoding="utf-8", errors="ignore"))
                        if isinstance(dados_json, dict):
                            exigir_str = "1" if dados_json.get("exigir_login_clientes") else "0"
                            conn.execute(
                                "INSERT OR REPLACE INTO config_sistema (chave, valor) VALUES ('exigir_login_clientes', ?)",
                                (exigir_str,)
                            )
                            for c in dados_json.get("clientes", []):
                                conn.execute(
                                    """INSERT OR IGNORE INTO clientes
                                       (usuario, senha, nome, plano_codigo, expira_em, max_telas, ativo, criado_em, atualizado_em)
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                    (
                                        str(c.get("usuario", "")),
                                        str(c.get("senha", "")),
                                        str(c.get("nome", "")),
                                        "VITALICIO" if str(c.get("usuario", "")) == "vip" else "MENSAL_30D",
                                        int(c.get("expira_em", 4102444800)),
                                        int(c.get("max_telas", 1) or 1),
                                        1 if c.get("ativo", True) else 0,
                                        agora,
                                        agora
                                    )
                                )
                    except Exception:
                        pass

                if conn.execute("SELECT COUNT(*) FROM clientes WHERE usuario='vip'").fetchone()[0] == 0:
                    conn.execute(
                        """INSERT OR IGNORE INTO clientes
                           (usuario, senha, nome, plano_codigo, expira_em, max_telas, ativo, criado_em, atualizado_em)
                           VALUES ('vip', 'vip', 'Casa do Jonas (Vitalício)', 'VITALICIO', 4102444800, 5, 1, ?, ?)""",
                        (agora, agora)
                    )

            qtd_pend = conn.execute("SELECT COUNT(*) FROM pendencias_roadmap").fetchone()[0]
            if qtd_pend == 0:
                pendencias = [
                    (1, "Subir Docker VIP na nuvem 24h (Render / Hugging Face)", "PENDENTE"),
                    (2, "Ligar banco externo persistente na nuvem para não zerar clientes", "PENDENTE"),
                    (3, "Plugar lista paga com futebol ao vivo (Premiere, SporTV, ESPN, HBO)", "PENDENTE"),
                    (4, "Adicionar 2o e 3o links reserva nos canais gratuitos", "PENDENTE"),
                    (5, "Conectar guia de programação (EPG) completo nos canais 24h", "PENDENTE"),
                    (6, "Fixar IP da rede local na TV Samsung ou usar domínio fixo da nuvem", "PENDENTE"),
                    (7, "Integrar PIX automático para liberar acesso 24h sem WhatsApp manual", "PENDENTE"),
                    (8, "Trocar senha padrão jonas2026 antes de publicar o painel na internet", "PENDENTE"),
                ]
                conn.executemany(
                    "INSERT INTO pendencias_roadmap (ordem, titulo, status) VALUES (?, ?, ?)",
                    pendencias
                )

            conn.commit()
        finally:
            conn.close()

_inicializar_banco_vip()

def _obter_config_vip(chave, padrao=""):
    with LOCK_CLIENTES:
        conn = _abrir_conexao_vip()
        try:
            row = conn.execute("SELECT valor FROM config_sistema WHERE chave = ?", (chave,)).fetchone()
            return row[0] if row else padrao
        finally:
            conn.close()

def _definir_config_vip(chave, valor):
    with LOCK_CLIENTES:
        conn = _abrir_conexao_vip()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO config_sistema (chave, valor) VALUES (?, ?)",
                (chave, str(valor or ""))
            )
            conn.commit()
        finally:
            conn.close()

def _listar_pagamentos_pix(limite=15):
    with LOCK_CLIENTES:
        conn = _abrir_conexao_vip()
        try:
            rows = conn.execute(
                "SELECT txid, provedor, cliente_usuario, valor, status, criado_em FROM pagamentos_pix ORDER BY id DESC LIMIT ?",
                (limite,)
            ).fetchall()
            return [
                {
                    "txid": r[0], "provedor": r[1], "cliente_usuario": r[2],
                    "valor": float(r[3] or 0.0), "status": r[4], "criado_em": int(r[5])
                }
                for r in rows
            ]
        finally:
            conn.close()

def _puxar_backup_nuvem():
    if not CINEPRO_CLOUD_SYNC_URL or not CINEPRO_CLOUD_SYNC_TOKEN:
        return
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            CINEPRO_CLOUD_SYNC_URL,
            headers={"X-Admin-Senha": CINEPRO_CLOUD_SYNC_TOKEN, "User-Agent": "CinePro-Sync/1.0"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
            res = json.loads(resp.read().decode("utf-8", errors="ignore"))
        dados_remotos = res.get("dados") if isinstance(res, dict) else None
        if isinstance(dados_remotos, dict) and isinstance(dados_remotos.get("clientes"), list):
            _salvar_dados_clientes(dados_remotos, sincronizar_nuvem=False)
            if dados_remotos.get("vip_m3u_url"):
                _definir_config_vip("vip_m3u_url", dados_remotos["vip_m3u_url"])
    except Exception:
        pass

def _enviar_backup_nuvem(dados):
    if not CINEPRO_CLOUD_SYNC_URL or not CINEPRO_CLOUD_SYNC_TOKEN:
        return
    def _worker_sync():
        try:
            pacote = dict(dados)
            pacote["vip_m3u_url"] = _obter_config_vip("vip_m3u_url", VIP_M3U_URL)
            corpo = json.dumps(pacote, ensure_ascii=False).encode("utf-8")
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(
                CINEPRO_CLOUD_SYNC_URL,
                data=corpo,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "X-Admin-Senha": CINEPRO_CLOUD_SYNC_TOKEN,
                    "User-Agent": "CinePro-Sync/1.0"
                }
            )
            urllib.request.urlopen(req, context=ctx, timeout=6).read()
        except Exception:
            pass
    threading.Thread(target=_worker_sync, daemon=True).start()

def _processar_pagamento_pix(payload):
    """Cria ou renova um cliente de 30 dias a partir de um webhook PIX (Mercado Pago, Asaas ou direto)."""
    if not isinstance(payload, dict):
        return False, {"erro": "Payload inválido"}

    provedor = str(payload.get("provedor") or "").strip()
    txid = str(payload.get("txid") or payload.get("id") or "").strip()
    status_pag = str(payload.get("status") or "APROVADO").strip().upper()
    valor = float(payload.get("valor") or 0.0)
    nome_cli = str(payload.get("nome") or "").strip()
    usuario_req = str(payload.get("usuario") or "").strip()
    dias = float(payload.get("dias") or 30.0)
    telas = max(1, int(payload.get("telas") or 1))

    # Formato Mercado Pago
    if "data" in payload and isinstance(payload.get("data"), dict) and payload["data"].get("id"):
        provedor = provedor or "MercadoPago"
        txid = txid or f"MP-{payload['data']['id']}"
    # Formato Asaas
    elif "payment" in payload and isinstance(payload.get("payment"), dict):
        provedor = provedor or "Asaas"
        pay = payload["payment"]
        txid = txid or str(pay.get("id") or "")
        valor = float(pay.get("value") or valor or 0.0)
        status_pag = str(payload.get("event") or pay.get("status") or status_pag).upper()
        if not nome_cli and pay.get("description"):
            nome_cli = str(pay.get("description"))

    provedor = provedor or "PIX Direto"
    if not txid:
        txid = f"PIX-{int(time.time())}-{random.randint(100, 999)}"

    with LOCK_CLIENTES:
        conn = _abrir_conexao_vip()
        try:
            ja_existe = conn.execute(
                "SELECT cliente_usuario, valor, status FROM pagamentos_pix WHERE txid = ?",
                (txid,)
            ).fetchone()
            if ja_existe:
                cli_row = conn.execute(
                    "SELECT usuario, senha, nome, expira_em, max_telas FROM clientes WHERE usuario = ?",
                    (ja_existe[0],)
                ).fetchone()
                return True, {
                    "ok": True,
                    "duplicado": True,
                    "pagamento": {"txid": txid, "provedor": provedor, "cliente_usuario": ja_existe[0], "valor": ja_existe[1], "status": ja_existe[2]},
                    "cliente": {
                        "usuario": cli_row[0], "senha": cli_row[1], "nome": cli_row[2],
                        "expira_em": cli_row[3], "max_telas": cli_row[4]
                    } if cli_row else None
                }
        finally:
            conn.close()

    dados = _carregar_dados_clientes()
    clientes = dados.get("clientes", [])
    agora = time.time()
    horas = max(1.0, dias * 24.0)

    cli_existente = next((c for c in clientes if usuario_req and c.get("usuario") == usuario_req), None)
    if cli_existente:
        base_tempo = max(agora, float(cli_existente.get("expira_em", agora)))
        cli_existente["expira_em"] = int(base_tempo + horas * 3600.0)
        cli_existente["ativo"] = True
        cli_final = cli_existente
    else:
        usuario_novo = usuario_req or f"pix{random.randint(1000, 9999)}"
        while any(c.get("usuario") == usuario_novo for c in clientes):
            usuario_novo = f"pix{random.randint(1000, 9999)}"
        senha_nova = str(random.randint(100000, 999999))
        cli_final = {
            "usuario": usuario_novo,
            "senha": senha_nova,
            "nome": nome_cli or f"Cliente PIX {usuario_novo}",
            "expira_em": int(agora + horas * 3600.0),
            "max_telas": telas,
            "ativo": True
        }
        clientes.append(cli_final)

    dados["clientes"] = clientes
    _salvar_dados_clientes(dados)

    with LOCK_CLIENTES:
        conn = _abrir_conexao_vip()
        try:
            conn.execute(
                """INSERT INTO pagamentos_pix (txid, provedor, cliente_usuario, valor, status, criado_em)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (txid, provedor, cli_final["usuario"], valor, status_pag, int(agora))
            )
            conn.commit()
        finally:
            conn.close()

    return True, {
        "ok": True,
        "duplicado": False,
        "pagamento": {
            "txid": txid,
            "provedor": provedor,
            "cliente_usuario": cli_final["usuario"],
            "valor": valor,
            "status": status_pag
        },
        "cliente": cli_final
    }

def _carregar_dados_clientes():
    with LOCK_CLIENTES:
        conn = _abrir_conexao_vip()
        try:
            row_cfg = conn.execute("SELECT valor FROM config_sistema WHERE chave='exigir_login_clientes'").fetchone()
            exigir = (row_cfg[0] == "1") if row_cfg else False
            rows = conn.execute(
                "SELECT usuario, senha, nome, expira_em, max_telas, ativo FROM clientes ORDER BY id ASC"
            ).fetchall()
            clientes = [
                {
                    "usuario": r[0],
                    "senha": r[1],
                    "nome": r[2],
                    "expira_em": int(r[3]),
                    "max_telas": int(r[4]),
                    "ativo": bool(r[5])
                }
                for r in rows
            ]
            return {"exigir_login_clientes": exigir, "clientes": clientes}
        finally:
            conn.close()

def _salvar_dados_clientes(dados, sincronizar_nuvem=True):
    with LOCK_CLIENTES:
        conn = _abrir_conexao_vip()
        try:
            exigir_str = "1" if dados.get("exigir_login_clientes") else "0"
            conn.execute(
                "INSERT OR REPLACE INTO config_sistema (chave, valor) VALUES ('exigir_login_clientes', ?)",
                (exigir_str,)
            )
            clientes_novos = dados.get("clientes", [])
            usuarios_novos = {str(c.get("usuario", "")).strip() for c in clientes_novos if c.get("usuario")}
            existentes = {r[0] for r in conn.execute("SELECT usuario FROM clientes").fetchall()}
            for u_rem in (existentes - usuarios_novos):
                if u_rem != "vip":
                    conn.execute("DELETE FROM clientes WHERE usuario = ?", (u_rem,))

            agora = int(time.time())
            for c in clientes_novos:
                u = str(c.get("usuario", "")).strip()
                if not u:
                    continue
                plano = "VITALICIO" if u == "vip" else "MENSAL_30D"
                if u in existentes:
                    conn.execute(
                        """UPDATE clientes
                           SET senha = ?, nome = ?, expira_em = ?, max_telas = ?, ativo = ?
                           WHERE usuario = ?""",
                        (
                            str(c.get("senha", "")),
                            str(c.get("nome", u)),
                            int(c.get("expira_em", agora)),
                            int(c.get("max_telas", 1) or 1),
                            1 if c.get("ativo", True) else 0,
                            u
                        )
                    )
                else:
                    conn.execute(
                        """INSERT INTO clientes
                           (usuario, senha, nome, plano_codigo, expira_em, max_telas, ativo, criado_em, atualizado_em)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            u,
                            str(c.get("senha", "")),
                            str(c.get("nome", u)),
                            plano,
                            int(c.get("expira_em", agora)),
                            int(c.get("max_telas", 1) or 1),
                            1 if c.get("ativo", True) else 0,
                            agora,
                            agora
                        )
                    )
            conn.commit()
        finally:
            conn.close()

def _listar_pagamentos_pix(limite=15):
    with LOCK_CLIENTES:
        conn = _abrir_conexao_vip()
        try:
            rows = conn.execute(
                "SELECT txid, provedor, cliente_usuario, valor, status, criado_em FROM pagamentos_pix ORDER BY id DESC LIMIT ?",
                (limite,)
            ).fetchall()
            return [
                {
                    "txid": r[0], "provedor": r[1], "cliente_usuario": r[2],
                    "valor": float(r[3] or 0.0), "status": r[4], "criado_em": int(r[5])
                }
                for r in rows
            ]
        finally:
            conn.close()

def _autorizar_acesso_cliente(usuario, senha, ip_cliente, registrar_tela=False):
    dados = _carregar_dados_clientes()
    agora = time.time()
    cli = next((c for c in dados.get("clientes", []) if str(c.get("usuario", "")).strip() == usuario), None)
    if cli is not None:
        if str(cli.get("senha", "")) != senha:
            return False, "Senha incorreta", cli
        if not cli.get("ativo", True):
            return False, "Cliente bloqueado", cli
        if agora >= float(cli.get("expira_em", 0)):
            return False, "Assinatura vencida", cli
        if registrar_tela:
            with LOCK_SESSOES:
                expiradas = [k for k, ts in _SESSOES_ATIVAS.items() if agora - ts > 45.0]
                for k in expiradas:
                    del _SESSOES_ATIVAS[k]
                ips_ativos = {k[1] for k in _SESSOES_ATIVAS if k[0] == usuario}
                max_telas = int(cli.get("max_telas", 1) or 1)
                if ip_cliente not in ips_ativos and len(ips_ativos) >= max_telas:
                    return False, "Limite de telas simultâneas atingido", cli
                _SESSOES_ATIVAS[(usuario, ip_cliente)] = agora
        return True, "OK", cli

    if dados.get("exigir_login_clientes"):
        return False, "Usuário não cadastrado", None
    if CINEPRO_VIP_TOKEN and senha != CINEPRO_VIP_TOKEN:
        return False, "Chave VIP inválida", None
    return True, "Modo Aberto", None

_CACHE_VIP = {
    "assinatura_arquivos": None,
    "url_remota": "",
    "expira_remoto": 0.0,
    "canais": []
}

def _classificar_tags_vip(nome: str, grupo: str):
    texto = f"{nome} {grupo}".lower()
    tags = ["vip"]
    mapa = [
        ("esportes", ["esport", "sport", "premiere", "combate", "espn", "fox sports", "caze", "futebol", "nba", "ufc"]),
        ("filmes", ["filme", "movie", "cine", "hbo", "telecine", "megapix", "tnt", "space", "cinemax", "paramount"]),
        ("series", ["serie", "série", "series", "warner", "axn", "sony", "universal", "star channel", "fx"]),
        ("infantil", ["kids", "infantil", "desenho", "cartoon", "disney", "discovery kids", "gloob", "nick"]),
        ("noticias", ["noticia", "notícia", "news", "cnn", "globonews", "bandnews", "jovem pan"]),
        ("aberta", ["globo", "sbt", "record", "band", "redetv", "cultura"]),
        ("comedia", ["comedia", "comédia", "comedy", "humor", "multishow"]),
        ("musica", ["music", "música", "mtv", "show", "bis", "radio", "rádio"]),
    ]
    for tag, termos in mapa:
        if any(t in texto for t in termos):
            tags.append(tag)
    return tags

def _parse_conteudo_m3u_vip(conteudo: str, canais_out: list, urls_vistas: set):
    nome_atual = ""
    grupo_atual = "⭐ Pacote VIP"
    logo_atual = ""
    for linha in conteudo.splitlines():
        l = linha.strip()
        if not l:
            continue
        if l.startswith("#EXTINF"):
            m_logo = re.search(r'tvg-logo="([^"]*)"', l, re.I)
            m_grupo = re.search(r'group-title="([^"]*)"', l, re.I)
            logo_atual = m_logo.group(1).strip() if m_logo else ""
            grupo_atual = (m_grupo.group(1).strip() if m_grupo else "") or "⭐ Pacote VIP"
            nome_atual = l.split(",")[-1].strip() if "," in l else "Canal VIP"
        elif l.startswith("http://") or l.startswith("https://"):
            if l not in urls_vistas:
                urls_vistas.add(l)
                idx = len(canais_out)
                nome_final = nome_atual or f"Canal VIP {idx + 1}"
                num = 201 + idx
                canais_out.append({
                    "id": 90001 + idx,
                    "numero": num,
                    "numero_str": f"{num:03d}",
                    "nome": nome_final,
                    "url": l,
                    "logo": logo_atual,
                    "categoria": grupo_atual,
                    "pais": "🇧🇷 Brasil",
                    "pais_codigo": "BR",
                    "idioma_badge": "👑 VIP",
                    "tags": _classificar_tags_vip(nome_final, grupo_atual),
                    "cors": 0
                })
            nome_atual = ""
            grupo_atual = "⭐ Pacote VIP"
            logo_atual = ""

def carregar_canais_vip_extras():
    """Carrega listas VIP (.json, .m3u/.m3u8) da pasta privada e de VIP_M3U_URL com cache em memória."""
    arquivos_json = sorted(list(DIRETORIO_VIP.glob("*.json")), key=lambda p: p.name.lower())
    arquivos_m3u = sorted(
        list(DIRETORIO_VIP.glob("*.m3u")) + list(DIRETORIO_VIP.glob("*.m3u8")),
        key=lambda p: p.name.lower()
    )
    arquivos = arquivos_json + arquivos_m3u
    assinatura = tuple((str(p), p.stat().st_mtime) for p in arquivos)
    agora = time.monotonic()
    vip_url_ativa = (_obter_config_vip("vip_m3u_url", "") or VIP_M3U_URL).strip()
    remoto_valido = (not vip_url_ativa) or (
        _CACHE_VIP["url_remota"] == vip_url_ativa and agora < _CACHE_VIP["expira_remoto"]
    )
    if _CACHE_VIP["assinatura_arquivos"] == assinatura and remoto_valido:
        return _CACHE_VIP["canais"]

    canais = []
    urls_vistas = set()

    for arq_json in arquivos_json:
        try:
            itens = json.loads(arq_json.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(itens, list):
                for item in itens:
                    if not isinstance(item, dict):
                        continue
                    url_item = str(item.get("url", "")).strip()
                    if not url_item or url_item in urls_vistas:
                        continue
                    urls_vistas.add(url_item)
                    novo = dict(item)
                    tags_atuais = list(novo.get("tags") or [])
                    if "vip" not in tags_atuais:
                        tags_atuais.append("vip")
                    novo["tags"] = tags_atuais
                    num = 201 + len(canais)
                    novo["n"] = num
                    novo["numero"] = num
                    novo["numero_str"] = f"{num:03d}"
                    canais.append(novo)
        except Exception:
            pass

    for arq in arquivos_m3u:
        try:
            texto = arq.read_text(encoding="utf-8", errors="ignore")
            _parse_conteudo_m3u_vip(texto, canais, urls_vistas)
        except Exception:
            pass

    if vip_url_ativa:
        try:
            ctx_vip = ssl.create_default_context()
            ctx_vip.check_hostname = False
            ctx_vip.verify_mode = ssl.CERT_NONE
            req_vip = urllib.request.Request(vip_url_ativa, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_vip, context=ctx_vip, timeout=12) as resp_vip:
                texto_remoto = decodificar_manifesto(
                    resp_vip.read(),
                    resp_vip.headers.get("Content-Encoding", "")
                )
                _parse_conteudo_m3u_vip(texto_remoto, canais, urls_vistas)
        except Exception:
            pass

    _CACHE_VIP["assinatura_arquivos"] = assinatura
    _CACHE_VIP["url_remota"] = vip_url_ativa
    _CACHE_VIP["expira_remoto"] = agora + 900.0
    _CACHE_VIP["canais"] = canais
    return canais

def carregar_catalogo_completo_unificado():
    """Retorna todos os canais base (canais.json) somados aos canais VIP privados."""
    lista = []
    urls_vistas = set()
    base_json = DIRETORIO_SAIDA / "canais.json"
    if base_json.exists():
        try:
            itens = json.loads(base_json.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(itens, list):
                for item in itens:
                    if not isinstance(item, dict):
                        continue
                    u = str(item.get("url", "")).strip()
                    if not u or u in urls_vistas:
                        continue
                    urls_vistas.add(u)
                    num = item.get("n", item.get("numero", len(lista) + 1))
                    lista.append({
                        "id": int(item.get("id", num)),
                        "numero": int(num),
                        "nome": str(item.get("nome", "Canal")),
                        "url": u,
                        "logo": str(item.get("logo", "")),
                        "categoria": str(item.get("cat", item.get("categoria", "📺 TV Aberta")))
                    })
        except Exception:
            pass

    for vip in carregar_canais_vip_extras():
        u = str(vip.get("url", "")).strip()
        if not u or u in urls_vistas:
            continue
        urls_vistas.add(u)
        num = vip.get("n", vip.get("numero", len(lista) + 1))
        lista.append({
            "id": int(vip.get("id", num)),
            "numero": int(num),
            "nome": str(vip.get("nome", "Canal VIP")),
            "url": u,
            "logo": str(vip.get("logo", "")),
            "categoria": str(vip.get("cat", vip.get("categoria", "⭐ Pacote VIP")))
        })
    return lista

def _validar_credencial_tv(params):
    if not CINEPRO_VIP_TOKEN:
        return True
    senha = (params.get("password", [""])[0] or params.get("chave", [""])[0] or "").strip()
    return senha == CINEPRO_VIP_TOKEN

def _gerar_categorias_xtream(catalogo):
    mapa = {}
    cats = []
    for ch in catalogo:
        cname = ch["categoria"] or "📺 TV Aberta"
        if cname not in mapa:
            cid = str(len(cats) + 1)
            mapa[cname] = cid
            cats.append({"category_id": cid, "category_name": cname, "parent_id": 0})
    return mapa, cats

# Fila sincronizada de comandos remotos (Celular -> TV)
LOCK_COMANDOS = threading.Lock()
COMANDOS_PENDENTES = []
STATUS_TV = {
    "canal_numero": 1,
    "canal_nome": "SBT Nacional HD",
    "pausado": False,
    "volume": 100,
    "mudo": False
}

def obter_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class ServidorMultithreadStreaming(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRETORIO_SAIDA), **kwargs)

    def log_message(self, format, *args):
        # Evita AttributeError quando executado em segundo plano via pythonw.exe (sys.stderr=None)
        if sys.stderr is not None:
            try:
                super().log_message(format, *args)
            except Exception:
                pass

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Expose-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        parsed_post = urllib.parse.urlparse(self.path)
        if parsed_post.path == '/api/webhook/pix':
            params_p = urllib.parse.parse_qs(parsed_post.query)
            if PIX_WEBHOOK_SECRET:
                segredo_req = (
                    self.headers.get('X-Pix-Secret', '')
                    or params_p.get('secret', [''])[0]
                ).strip()
                if segredo_req != PIX_WEBHOOK_SECRET:
                    payload = json.dumps({"ok": False, "erro": "Segredo PIX inválido."}).encode('utf-8')
                    self.send_response(401)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Content-Length', str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                    return

            tam = int(self.headers.get('Content-Length', '0') or '0')
            bruto = self.rfile.read(min(tam, 1024 * 256)) if tam > 0 else b'{}'
            try:
                dados_pix = json.loads(bruto.decode('utf-8', errors='ignore') or '{}')
            except Exception:
                dados_pix = {}

            ok_pix, res_pix = _processar_pagamento_pix(dados_pix)
            status_http = 200 if ok_pix else 400
            payload = json.dumps(res_pix, ensure_ascii=False).encode('utf-8')
            self.send_response(status_http)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.end_headers()

    def do_HEAD(self):
        rota = urllib.parse.urlparse(self.path).path
        if rota in ('/', '/index.html', '/tv', '/tv/', '/tv.html', '/admin', '/admin/', '/admin.html', '/healthz', '/api/status_servidor', '/msx/start.json', '/start.json'):
            self.send_response(200)
            ctype = 'application/json' if rota in ('/healthz', '/api/status_servidor', '/msx/start.json', '/start.json') else 'text/html; charset=utf-8'
            self.send_header('Content-Type', ctype)
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        parsed_req = urllib.parse.urlparse(self.path)
        rota_req = parsed_req.path

        if rota_req == '/api/admin/clientes':
            params_adm = urllib.parse.parse_qs(parsed_req.query)
            pin_enviado = (params_adm.get('pin', [''])[0] or self.headers.get('X-Admin-Pin', '')).strip()
            if pin_enviado != CINEPRO_ADMIN_PIN:
                payload = json.dumps({"ok": False, "erro": "PIN incorreto."}).encode('utf-8')
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            dados = _carregar_dados_clientes()
            agora = time.time()
            with LOCK_SESSOES:
                expiradas = [k for k, ts in _SESSOES_ATIVAS.items() if agora - ts > 45.0]
                for k in expiradas:
                    del _SESSOES_ATIVAS[k]
                sessoes_snap = list(_SESSOES_ATIVAS.keys())

            lista_clientes = []
            for c in dados.get("clientes", []):
                u = str(c.get("usuario", ""))
                exp = float(c.get("expira_em", 0))
                restante_seg = max(0.0, exp - agora)
                telas_on = len({k[1] for k in sessoes_snap if k[0] == u})
                lista_clientes.append({
                    "usuario": u,
                    "senha": str(c.get("senha", "")),
                    "nome": str(c.get("nome", u)),
                    "expira_em": exp,
                    "dias_restantes": round(restante_seg / 86400.0, 1),
                    "horas_restantes": round(restante_seg / 3600.0, 1),
                    "vencido": agora >= exp,
                    "max_telas": int(c.get("max_telas", 1) or 1),
                    "telas_online": telas_on,
                    "ativo": bool(c.get("ativo", True))
                })

            payload = json.dumps({
                "ok": True,
                "exigir_login_clientes": bool(dados.get("exigir_login_clientes", False)),
                "ip_local": obter_ip_local(),
                "porta_host": self.headers.get('Host') or f"{obter_ip_local()}:{PORT}",
                "vip_m3u_url": _obter_config_vip("vip_m3u_url", VIP_M3U_URL),
                "qtd_canais_vip": len(carregar_canais_vip_extras()),
                "nuvem_sync_ativa": bool(CINEPRO_CLOUD_SYNC_URL and CINEPRO_CLOUD_SYNC_TOKEN),
                "pagamentos_pix": _listar_pagamentos_pix(15),
                "clientes": lista_clientes
            }, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if rota_req == '/api/admin/acao':
            params_adm = urllib.parse.parse_qs(parsed_req.query)
            pin_enviado = (params_adm.get('pin', [''])[0] or self.headers.get('X-Admin-Pin', '')).strip()
            if pin_enviado != CINEPRO_ADMIN_PIN:
                payload = json.dumps({"ok": False, "erro": "PIN incorreto."}).encode('utf-8')
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            acao = (params_adm.get('acao', [''])[0] or '').strip()
            dados = _carregar_dados_clientes()
            clientes = dados.get("clientes", [])
            agora = time.time()

            if acao == 'criar':
                usuario = (params_adm.get('usuario', [''])[0] or '').strip()
                senha = (params_adm.get('senha', [''])[0] or '').strip()
                nome = (params_adm.get('nome', [usuario])[0] or usuario).strip()
                try:
                    horas = float(params_adm.get('horas', ['720'])[0] or '720')
                except Exception:
                    horas = 720.0
                try:
                    max_telas = max(1, int(params_adm.get('max_telas', ['1'])[0] or '1'))
                except Exception:
                    max_telas = 1

                if not usuario or not senha:
                    payload = json.dumps({"ok": False, "erro": "Informe usuário e senha."}).encode('utf-8')
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(payload)
                    return

                existente = next((c for c in clientes if c.get("usuario") == usuario), None)
                novo_obj = {
                    "usuario": usuario,
                    "senha": senha,
                    "nome": nome,
                    "expira_em": int(agora + horas * 3600.0),
                    "max_telas": max_telas,
                    "ativo": True
                }
                if existente:
                    existente.update(novo_obj)
                else:
                    clientes.append(novo_obj)
                dados["clientes"] = clientes
                _salvar_dados_clientes(dados)

            elif acao == 'renovar':
                usuario = (params_adm.get('usuario', [''])[0] or '').strip()
                cli = next((c for c in clientes if c.get("usuario") == usuario), None)
                if cli:
                    base_tempo = max(agora, float(cli.get("expira_em", agora)))
                    cli["expira_em"] = int(base_tempo + 720 * 3600)
                    cli["ativo"] = True
                    _salvar_dados_clientes(dados)

            elif acao == 'alternar':
                usuario = (params_adm.get('usuario', [''])[0] or '').strip()
                cli = next((c for c in clientes if c.get("usuario") == usuario), None)
                if cli and usuario != "vip":
                    cli["ativo"] = not bool(cli.get("ativo", True))
                    _salvar_dados_clientes(dados)

            elif acao == 'excluir':
                usuario = (params_adm.get('usuario', [''])[0] or '').strip()
                if usuario != "vip":
                    dados["clientes"] = [c for c in clientes if c.get("usuario") != usuario]
                    _salvar_dados_clientes(dados)

            elif acao == 'modo_cobranca':
                dados["exigir_login_clientes"] = not bool(dados.get("exigir_login_clientes", False))
                _salvar_dados_clientes(dados)

            elif acao == 'salvar_vip_url':
                nova_url_vip = (params_adm.get('vip_m3u_url', [''])[0] or '').strip()
                _definir_config_vip("vip_m3u_url", nova_url_vip)
                _CACHE_VIP["assinatura_arquivos"] = None
                _CACHE_VIP["expira_remoto"] = 0.0
                _enviar_backup_nuvem(dados)
                qtd_rec = len(carregar_canais_vip_extras())
                payload = json.dumps({"ok": True, "qtd_canais_vip": qtd_rec}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            elif acao == 'simular_pix':
                _, res_sim = _processar_pagamento_pix({
                    "provedor": "Simulação Painel",
                    "valor": 29.90,
                    "dias": 30,
                    "telas": 1,
                    "status": "APROVADO"
                })
                payload = json.dumps(res_sim, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            payload = json.dumps({
                "ok": True,
                "exigir_login_clientes": bool(dados.get("exigir_login_clientes", False))
            }).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if rota_req in ('/msx/start.json', '/start.json'):
            host_header = self.headers.get('Host') or f"127.0.0.1:{PORT}"
            payload = json.dumps({
                "name": "CinePro TV Samsung",
                "version": "1.0.0",
                "parameter": f"menu:request:interaction:init@http://{host_header}/tv.html",
                "welcome": "none"
            }, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if rota_req == '/player_api.php':
            params_x = urllib.parse.parse_qs(parsed_req.query)
            username = (params_x.get('username', ['vip'])[0] or 'vip').strip()
            password = (params_x.get('password', ['vip'])[0] or 'vip').strip()
            action = (params_x.get('action', [''])[0] or '').strip()

            ok_cli, _, info_cli = _autorizar_acesso_cliente(username, password, self.client_address[0], registrar_tela=False)
            if not ok_cli:
                payload = json.dumps({"user_info": {"auth": 0, "status": "Disabled"}}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            catalogo = carregar_catalogo_completo_unificado()
            mapa_cats, lista_cats = _gerar_categorias_xtream(catalogo)

            if action == 'get_live_categories':
                payload = json.dumps(lista_cats, ensure_ascii=False).encode('utf-8')
            elif action == 'get_live_streams':
                cat_filtro = (params_x.get('category_id', [''])[0] or '').strip()
                streams = []
                for ch in catalogo:
                    cid = mapa_cats.get(ch["categoria"] or "📺 TV Aberta", "1")
                    if cat_filtro and cid != cat_filtro:
                        continue
                    streams.append({
                        "num": ch["numero"],
                        "name": ch["nome"],
                        "stream_type": "live",
                        "stream_id": ch["id"],
                        "stream_icon": ch["logo"],
                        "epg_channel_id": "",
                        "added": "1700000000",
                        "category_id": cid,
                        "custom_sid": "",
                        "tv_archive": 0,
                        "direct_source": "",
                        "tv_archive_duration": 0
                    })
                payload = json.dumps(streams, ensure_ascii=False).encode('utf-8')
            else:
                host_raw = self.headers.get('Host') or f"192.168.100.210:{PORT}"
                host_sem_porta = host_raw.split(':')[0]
                porta_host = host_raw.split(':')[1] if ':' in host_raw else "80"
                payload = json.dumps({
                    "user_info": {
                        "username": username,
                        "password": password,
                        "message": "CinePro TV VIP",
                        "auth": 1,
                        "status": "Active",
                        "exp_date": str(int(info_cli.get("expira_em", 1999999999))) if info_cli else "1999999999",
                        "is_trial": "0",
                        "active_cons": "1",
                        "created_at": "1700000000",
                        "max_connections": str(int(info_cli.get("max_telas", 5))) if info_cli else "5",
                        "allowed_output_formats": ["m3u8", "ts"]
                    },
                    "server_info": {
                        "url": host_sem_porta,
                        "port": porta_host,
                        "https_port": "443",
                        "server_protocol": "http",
                        "rtmp_port": "1935",
                        "timezone": "America/Sao_Paulo",
                        "timestamp_now": int(time.time()),
                        "time_now": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                }, ensure_ascii=False).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if rota_req in ('/get.php', '/vip.m3u'):
            params_m = urllib.parse.parse_qs(parsed_req.query)
            user_raw = (params_m.get('username', ['vip'])[0] or 'vip').strip()
            pass_raw = (params_m.get('password', [CINEPRO_VIP_TOKEN or 'vip'])[0] or 'vip').strip()
            ok_m, motivo_m, _ = _autorizar_acesso_cliente(user_raw, pass_raw, self.client_address[0], registrar_tela=False)
            if not ok_m:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(motivo_m.encode('utf-8', errors='ignore'))
                return
            user_m = urllib.parse.quote(user_raw, safe='')
            pass_m = urllib.parse.quote(pass_raw, safe='')
            host_m = self.headers.get('Host') or f"192.168.100.210:{PORT}"
            catalogo = carregar_catalogo_completo_unificado()
            linhas_m3u = ['#EXTM3U']
            for ch in catalogo:
                nome_limpo = ch["nome"].replace('"', "'")
                cat_limpa = (ch["categoria"] or "TV").replace('"', "'")
                linhas_m3u.append(
                    f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{nome_limpo}" tvg-logo="{ch["logo"]}" group-title="{cat_limpa}",{ch["nome"]}'
                )
                linhas_m3u.append(f'http://{host_m}/live/{user_m}/{pass_m}/{ch["id"]}.m3u8')
            body_m3u = ('\n'.join(linhas_m3u) + '\n').encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'audio/x-mpegurl; charset=utf-8')
            self.send_header('Content-Disposition', 'inline; filename="cinepro_vip.m3u"')
            self.send_header('Content-Length', str(len(body_m3u)))
            self.end_headers()
            self.wfile.write(body_m3u)
            return

        if rota_req.startswith('/live/'):
            partes_live = [p for p in rota_req.split('/') if p]
            if len(partes_live) >= 4:
                user_live = urllib.parse.unquote(partes_live[1])
                senha_live = urllib.parse.unquote(partes_live[2])
                ok_live, _, _ = _autorizar_acesso_cliente(user_live, senha_live, self.client_address[0], registrar_tela=True)
                if not ok_live:
                    self.send_response(401)
                    self.end_headers()
                    return
                m_id = re.match(r'^(\d+)', partes_live[3])
                if m_id:
                    sid = int(m_id.group(1))
                    canal_alvo = next((c for c in carregar_catalogo_completo_unificado() if c["id"] == sid), None)
                    if canal_alvo:
                        self.path = '/proxy?url=' + urllib.parse.quote(canal_alvo["url"], safe='')
                    else:
                        self.send_response(404)
                        self.end_headers()
                        return

        if rota_req == '/healthz':
            payload = json.dumps({
                "status": "ok",
                "modo": CINEPRO_MODO,
                "porta": PORT
            }).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if rota_req == '/api/status_servidor':
            canais_vip = carregar_canais_vip_extras()
            payload = json.dumps({
                "ativo": True,
                "modo": CINEPRO_MODO,
                "docker": (CINEPRO_MODO == "VIP_DOCKER"),
                "requer_chave": bool(CINEPRO_VIP_TOKEN),
                "qtd_vip_extras": len(canais_vip),
                "versao": "2026.4-VIP"
            }, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if rota_req == '/api/canais_vip':
            params_vip = urllib.parse.parse_qs(parsed_req.query)
            chave_enviada = (params_vip.get('chave', [''])[0] or self.headers.get('X-Vip-Token', '')).strip()
            if CINEPRO_VIP_TOKEN and chave_enviada != CINEPRO_VIP_TOKEN:
                payload = json.dumps({
                    "ok": False,
                    "requer_chave": True,
                    "erro": "Chave VIP inválida. Solicite no WhatsApp (11) 96670-7293."
                }, ensure_ascii=False).encode('utf-8')
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            canais_vip = carregar_canais_vip_extras()
            payload = json.dumps({
                "ok": True,
                "canais": canais_vip
            }, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # 1. API DE COMANDOS REMOTOS (CELULAR -> TV)
        if self.path.startswith('/api/comando'):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            cmd = params.get('cmd', [''])[0]
            val = params.get('val', [''])[0]
            with LOCK_COMANDOS:
                COMANDOS_PENDENTES.append({"cmd": cmd, "val": val})
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return

        elif self.path == '/api/ouvir_comandos':
            with LOCK_COMANDOS:
                cmds = list(COMANDOS_PENDENTES)
                COMANDOS_PENDENTES.clear()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(cmds).encode('utf-8'))
            return

        elif self.path.startswith('/api/status_tv'):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            for k, v in params.items():
                STATUS_TV[k] = v[0]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(STATUS_TV).encode('utf-8'))
            return

        elif self.path == '/api/obter_status_tv':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(STATUS_TV).encode('utf-8'))
            return

        elif self.path == '/api/ip_local':
            ip = obter_ip_local()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "ip": ip,
                "porta": PORT,
                "url_controle": f"http://{ip}:{PORT}/controle.html"
            }).encode('utf-8'))
            return

        # 2. PROXY DE STREAMING HLS
        if self.path.startswith('/proxy?url='):
            raw_url = self.path.split('/proxy?url=')[1]
            target_url = urllib.parse.unquote(raw_url)

            parsed_target = urllib.parse.urlparse(target_url)
            base_url = target_url.rsplit('/', 1)[0] + '/'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept-Encoding': 'identity',
                'Referer': base_url,
                'Origin': f"{parsed_target.scheme}://{parsed_target.netloc}"
            }
            if any(k in target_url.lower() for k in ['pluto.tv', 'plutotv.net', 'jmp2.uk', 'pluto']):
                headers['Origin'] = 'https://pluto.tv'
                headers['Referer'] = 'https://pluto.tv/'

            # Repassar cabeçalho de Range caso enviado pelo player
            if 'Range' in self.headers:
                headers['Range'] = self.headers['Range']

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            try:
                req = urllib.request.Request(target_url, headers=headers)
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    resp_status = resp.status if hasattr(resp, 'status') else 200
                    content_type = resp.headers.get('Content-Type', 'video/mp2t')
                    
                    # Pegar a URL FINAL após redirecionamentos (ex: jmp2.uk -> ipv4.pluto.tv)
                    final_url = resp.geturl()
                    parsed_final = urllib.parse.urlparse(final_url)
                    base_url = final_url.rsplit('/', 1)[0] + '/'

                    # Se a URL final for Pluto TV, garantir headers corretos para sub-requisições
                    if any(k in final_url.lower() for k in ['pluto.tv', 'plutotv.net']):
                        headers['Origin'] = 'https://pluto.tv'
                        headers['Referer'] = 'https://pluto.tv/'
                    
                    # 1. Se for arquivo de chave criptográfica AES-128 (.key), devolver bytes puros antes de qualquer parser de M3U8
                    eh_chave_aes = (
                        target_url.lower().endswith('.key')
                        or '.key?' in target_url.lower()
                        or 'keyfile' in target_url.lower()
                        or final_url.lower().endswith('.key')
                        or '.key?' in final_url.lower()
                    )
                    if eh_chave_aes:
                        key_data = resp.read()
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/octet-stream')
                        self.send_header('Content-Length', str(len(key_data)))
                        self.end_headers()
                        self.wfile.write(key_data)

                    # 2. Se for playlist M3U8, reescrevemos segmentos e tags #EXT-X-MAP / #EXT-X-KEY
                    elif 'mpegurl' in content_type.lower() or target_url.endswith('.m3u8') or '.m3u8?' in target_url or final_url.endswith('.m3u8') or '.m3u8?' in final_url:
                        raw_bytes = resp.read()
                        manifest = decodificar_manifesto(raw_bytes, resp.headers.get('Content-Encoding', ''))
                        if '#EXTM3U' not in manifest:
                            self.send_response(resp_status)
                            self.send_header('Content-Type', 'application/octet-stream')
                            self.send_header('Content-Length', str(len(raw_bytes)))
                            self.end_headers()
                            self.wfile.write(raw_bytes)
                            return

                        # Se for Master Playlist simples (#EXT-X-STREAM-INF sem áudio demuxado nem Pluto TV), achatamos para a sub-playlist ativa
                        if '#EXT-X-STREAM-INF' in manifest and '#EXT-X-MEDIA:' not in manifest and 'pluto' not in final_url.lower():
                            sub_cands = [l.strip() for l in manifest.splitlines() if l.strip() and not l.startswith('#')]
                            if sub_cands:
                                sub_target = sub_cands[0]
                                if not sub_target.startswith('http'):
                                    sub_target = urllib.parse.urljoin(base_url, sub_target)
                                try:
                                    req_sub = urllib.request.Request(sub_target, headers=headers)
                                    with urllib.request.urlopen(req_sub, context=ctx, timeout=8) as resp_sub:
                                        final_sub_url = resp_sub.geturl()
                                        sub_manifest = decodificar_manifesto(resp_sub.read(), resp_sub.headers.get('Content-Encoding', ''))
                                        if '#EXTM3U' in sub_manifest:
                                            manifest = sub_manifest
                                            base_url = final_sub_url.rsplit('/', 1)[0] + '/'
                                            parsed_final = urllib.parse.urlparse(final_sub_url)
                                except Exception:
                                    pass
                        
                        def resolver_link(link):
                            if link.startswith('http://') or link.startswith('https://'):
                                return '/proxy?url=' + urllib.parse.quote(link, safe='')
                            elif link.startswith('/'):
                                abs_u = f"{parsed_final.scheme}://{parsed_final.netloc}{link}"
                                return '/proxy?url=' + urllib.parse.quote(abs_u, safe='')
                            else:
                                abs_u = urllib.parse.urljoin(base_url, link)
                                return '/proxy?url=' + urllib.parse.quote(abs_u, safe='')

                        linhas_novas = []
                        for linha in manifest.splitlines():
                            l_strip = linha.strip()
                            if not l_strip:
                                continue
                            
                            # Tratar qualquer tag HLS com atributo URI="..." (#EXT-X-MEDIA, #EXT-X-MAP, #EXT-X-KEY, etc.)
                            if l_strip.startswith('#') and 'URI="' in l_strip:
                                l_strip = re.sub(r'URI="([^"]+)"', lambda m: f'URI="{resolver_link(m.group(1))}"', l_strip)
                                linhas_novas.append(l_strip)
                            elif not l_strip.startswith('#'):
                                linhas_novas.append(resolver_link(l_strip))
                            else:
                                linhas_novas.append(l_strip)
                                
                        body_modificado = '\n'.join(linhas_novas).encode('utf-8')
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/vnd.apple.mpegurl')
                        self.send_header('Content-Length', str(len(body_modificado)))
                        self.end_headers()
                        self.wfile.write(body_modificado)

                    # 3. Stream contínuo (.ts / mp4 / chunks de vídeo) em blocos com Keep-Alive
                    else:
                        self.send_response(resp_status)
                        self.send_header('Content-Type', content_type)
                        content_length = resp.headers.get('Content-Length')
                        if content_length:
                            self.send_header('Content-Length', content_length)
                        content_range = resp.headers.get('Content-Range')
                        if content_range:
                            self.send_header('Content-Range', content_range)
                        self.end_headers()
                        try:
                            while True:
                                chunk = resp.read(64 * 1024)
                                if not chunk:
                                    break
                                self.wfile.write(chunk)
                                self.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError):
                            pass
            except Exception as e:
                try:
                    self.send_response(502)
                    self.end_headers()
                    self.wfile.write(f"Erro Proxy: {e}".encode('utf-8'))
                except:
                    pass
        else:
            parsed_fb = urllib.parse.urlparse(self.path)
            rota_fb = parsed_fb.path
            ua = (self.headers.get('User-Agent') or '').lower()
            host_fb = (self.headers.get('Host') or '').lower()
            assinaturas_tv = ('tizen', 'smarttv', 'smart-tv', 'maple', 'web0s', 'webos', 'netcast', 'opera tv', 'vewd', 'hbbtv', 'vidaa')
            dominios_doadores = ('smart-stb', 'ottplayer', 'ivi.ru', 'tvigle', 'divan.tv')
            eh_tv_ou_dns = any(a in ua for a in assinaturas_tv) or any(d in host_fb for d in dominios_doadores)
            if rota_fb in ('/tv', '/tv/'):
                self.path = '/tv.html'
            elif rota_fb in ('/admin', '/admin/'):
                self.path = '/admin.html'
            elif rota_fb == '/' or self.path.startswith('/?'):
                if eh_tv_ou_dns and 'completo=1' not in parsed_fb.query:
                    self.path = '/tv.html'
                else:
                    self.path = '/index.html'
            super().do_GET()

# Servidor Threading (não trava com múltiplos requests simultâneos)
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == '__main__':
    try:
        _puxar_backup_nuvem()
        httpd = ThreadingHTTPServer(("", PORT), ServidorMultithreadStreaming)
        print(f"Servidor Multithread Ativo na porta {PORT}")
        httpd.serve_forever()
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
