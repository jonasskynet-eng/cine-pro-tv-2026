CREATE TABLE IF NOT EXISTS sessoes (
    sessao_id TEXT PRIMARY KEY,
    chave_cliente TEXT NOT NULL DEFAULT 'VISITANTE',
    app TEXT NOT NULL,
    ip TEXT NOT NULL,
    cidade TEXT NOT NULL DEFAULT '',
    regiao TEXT NOT NULL DEFAULT '',
    pais TEXT NOT NULL DEFAULT 'BR',
    dispositivo TEXT NOT NULL DEFAULT '',
    item_atual TEXT NOT NULL DEFAULT '',
    iniciado_em INTEGER NOT NULL,
    ultimo_sinal_em INTEGER NOT NULL,
    segundos_totais INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_sessoes_ultimo_sinal ON sessoes(ultimo_sinal_em DESC);
CREATE INDEX IF NOT EXISTS idx_sessoes_chave ON sessoes(chave_cliente);
CREATE INDEX IF NOT EXISTS idx_sessoes_ip ON sessoes(ip);

CREATE TABLE IF NOT EXISTS chaves_clientes (
    chave TEXT PRIMARY KEY,
    nome_cliente TEXT NOT NULL,
    plano TEXT NOT NULL DEFAULT 'TV e Rádio Casa R$ 30',
    max_ips INTEGER NOT NULL DEFAULT 2,
    ativa INTEGER NOT NULL DEFAULT 1,
    pagou INTEGER NOT NULL DEFAULT 0,
    expira_em INTEGER NOT NULL DEFAULT 0,
    criado_em INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS enquetes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao_id TEXT NOT NULL,
    chave_cliente TEXT NOT NULL DEFAULT 'VISITANTE',
    app TEXT NOT NULL,
    ip TEXT NOT NULL,
    cidade TEXT NOT NULL DEFAULT '',
    resposta TEXT NOT NULL,
    nota INTEGER DEFAULT 5,
    comentario TEXT DEFAULT '',
    respondido_em INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_enquetes_data ON enquetes(respondido_em DESC);

CREATE TABLE IF NOT EXISTS mensagens_admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    texto TEXT NOT NULL,
    link_whatsapp TEXT NOT NULL DEFAULT 'https://wa.me/5511966707293',
    ativa INTEGER NOT NULL DEFAULT 1,
    criado_em INTEGER NOT NULL
);
