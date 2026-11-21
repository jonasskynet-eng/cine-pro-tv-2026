/**
 * CinePro TV & RádioPro — Ponte Nuvem + Painel de Telemetria (IP e Tempo Conectado)
 * Cloudflare Workers + Banco Gratuito D1
 */

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, HEAD, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-Admin-Senha",
  "Access-Control-Expose-Headers": "*",
};

function respostaCors(body, status = 200, extraHeaders = {}) {
  return new Response(body, {
    status,
    headers: {
      ...CORS_HEADERS,
      "Cache-Control": "no-store",
      ...extraHeaders,
    },
  });
}

function respostaJson(obj, status = 200) {
  return respostaCors(JSON.stringify(obj), status, {
    "Content-Type": "application/json; charset=utf-8",
  });
}

function ehHostPrivado(hostname) {
  const h = (hostname || "").toLowerCase();
  if (!h) return true;
  if (h === "localhost" || h.endsWith(".local")) return true;
  if (/^(127\.|10\.|192\.168\.|169\.254\.|0\.)/.test(h)) return true;
  const m172 = h.match(/^172\.(\d+)\./);
  if (m172 && Number(m172[1]) >= 16 && Number(m172[1]) <= 31) return true;
  return false;
}

function obterHeadersOrigem(targetUrl) {
  const parsed = new URL(targetUrl);
  const lower = targetUrl.toLowerCase();
  const headers = {
    "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    Accept: "*/*",
    Referer: `${parsed.origin}/`,
    Origin: parsed.origin,
  };

  if (
    lower.includes("pluto.tv") ||
    lower.includes("plutotv.net") ||
    lower.includes("jmp2.uk")
  ) {
    headers.Origin = "https://pluto.tv";
    headers.Referer = "https://pluto.tv/";
  }

  return headers;
}

function reescreverUrl(link, baseUrl, workerProxyBase) {
  try {
    const abs = new URL(link, baseUrl).toString();
    return `${workerProxyBase}?url=${encodeURIComponent(abs)}`;
  } catch {
    return link;
  }
}

function detectarDispositivo(ua) {
  const txt = (ua || "").toLowerCase();
  if (/tizen|web0s|webos|smart-tv|smarttv|bravia|viera|philips|roku|crkey/.test(txt)) {
    return "Smart TV";
  }
  if (/aft|fire tv|mi box|mibox|android tv|googletv/.test(txt)) return "TV Box / Android TV";
  if (/iphone|ipad|ipod/.test(txt)) return "iPhone / iPad";
  if (/android/.test(txt)) return "Celular Android";
  if (/windows/.test(txt)) return "Computador Windows";
  if (/macintosh|mac os/.test(txt)) return "Mac";
  if (/linux/.test(txt)) return "Linux";
  return "Navegador Web";
}

function validarAdmin(request, env, urlObj) {
  const esperada = (env && env.ADMIN_SENHA) ? String(env.ADMIN_SENHA) : "";
  const recebida =
    request.headers.get("X-Admin-Senha") ||
    urlObj.searchParams.get("senha") ||
    "";
  return recebida === esperada;
}

async function tratarPing(request, env, reqUrl) {
  if (!env || !env.DB) {
    return respostaJson({ ok: false, erro: "Banco D1 não configurado" }, 500);
  }

  let dados = {};
  if (request.method === "POST") {
    try {
      const txt = await request.text();
      if (txt) dados = JSON.parse(txt);
    } catch {
      dados = {};
    }
  } else {
    dados = {
      sessao_id: reqUrl.searchParams.get("sessao_id"),
      app: reqUrl.searchParams.get("app"),
      item_atual: reqUrl.searchParams.get("item_atual"),
      chave_cliente: reqUrl.searchParams.get("chave_cliente"),
    };
  }

  const sessaoId = String(dados.sessao_id || "").trim().slice(0, 80);
  if (!sessaoId) {
    return respostaJson({ ok: false, erro: "sessao_id obrigatório" }, 400);
  }

  const app = String(dados.app || "cinepro-tv").trim().slice(0, 40);
  const itemAtual = String(dados.item_atual || "Navegando").trim().slice(0, 120);
  const chaveBruta = String(dados.chave_cliente || "VISITANTE").trim().toUpperCase().slice(0, 40);
  const chaveCliente = chaveBruta || "VISITANTE";

  const ip =
    request.headers.get("CF-Connecting-IP") ||
    (request.headers.get("X-Forwarded-For") || "").split(",")[0].trim() ||
    "0.0.0.0";
  const cf = request.cf || {};
  const cidade = String(cf.city || "").slice(0, 60);
  const regiao = String(cf.regionCode || "").slice(0, 20);
  const pais = String(cf.country || "BR").slice(0, 10);
  const dispositivo = detectarDispositivo(request.headers.get("User-Agent"));
  const agora = Math.floor(Date.now() / 1000);

  const existente = await env.DB.prepare(
    "SELECT ultimo_sinal_em, segundos_totais FROM sessoes WHERE sessao_id = ?"
  )
    .bind(sessaoId)
    .first();

  let segundosTotais = 0;
  if (existente) {
    const ultimo = Number(existente.ultimo_sinal_em || agora);
    const delta = Math.min(Math.max(agora - ultimo, 0), 120);
    segundosTotais = Number(existente.segundos_totais || 0) + delta;

    await env.DB.prepare(
      `UPDATE sessoes
       SET chave_cliente = ?, app = ?, ip = ?, cidade = ?, regiao = ?, pais = ?,
           dispositivo = ?, item_atual = ?, ultimo_sinal_em = ?, segundos_totais = ?
       WHERE sessao_id = ?`
    )
      .bind(
        chaveCliente,
        app,
        ip,
        cidade,
        regiao,
        pais,
        dispositivo,
        itemAtual,
        agora,
        segundosTotais,
        sessaoId
      )
      .run();
  } else {
    await env.DB.prepare(
      `INSERT INTO sessoes (
         sessao_id, chave_cliente, app, ip, cidade, regiao, pais,
         dispositivo, item_atual, iniciado_em, ultimo_sinal_em, segundos_totais
       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)`
    )
      .bind(
        sessaoId,
        chaveCliente,
        app,
        ip,
        cidade,
        regiao,
        pais,
        dispositivo,
        itemAtual,
        agora,
        agora
      )
      .run();
  }

  // Checagem opcional de chave de cliente cadastrado (controle de telas/IPs, pagamento e prazo)
  let permitido = true;
  let motivo = "";
  let avisoPre = null;
  if (chaveCliente !== "VISITANTE") {
    const regChave = await env.DB.prepare(
      "SELECT chave, nome_cliente, max_ips, ativa, pagou, expira_em FROM chaves_clientes WHERE chave = ?"
    )
      .bind(chaveCliente)
      .first();

    if (regChave) {
      if (Number(regChave.ativa) === 0) {
        permitido = false;
        motivo = "Chave suspensa pelo administrador.";
      } else if (Number(regChave.expira_em) > 0 && agora > Number(regChave.expira_em)) {
        permitido = false;
        motivo = "Seu período de teste terminou! Chame o Jonas no WhatsApp para liberar seu acesso completo.";
      } else {
        if (Number(regChave.expira_em) > 0) {
          const restante = Number(regChave.expira_em) - agora;
          if (restante <= 7200) { // 2 horas (7200 segundos) até encerrar o teste
            avisoPre = {
              restante_seg: restante,
              motivo: "Atenção: seu tempo de teste termina em menos de 2 horas! Chame o Jonas no WhatsApp para não perder o sinal."
            };
          }
        }
        const limite = Number(regChave.max_ips || 2);
        const ativos = await env.DB.prepare(
          `SELECT DISTINCT ip FROM sessoes
           WHERE chave_cliente = ? AND ultimo_sinal_em >= ?`
        )
          .bind(chaveCliente, agora - 180)
          .all();
        const ipsAtivos = (ativos.results || []).map((r) => r.ip);
        if (ipsAtivos.length > limite && !ipsAtivos.slice(0, limite).includes(ip)) {
          permitido = false;
          motivo = `Limite de ${limite} IPs simultâneos atingido nesta chave.`;
        }
      }
    }
  }

  let msgAdmin = null;
  try {
    const regMsg = await env.DB.prepare(
      "SELECT id, texto, link_whatsapp FROM mensagens_admin WHERE ativa = 1 ORDER BY criado_em DESC LIMIT 1"
    ).first();
    if (regMsg) {
      msgAdmin = {
        id: regMsg.id,
        texto: regMsg.texto,
        link: regMsg.link_whatsapp || "https://wa.me/5511966707293"
      };
    }
  } catch (_) {}

  return respostaJson({
    ok: true,
    ip,
    cidade,
    pais,
    segundos_totais: segundosTotais,
    permitido,
    motivo,
    aviso_pre: avisoPre,
    mensagem_admin: msgAdmin,
  });
}

async function tratarMonitorApi(request, env, reqUrl) {
  if (!validarAdmin(request, env, reqUrl)) {
    return respostaJson({ ok: false, erro: "Senha de administrador incorreta." }, 401);
  }
  if (!env || !env.DB) {
    return respostaJson({ ok: false, erro: "Banco D1 não configurado." }, 500);
  }

  const agora = Math.floor(Date.now() / 1000);
  const limiteOnline = agora - 120; // Últimos 2 minutos = conectado agora
  const inicioDia = agora - 86400;  // Últimas 24 horas

  const [resumoOnline, resumoHoje, resumoTotal, resSessoes, resChaves, resTotalEnquetes, resEnquetes] = await Promise.all([
    env.DB.prepare("SELECT COUNT(*) AS qtd FROM sessoes WHERE ultimo_sinal_em >= ?")
      .bind(limiteOnline)
      .first(),
    env.DB.prepare("SELECT COUNT(DISTINCT ip) AS qtd FROM sessoes WHERE ultimo_sinal_em >= ?")
      .bind(inicioDia)
      .first(),
    env.DB.prepare("SELECT COUNT(*) AS qtd FROM sessoes").first(),
    env.DB.prepare(
      `SELECT s.sessao_id, s.chave_cliente, s.app, s.ip, s.cidade, s.regiao, s.pais,
              s.dispositivo, s.item_atual, s.iniciado_em, s.ultimo_sinal_em, s.segundos_totais,
              c.nome_cliente, c.pagou, c.expira_em, c.ativa
       FROM sessoes s
       LEFT JOIN chaves_clientes c ON s.chave_cliente = c.chave
       ORDER BY s.ultimo_sinal_em DESC
       LIMIT 120`
    ).all(),
    env.DB.prepare(
      `SELECT c.chave, c.nome_cliente, c.plano, c.max_ips, c.ativa, c.pagou, c.expira_em, c.criado_em,
              (SELECT COUNT(DISTINCT s.ip) FROM sessoes s
               WHERE s.chave_cliente = c.chave AND s.ultimo_sinal_em >= ?) AS ips_online,
              (SELECT COALESCE(SUM(s.segundos_totais), 0) FROM sessoes s
               WHERE s.chave_cliente = c.chave) AS segundos_acumulados
       FROM chaves_clientes c
       ORDER BY c.criado_em DESC`
    )
      .bind(limiteOnline)
      .all(),
    env.DB.prepare("SELECT COUNT(*) AS qtd FROM enquetes").first(),
    env.DB.prepare(
      `SELECT id, sessao_id, chave_cliente, app, ip, cidade, resposta, nota, comentario, respondido_em
       FROM enquetes
       ORDER BY respondido_em DESC
       LIMIT 50`
    ).all(),
  ]);

  const listaChaves = resChaves.results || [];
  let msgAdminAtiva = null;
  try {
    msgAdminAtiva = await env.DB.prepare(
      "SELECT id, texto, link_whatsapp, criado_em FROM mensagens_admin WHERE ativa = 1 ORDER BY criado_em DESC LIMIT 1"
    ).first();
  } catch (_) {}

  return respostaJson({
    ok: true,
    agora,
    resumo: {
      online_agora: Number(resumoOnline?.qtd || 0),
      ips_unicos_24h: Number(resumoHoje?.qtd || 0),
      total_sessoes: Number(resumoTotal?.qtd || 0),
      chaves_ativas: listaChaves.filter((c) => Number(c.ativa) === 1).length,
      pagos_ativos: listaChaves.filter((c) => Number(c.pagou) === 1).length,
      total_enquetes: Number(resTotalEnquetes?.qtd || 0),
    },
    sessoes: resSessoes.results || [],
    chaves: listaChaves,
    enquetes: resEnquetes.results || [],
    mensagem_ativa: msgAdminAtiva,
  });
}

async function tratarMensagemAdminApi(request, env, reqUrl) {
  if (!validarAdmin(request, env, reqUrl)) {
    return respostaJson({ ok: false, erro: "Senha de administrador incorreta." }, 401);
  }
  if (!env || !env.DB) {
    return respostaJson({ ok: false, erro: "Banco D1 não configurado." }, 500);
  }

  try {
    await env.DB.prepare(
      `CREATE TABLE IF NOT EXISTS mensagens_admin (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         texto TEXT NOT NULL,
         link_whatsapp TEXT NOT NULL DEFAULT 'https://wa.me/5511966707293',
         ativa INTEGER NOT NULL DEFAULT 1,
         criado_em INTEGER NOT NULL
       )`
    ).run();
  } catch (_) {}

  let body = {};
  try {
    body = await request.json();
  } catch {
    return respostaJson({ ok: false, erro: "JSON inválido." }, 400);
  }

  const acao = String(body.acao || "salvar");
  if (acao === "desativar") {
    await env.DB.prepare("UPDATE mensagens_admin SET ativa = 0").run();
    return respostaJson({ ok: true, mensagem: "Mensagem desativada das telas." });
  }

  const texto = String(body.texto || "").trim().slice(0, 300);
  const link = String(body.link || "https://wa.me/5511966707293").trim().slice(0, 200);

  if (!texto) {
    return respostaJson({ ok: false, erro: "O texto da mensagem é obrigatório." }, 400);
  }

  const agora = Math.floor(Date.now() / 1000);
  await env.DB.prepare("UPDATE mensagens_admin SET ativa = 0").run();
  await env.DB.prepare(
    "INSERT INTO mensagens_admin (texto, link_whatsapp, ativa, criado_em) VALUES (?, ?, 1, ?)"
  )
    .bind(texto, link, agora)
    .run();

  return respostaJson({ ok: true, mensagem: "Mensagem transmitida com sucesso para todas as telas!" });
}

async function tratarEnqueteApi(request, env) {
  if (!env || !env.DB) {
    return respostaJson({ ok: false, erro: "Banco D1 não configurado." }, 500);
  }
  let body = {};
  try {
    body = await request.json();
  } catch {
    return respostaJson({ ok: false, erro: "JSON inválido." }, 400);
  }

  const sessaoId = String(body.sessao_id || "").trim().slice(0, 80);
  const chaveCliente = String(body.chave_cliente || "VISITANTE").trim().toUpperCase().slice(0, 40);
  const app = String(body.app || "cinepro-tv").trim().slice(0, 40);
  const resposta = String(body.resposta || "").trim().slice(0, 200);
  const nota = Math.max(1, Math.min(5, parseInt(body.nota || "5", 10) || 5));
  const comentario = String(body.comentario || "").trim().slice(0, 500);

  if (!resposta) {
    return respostaJson({ ok: false, erro: "Resposta da enquete é obrigatória." }, 400);
  }

  const ip =
    request.headers.get("CF-Connecting-IP") ||
    (request.headers.get("X-Forwarded-For") || "").split(",")[0].trim() ||
    "0.0.0.0";
  const cf = request.cf || {};
  const cidade = String(cf.city || "").slice(0, 60);
  const agora = Math.floor(Date.now() / 1000);

  await env.DB.prepare(
    `INSERT INTO enquetes (sessao_id, chave_cliente, app, ip, cidade, resposta, nota, comentario, respondido_em)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(sessaoId, chaveCliente, app, ip, cidade, resposta, nota, comentario, agora)
    .run();

  return respostaJson({ ok: true, mensagem: "Enquete registrada com sucesso no banco de dados!" });
}

async function tratarChavesApi(request, env, reqUrl) {
  if (!validarAdmin(request, env, reqUrl)) {
    return respostaJson({ ok: false, erro: "Senha de administrador incorreta." }, 401);
  }
  let body = {};
  try {
    body = await request.json();
  } catch {
    return respostaJson({ ok: false, erro: "JSON inválido." }, 400);
  }

  const acao = String(body.acao || "salvar");
  if (acao === "limpar_antigas") {
    const limite = Math.floor(Date.now() / 1000) - 86400 * 7;
    await env.DB.prepare("DELETE FROM sessoes WHERE ultimo_sinal_em < ?").bind(limite).run();
    return respostaJson({ ok: true, mensagem: "Sessões com mais de 7 dias removidas." });
  }

  const chave = String(body.chave || "").trim().toUpperCase().replace(/[^A-Z0-9_-]/g, "").slice(0, 40);
  if (!chave) {
    return respostaJson({ ok: false, erro: "Informe um código de chave válido (ex: CLI001)." }, 400);
  }

  if (acao === "excluir") {
    await env.DB.prepare("DELETE FROM chaves_clientes WHERE chave = ?").bind(chave).run();
    return respostaJson({ ok: true, mensagem: `Chave ${chave} excluída.` });
  }

  if (acao === "alternar") {
    const atual = await env.DB.prepare("SELECT ativa FROM chaves_clientes WHERE chave = ?").bind(chave).first();
    const nova = atual && Number(atual.ativa) === 1 ? 0 : 1;
    await env.DB.prepare("UPDATE chaves_clientes SET ativa = ? WHERE chave = ?").bind(nova, chave).run();
    return respostaJson({ ok: true, ativa: nova });
  }

  if (acao === "alternar_pagamento") {
    const atual = await env.DB.prepare("SELECT pagou FROM chaves_clientes WHERE chave = ?").bind(chave).first();
    const novoPagou = atual && Number(atual.pagou) === 1 ? 0 : 1;
    await env.DB.prepare("UPDATE chaves_clientes SET pagou = ? WHERE chave = ?").bind(novoPagou, chave).run();
    return respostaJson({ ok: true, pagou: novoPagou });
  }

  if (acao === "renovar_7d") {
    const agoraRenov = Math.floor(Date.now() / 1000);
    const atual = await env.DB.prepare("SELECT expira_em FROM chaves_clientes WHERE chave = ?").bind(chave).first();
    const base = Math.max(agoraRenov, Number(atual?.expira_em || 0));
    const novoExp = base + 86400 * 7;
    await env.DB.prepare("UPDATE chaves_clientes SET expira_em = ?, ativa = 1 WHERE chave = ?")
      .bind(novoExp, chave)
      .run();
    return respostaJson({ ok: true, expira_em: novoExp });
  }

  if (acao === "renovar_15d") {
    const agoraRenov = Math.floor(Date.now() / 1000);
    const atual = await env.DB.prepare("SELECT expira_em FROM chaves_clientes WHERE chave = ?").bind(chave).first();
    const base = Math.max(agoraRenov, Number(atual?.expira_em || 0));
    const novoExp = base + 86400 * 15;
    await env.DB.prepare("UPDATE chaves_clientes SET expira_em = ?, ativa = 1 WHERE chave = ?")
      .bind(novoExp, chave)
      .run();
    return respostaJson({ ok: true, expira_em: novoExp });
  }

  if (acao === "renovar_30d") {
    const agoraRenov = Math.floor(Date.now() / 1000);
    const atual = await env.DB.prepare("SELECT expira_em FROM chaves_clientes WHERE chave = ?").bind(chave).first();
    const base = Math.max(agoraRenov, Number(atual?.expira_em || 0));
    const novoExp = base + 86400 * 30;
    await env.DB.prepare("UPDATE chaves_clientes SET expira_em = ?, ativa = 1 WHERE chave = ?")
      .bind(novoExp, chave)
      .run();
    return respostaJson({ ok: true, expira_em: novoExp });
  }

  const nome = String(body.nome_cliente || "Cliente").trim().slice(0, 80);
  const plano = String(body.plano || "TV e Rádio Casa R$ 30").trim().slice(0, 80);
  const maxIps = Math.max(1, Math.min(20, parseInt(body.max_ips || "2", 10) || 2));
  const pagou = Number(body.pagou) === 1 ? 1 : 0;
  const prazoHoras = Number(body.prazo_horas ?? 720);
  const agora = Math.floor(Date.now() / 1000);
  const expiraEm = prazoHoras > 0 ? agora + Math.round(prazoHoras * 3600) : 0;

  await env.DB.prepare(
    `INSERT INTO chaves_clientes (chave, nome_cliente, plano, max_ips, ativa, pagou, expira_em, criado_em)
     VALUES (?, ?, ?, ?, 1, ?, ?, ?)
     ON CONFLICT(chave) DO UPDATE SET
       nome_cliente = excluded.nome_cliente,
       plano = excluded.plano,
       max_ips = excluded.max_ips,
       pagou = excluded.pagou,
       expira_em = excluded.expira_em`
  )
    .bind(chave, nome, plano, maxIps, pagou, expiraEm, agora)
    .run();

  return respostaJson({ ok: true, chave, pagou, expira_em: expiraEm });
}

function renderizarPainelHtml() {
  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Jonas Digital • Painel ao Vivo (IP, Tempo e Pagamento)</title>
  <style>
    :root {
      --bg: #0c0e12;
      --card: #151922;
      --line: rgba(255,255,255,0.09);
      --ink: #f3f5f8;
      --muted: #98a3b6;
      --accent: #34d399;
      --accent-dark: #06281c;
      --warn: #f59e0b;
      --danger: #f87171;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--ink);
      font-family: system-ui, -apple-system, Segoe UI, sans-serif;
      line-height: 1.5;
      padding: 20px;
    }
    .wrap { max-width: 1240px; margin: 0 auto; }
    header {
      display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
      gap: 12px; padding-bottom: 18px; border-bottom: 1px solid var(--line); margin-bottom: 22px;
    }
    h1 { font-size: 20px; font-weight: 800; letter-spacing: -0.02em; }
    .sub { font-size: 12.5px; color: var(--muted); }
    .row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    input, select {
      background: #0f131a; color: var(--ink); border: 1px solid var(--line);
      border-radius: 8px; padding: 9px 12px; font-size: 13.5px;
    }
    button {
      border: none; border-radius: 8px; padding: 8px 12px; font-size: 12.5px;
      font-weight: 700; cursor: pointer; font-family: inherit;
    }
    .btn-main { background: var(--accent); color: var(--accent-dark); }
    .btn-sec { background: #1e2430; color: var(--ink); border: 1px solid var(--line); }
    .btn-danger { background: rgba(248,113,113,0.16); color: var(--danger); }
    .cards {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
      gap: 14px; margin-bottom: 24px;
    }
    .card {
      background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px;
    }
    .card-lbl { font-size: 12px; color: var(--muted); font-weight: 600; }
    .card-val { font-size: 28px; font-weight: 800; margin-top: 4px; font-variant-numeric: tabular-nums; }
    .panel {
      background: var(--card); border: 1px solid var(--line); border-radius: 12px;
      padding: 18px; margin-bottom: 22px; overflow-x: auto;
    }
    .panel-head {
      display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
      gap: 10px; margin-bottom: 14px;
    }
    table { width: 100%; border-collapse: collapse; font-size: 13px; min-width: 860px; }
    th {
      text-align: left; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.04em;
      color: var(--muted); padding: 10px 8px; border-bottom: 1px solid var(--line);
    }
    td { padding: 10px 8px; border-bottom: 1px solid var(--line); vertical-align: middle; }
    .pill {
      display: inline-flex; align-items: center; gap: 5px; padding: 3px 9px;
      border-radius: 99px; font-size: 11.5px; font-weight: 700; white-space: nowrap;
    }
    .pill-on { background: rgba(52,211,153,0.14); color: var(--accent); }
    .pill-off { background: rgba(152,163,182,0.14); color: var(--muted); }
    .pill-chave { background: rgba(245,158,11,0.14); color: var(--warn); }
    .pill-no { background: rgba(248,113,113,0.16); color: var(--danger); }
    .login-box {
      max-width: 390px; margin: 70px auto; background: var(--card); border: 1px solid var(--line);
      border-radius: 14px; padding: 26px; display: flex; flex-direction: column; gap: 12px;
    }
    .erro { color: var(--danger); font-size: 13px; min-height: 18px; }
    .hidden { display: none; }
    .mono { font-family: ui-monospace, Consolas, monospace; font-size: 12.5px; }
  </style>
</head>
<body>
  <div id="loginView" class="login-box">
    <h1>🔐 Painel Jonas Digital</h1>
    <p class="sub">Digite a senha de administrador para acompanhar IPs conectados, tempo de uso e quem pagou.</p>
    <input type="password" id="senhaInput" placeholder="Senha de administrador">
    <button class="btn-main" id="btnEntrar">Entrar no Painel</button>
    <div id="loginErro" class="erro"></div>
  </div>

  <div id="dashView" class="wrap hidden">
    <header>
      <div>
        <h1>📡 Painel ao Vivo — IP, Tempo &amp; Pagamento</h1>
        <p class="sub">Atualização automática a cada 15 segundos • Banco D1 gratuito</p>
      </div>
      <div class="row">
        <button class="btn-sec" id="btnFiltroOnline">Mostrar: Todos</button>
        <button class="btn-main" id="btnAtualizar">🔄 Atualizar Agora</button>
        <button class="btn-danger" id="btnLimpar">Limpar +7 dias</button>
        <button class="btn-sec" id="btnSair">Sair</button>
      </div>
    </header>

    <div class="cards">
      <div class="card"><div class="card-lbl">Conectados Agora (últimos 2 min)</div><div class="card-val" id="cOnline">0</div></div>
      <div class="card"><div class="card-lbl">IPs Únicos nas últimas 24h</div><div class="card-val" id="cIps">0</div></div>
      <div class="card"><div class="card-lbl">Sessões Registradas</div><div class="card-val" id="cSessoes">0</div></div>
      <div class="card"><div class="card-lbl">Chaves Ativas</div><div class="card-val" id="cChaves">0</div></div>
      <div class="card"><div class="card-lbl">Clientes Pagos</div><div class="card-val" id="cPagos">0</div></div>
      <div class="card"><div class="card-lbl">Enquetes Respondidas</div><div class="card-val" id="cEnquetes">0</div></div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h2>👥 Usuários Conectados &amp; Histórico Recente</h2>
        <span class="sub" id="statusAtualizacao">Carregando...</span>
      </div>
      <table>
        <thead>
          <tr>
            <th style="width:50px;"># Nº</th>
            <th>Estado</th>
            <th>IP &amp; Local</th>
            <th>Chave / Cliente</th>
            <th>Pagamento</th>
            <th>Sistema &amp; Canal/Rádio</th>
            <th>Aparelho</th>
            <th>Tempo Conectado &amp; Validade</th>
            <th>Último Sinal</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody id="tabelaSessoes"></tbody>
      </table>
    </div>

    <div class="panel" id="painelChavesSec">
      <div class="panel-head">
        <h2>🔑 Chaves de Acesso para Clientes (Controle de Pagamento, Prazo &amp; IPs)</h2>
      </div>
      <div class="row" style="margin-bottom:14px;background:rgba(255,255,255,0.02);padding:12px;border-radius:10px;border:1px solid var(--line);align-items:flex-end;">
        <div style="display:flex;flex-direction:column;gap:4px;">
          <label style="font-size:11px;color:var(--accent);font-weight:700;">⚡ Nº do IP (Lista acima):</label>
          <input type="number" id="numLinhaRapida" min="1" placeholder="Ex: 1" style="width:85px;border-color:rgba(52,211,153,0.4);" title="Digite o número da lista acima para puxar os dados na hora" oninput="puxarDadosPorNumero(this.value)">
        </div>
        <div style="display:flex;flex-direction:column;gap:4px;">
          <label style="font-size:11px;color:var(--muted);font-weight:700;">Código / Número da Chave:</label>
          <input type="text" id="novaChave" placeholder="Ex: 1 ou CLI01" style="width:140px;">
        </div>
        <div style="display:flex;flex-direction:column;gap:4px;">
          <label style="font-size:11px;color:var(--muted);font-weight:700;">Nome do Cliente:</label>
          <input type="text" id="novoNome" placeholder="Nome do cliente (ex: Marcos)" style="min-width:180px;">
        </div>
        <div style="display:flex;flex-direction:column;gap:4px;">
          <label style="font-size:11px;color:var(--muted);font-weight:700;">Plano:</label>
          <input type="text" id="novoPlano" value="TV e Rádio Casa R$ 30" placeholder="Plano" style="width:160px;">
        </div>
        <div style="display:flex;flex-direction:column;gap:4px;">
          <label style="font-size:11px;color:var(--muted);font-weight:700;">Pagamento:</label>
          <select id="novoPagou" title="Situação de pagamento">
            <option value="1">✅ Já Pagou</option>
            <option value="0">❌ Não Pagou / Em Teste</option>
          </select>
        </div>
        <div style="display:flex;flex-direction:column;gap:4px;">
          <label style="font-size:11px;color:var(--muted);font-weight:700;">Validade:</label>
          <select id="novoPrazo" title="Tempo de validade da chave">
            <option value="168" selected>📅 Teste 7 Dias</option>
            <option value="360">📅 Teste 15 Dias</option>
            <option value="720">📅 30 Dias (Mensal)</option>
            <option value="2">⏱️ Teste 2 Horas</option>
            <option value="24">⏱️ Teste 24 Horas</option>
            <option value="0">♾️ Vitalício (Sem vencimento)</option>
          </select>
        </div>
        <div style="display:flex;flex-direction:column;gap:4px;">
          <label style="font-size:11px;color:var(--muted);font-weight:700;">Limite IPs:</label>
          <input type="number" id="novoMaxIps" value="2" min="1" max="20" style="width:75px;" title="Limite de IPs simultâneos">
        </div>
        <button class="btn-main" id="btnCriarChave" style="height:38px;">+ Salvar Cadastro</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Chave</th>
            <th>Cliente &amp; Plano</th>
            <th>Pagou?</th>
            <th>IPs Agora / Limite</th>
            <th>Tempo Usado &amp; Validade</th>
            <th>Situação</th>
            <th>Links Prontos e Ações</th>
          </tr>
        </thead>
        <tbody id="tabelaChaves"></tbody>
      </table>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h2>📢 Transmitir Mensagem na Tela de Quem Está Assistindo</h2>
      </div>
      <div style="padding:16px 20px;">
        <p class="sub" style="margin-bottom:12px;">Essa mensagem surge como uma notificação elegante na tela de todos os visitantes e clientes que estão com o player aberto.</p>
        <div id="statusMsgAtiva" style="margin-bottom:12px;padding:10px 14px;border-radius:8px;background:#151922;border:1px solid rgba(255,255,255,0.08);font-size:13px;">
          Carregando status...
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
          <input type="text" id="inputMsgAdmin" placeholder="Ex: Olá! Como está sua transmissão? Quer ajuda ou liberar mais canais? Fale comigo no WhatsApp!" style="flex:1;min-width:280px;background:#0c0e12;border:1px solid rgba(255,255,255,0.15);color:#fff;padding:10px 14px;border-radius:8px;font-size:13px;">
          <button class="btn" id="btnEnviarMsgAdmin" style="background:#34d399;color:#06281c;font-weight:700;">🚀 Enviar para as Telas</button>
          <button class="btn-danger" id="btnDesativarMsgAdmin">✕ Apagar / Desativar</button>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <h2>📊 Respostas da Enquete ("Gostou do Aplicativo?")</h2>
      </div>
      <table>
        <thead>
          <tr>
            <th>Data &amp; Hora</th>
            <th>IP &amp; Local</th>
            <th>Chave / Cliente</th>
            <th>Sistema</th>
            <th>Avaliação / Resposta</th>
            <th>Nota</th>
          </tr>
        </thead>
        <tbody id="tabelaEnquetes"></tbody>
      </table>
    </div>
  </div>

  <script>
    let senhaAtual = sessionStorage.getItem('jonas_admin_senha') || '';
    let apenasOnline = false;
    let timerAuto = null;
    let ultimasSessoes = [];

    function preencherCadastroPeloNumero(num) {
      num = parseInt(num, 10);
      if (!num || !ultimasSessoes || !ultimasSessoes[num - 1]) return;
      const s = ultimasSessoes[num - 1];
      const codSugerido = s.chave_cliente !== 'VISITANTE' ? s.chave_cliente : ('CLI' + String(num).padStart(2, '0'));
      const campoNum = document.getElementById('numLinhaRapida');
      if (campoNum) campoNum.value = num;
      document.getElementById('novaChave').value = codSugerido;
      const loc = [s.cidade, s.regiao].filter(Boolean).join(' - ');
      const disp = s.dispositivo ? ' • ' + s.dispositivo : '';
      document.getElementById('novoNome').value = s.nome_cliente || ('Cliente #' + num + (loc ? ' (' + loc + disp + ')' : disp));
      
      const el = document.getElementById('novaChave');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.focus();
      }
    }

    function puxarDadosPorNumero(val) {
      const num = parseInt(val, 10);
      if (!num || isNaN(num)) return;
      if (!ultimasSessoes || !ultimasSessoes[num - 1]) return;
      preencherCadastroPeloNumero(num);
    }

    function fmtDuracao(seg) {
      const s = Math.max(0, Number(seg || 0));
      const h = Math.floor(s / 3600);
      const m = Math.floor((s % 3600) / 60);
      const r = s % 60;
      if (h > 0) return h + 'h ' + String(m).padStart(2, '0') + 'm';
      if (m > 0) return m + 'm ' + String(r).padStart(2, '0') + 's';
      return r + 's';
    }

    function fmtRelativo(agora, ts) {
      const diff = Math.max(0, agora - Number(ts || agora));
      if (diff <= 15) return 'agora mesmo';
      if (diff < 60) return 'há ' + diff + 's';
      if (diff < 3600) return 'há ' + Math.floor(diff / 60) + ' min';
      if (diff < 86400) return 'há ' + Math.floor(diff / 3600) + 'h';
      return 'há ' + Math.floor(diff / 86400) + 'd';
    }

    function fmtPrazo(agora, expiraEm, chave) {
      if (chave === 'VISITANTE') return 'Demo livre';
      const exp = Number(expiraEm || 0);
      if (!exp) return '♾️ Vitalício';
      const diff = exp - agora;
      if (diff <= 0) return '⚠️ Vencido';
      if (diff < 3600) return 'Vence em ' + Math.ceil(diff / 60) + ' min';
      if (diff < 86400) return 'Vence em ' + Math.ceil(diff / 3600) + 'h';
      return 'Vence em ' + Math.ceil(diff / 86400) + ' dias';
    }

    function esc(txt) {
      return String(txt || '').replace(/[&<>"']/g, function(c) {
        return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
      });
    }

    async function carregarPainel() {
      const resp = await fetch('/api/monitor', {
        headers: { 'X-Admin-Senha': senhaAtual }
      });
      if (resp.status === 401) {
        sessionStorage.removeItem('jonas_admin_senha');
        document.getElementById('dashView').classList.add('hidden');
        document.getElementById('loginView').classList.remove('hidden');
        document.getElementById('loginErro').textContent = 'Senha incorreta.';
        return false;
      }
      const data = await resp.json();
      document.getElementById('loginView').classList.add('hidden');
      document.getElementById('dashView').classList.remove('hidden');
      document.getElementById('cOnline').textContent = data.resumo.online_agora;
      document.getElementById('cIps').textContent = data.resumo.ips_unicos_24h;
      document.getElementById('cSessoes').textContent = data.resumo.total_sessoes;
      document.getElementById('cChaves').textContent = data.resumo.chaves_ativas;
      document.getElementById('cPagos').textContent = data.resumo.pagos_ativos || 0;
      document.getElementById('cEnquetes').textContent = data.resumo.total_enquetes || 0;

      const agora = data.agora;
      const lista = (data.sessoes || []).filter(function(s) {
        return !apenasOnline || (agora - Number(s.ultimo_sinal_em)) <= 120;
      });

      ultimasSessoes = lista;
      const tbody = document.getElementById('tabelaSessoes');
      if (!lista.length) {
        tbody.innerHTML = '<tr><td colspan="10" class="sub">Nenhuma conexão registrada ainda.</td></tr>';
      } else {
        tbody.innerHTML = lista.map(function(s, idx) {
          const num = idx + 1;
          const numBadge = '<span class="pill" style="background:#1e293b;color:#34d399;font-weight:900;border:1px solid rgba(52,211,153,0.3);min-width:32px;justify-content:center;">#' + num + '</span>';
          const online = (agora - Number(s.ultimo_sinal_em)) <= 120;
          const badge = online
            ? '<span class="pill pill-on">🟢 Ao vivo</span>'
            : '<span class="pill pill-off">⚪ Saiu</span>';
          const local = [s.cidade, s.regiao, s.pais].filter(Boolean).join(', ');
          const appNome = s.app === 'radiopro' ? '📻 RádioPro' : '📺 CinePro TV';
          const pago = s.chave_cliente !== 'VISITANTE' && Number(s.pagou) === 1;
          const badgePagou = pago
            ? '<span class="pill pill-on">✅ PAGO</span>'
            : '<span class="pill pill-no">❌ NÃO PAGOU</span>';
          const subNome = s.nome_cliente ? '<div class="sub">' + esc(s.nome_cliente) + '</div>' : '';
          const btnCadastrarRapido = '<button class="btn-main" style="padding:4px 9px;font-size:11.5px;white-space:nowrap;" onclick="preencherCadastroPeloNumero(' + num + ')" title="Puxar dados do IP #' + num + ' para o cadastro">+ Cadastrar #' + num + '</button>';
          return '<tr>'
            + '<td>' + numBadge + '</td>'
            + '<td>' + badge + '</td>'
            + '<td><div class="mono">' + esc(s.ip) + '</div><div class="sub">' + esc(local) + '</div></td>'
            + '<td><span class="pill pill-chave">' + esc(s.chave_cliente) + '</span>' + subNome + '</td>'
            + '<td>' + badgePagou + '</td>'
            + '<td><div><strong>' + appNome + '</strong></div><div class="sub">' + esc(s.item_atual) + '</div></td>'
            + '<td>' + esc(s.dispositivo) + '</td>'
            + '<td><div><strong>' + fmtDuracao(s.segundos_totais) + '</strong></div><div class="sub">' + fmtPrazo(agora, s.expira_em, s.chave_cliente) + '</div></td>'
            + '<td class="sub">' + fmtRelativo(agora, s.ultimo_sinal_em) + '</td>'
            + '<td>' + btnCadastrarRapido + '</td>'
            + '</tr>';
        }).join('');
      }

      const tbChaves = document.getElementById('tabelaChaves');
      const chaves = data.chaves || [];
      if (!chaves.length) {
        tbChaves.innerHTML = '<tr><td colspan="7" class="sub">Nenhuma chave criada ainda (o acesso público segue livre).</td></tr>';
      } else {
        tbChaves.innerHTML = chaves.map(function(c) {
          const ativa = Number(c.ativa) === 1;
          const pago = Number(c.pagou) === 1;
          const vencido = Number(c.expira_em || 0) > 0 && agora > Number(c.expira_em);
          const st = !ativa
            ? '<span class="pill pill-off">Bloqueada</span>'
            : (vencido ? '<span class="pill pill-no">Vencida</span>' : '<span class="pill pill-on">Ativa</span>');
          const seloPago = pago
            ? '<span class="pill pill-on">✅ PAGO</span>'
            : '<span class="pill pill-no">❌ NÃO PAGOU</span>';
          const cEsc = esc(c.chave);
          return '<tr>'
            + '<td class="mono"><strong>' + cEsc + '</strong></td>'
            + '<td><div><strong>' + esc(c.nome_cliente) + '</strong></div><div class="sub">' + esc(c.plano) + '</div></td>'
            + '<td>' + seloPago + '</td>'
            + '<td>' + Number(c.ips_online || 0) + ' / ' + Number(c.max_ips || 2) + ' IPs</td>'
            + '<td><div><strong>' + fmtDuracao(c.segundos_acumulados) + '</strong></div><div class="sub">' + fmtPrazo(agora, c.expira_em, c.chave) + '</div></td>'
            + '<td>' + st + '</td>'
            + '<td class="row">'
            + '<button class="btn-sec" onclick="copiarLink(\\'' + cEsc + '\\', \\'tv\\')">📺 Link TV</button>'
            + '<button class="btn-sec" onclick="copiarLink(\\'' + cEsc + '\\', \\'radio\\')">📻 Link Rádio</button>'
            + '<button class="btn-sec" onclick="acaoChave(\\'alternar_pagamento\\', \\'' + cEsc + '\\')">💳 Pago/Não</button>'
            + '<button class="btn-sec" onclick="acaoChave(\\'renovar_7d\\', \\'' + cEsc + '\\')">+7d</button>'
            + '<button class="btn-sec" onclick="acaoChave(\\'renovar_15d\\', \\'' + cEsc + '\\')">+15d</button>'
            + '<button class="btn-sec" onclick="acaoChave(\\'renovar_30d\\', \\'' + cEsc + '\\')">+30d</button>'
            + '<button class="btn-sec" onclick="acaoChave(\\'alternar\\', \\'' + cEsc + '\\')">' + (ativa ? 'Bloquear' : 'Ativar') + '</button>'
            + '<button class="btn-danger" onclick="acaoChave(\\'excluir\\', \\'' + cEsc + '\\')">Excluir</button>'
            + '</td></tr>';
        }).join('');
      }

      const tbEnquetes = document.getElementById('tabelaEnquetes');
      const enquetes = data.enquetes || [];
      if (!enquetes.length) {
        tbEnquetes.innerHTML = '<tr><td colspan="6" class="sub">Nenhuma resposta de enquete registrada ainda.</td></tr>';
      } else {
        tbEnquetes.innerHTML = enquetes.map(function(e) {
          const estrelas = '⭐'.repeat(Math.max(1, Math.min(5, Number(e.nota || 5))));
          const dataHora = new Date(Number(e.respondido_em) * 1000).toLocaleString('pt-BR');
          const local = [e.cidade, 'BR'].filter(Boolean).join(', ');
          const appNome = e.app === 'radiopro' ? '📻 RádioPro' : '📺 CinePro TV';
          return '<tr>'
            + '<td class="sub">' + esc(dataHora) + '</td>'
            + '<td><div class="mono">' + esc(e.ip) + '</div><div class="sub">' + esc(local) + '</div></td>'
            + '<td><span class="pill pill-chave">' + esc(e.chave_cliente) + '</span></td>'
            + '<td><strong>' + appNome + '</strong></td>'
            + '<td><div><strong>' + esc(e.resposta) + '</strong></div>' + (e.comentario ? '<div class="sub">' + esc(e.comentario) + '</div>' : '') + '</td>'
            + '<td><span title="' + e.nota + '/5">' + estrelas + '</span></td>'
            + '</tr>';
        }).join('');
      }

      const boxMsg = document.getElementById('statusMsgAtiva');
      if (boxMsg) {
        if (data.mensagem_ativa && data.mensagem_ativa.texto) {
          boxMsg.innerHTML = '<span style="color:#34d399;font-weight:700;">🟢 Mensagem ativa na tela agora:</span> "' + esc(data.mensagem_ativa.texto) + '"';
        } else {
          boxMsg.innerHTML = '<span style="color:#94a3b8;">⚪ Nenhuma mensagem ativa nas telas no momento.</span>';
        }
      }

      document.getElementById('statusAtualizacao').textContent = 'Última leitura: ' + new Date().toLocaleTimeString('pt-BR');
      return true;
    }

    function copiarLink(chave, tipo) {
      const base = tipo === 'radio'
        ? 'https://jonasskynet-eng.github.io/central-radios-pro/'
        : 'https://jonasskynet-eng.github.io/cine-pro-tv-2026/';
      const url = base + '?chave=' + encodeURIComponent(chave);
      navigator.clipboard.writeText(url).then(function() {
        alert('Link copiado para enviar ao cliente:\\n' + url);
      });
    }

    async function acaoChave(acao, chave) {
      await fetch('/api/chaves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Admin-Senha': senhaAtual },
        body: JSON.stringify({ acao: acao, chave: chave })
      });
      carregarPainel();
    }

    document.getElementById('btnEntrar').onclick = async function() {
      senhaAtual = document.getElementById('senhaInput').value.trim();
      document.getElementById('loginErro').textContent = '';
      const ok = await carregarPainel();
      if (ok) {
        sessionStorage.setItem('jonas_admin_senha', senhaAtual);
        if (!timerAuto) timerAuto = setInterval(carregarPainel, 15000);
      }
    };
    document.getElementById('btnAtualizar').onclick = carregarPainel;
    document.getElementById('btnFiltroOnline').onclick = function() {
      apenasOnline = !apenasOnline;
      this.textContent = apenasOnline ? 'Mostrar: Só Ao Vivo' : 'Mostrar: Todos';
      carregarPainel();
    };
    document.getElementById('btnLimpar').onclick = async function() {
      await fetch('/api/chaves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Admin-Senha': senhaAtual },
        body: JSON.stringify({ acao: 'limpar_antigas' })
      });
      carregarPainel();
    };
    document.getElementById('btnCriarChave').onclick = async function() {
      const chave = document.getElementById('novaChave').value.trim();
      const nome_cliente = document.getElementById('novoNome').value.trim();
      const plano = document.getElementById('novoPlano').value.trim();
      const pagou = document.getElementById('novoPagou').value;
      const prazo_horas = document.getElementById('novoPrazo').value;
      const max_ips = document.getElementById('novoMaxIps').value;
      if (!chave) { alert('Digite um código para a chave.'); return; }
      await fetch('/api/chaves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Admin-Senha': senhaAtual },
        body: JSON.stringify({
          acao: 'salvar',
          chave: chave,
          nome_cliente: nome_cliente || 'Cliente',
          plano: plano,
          pagou: Number(pagou),
          prazo_horas: Number(prazo_horas),
          max_ips: max_ips
        })
      });
      document.getElementById('novaChave').value = '';
      document.getElementById('novoNome').value = '';
      const numLinha = document.getElementById('numLinhaRapida');
      if (numLinha) numLinha.value = '';
      carregarPainel();
    };
    document.getElementById('btnEnviarMsgAdmin').onclick = async function() {
      const texto = document.getElementById('inputMsgAdmin').value.trim();
      if (!texto) { alert('Digite uma mensagem para transmitir.'); return; }
      const resp = await fetch('/api/mensagem_admin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Admin-Senha': senhaAtual },
        body: JSON.stringify({ texto: texto })
      });
      const data = await resp.json();
      if (data.ok) {
        alert(data.mensagem || 'Mensagem transmitida!');
        document.getElementById('inputMsgAdmin').value = '';
        carregarPainel();
      } else {
        alert('Erro: ' + (data.erro || 'Falha ao enviar'));
      }
    };
    document.getElementById('btnDesativarMsgAdmin').onclick = async function() {
      const resp = await fetch('/api/mensagem_admin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Admin-Senha': senhaAtual },
        body: JSON.stringify({ acao: 'desativar' })
      });
      const data = await resp.json();
      if (data.ok) {
        alert(data.mensagem || 'Mensagem desativada!');
        carregarPainel();
      }
    };
    document.getElementById('btnSair').onclick = function() {
      sessionStorage.removeItem('jonas_admin_senha');
      location.reload();
    };

    if (senhaAtual) {
      carregarPainel().then(function(ok) {
        if (ok) timerAuto = setInterval(carregarPainel, 15000);
      });
    }
  </script>
</body>
</html>`;
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return respostaCors(null, 204);
    }

    const reqUrl = new URL(request.url);
    const path = reqUrl.pathname;

    try {
      if (path === "/ping") {
        return await tratarPing(request, env, reqUrl);
      }
      if (path === "/painel") {
        return new Response(renderizarPainelHtml(), {
          status: 200,
          headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
        });
      }
      if (path === "/api/monitor") {
        return await tratarMonitorApi(request, env, reqUrl);
      }
      if (path === "/api/chaves" && request.method === "POST") {
        return await tratarChavesApi(request, env, reqUrl);
      }
      if (path === "/api/enquete" && request.method === "POST") {
        return await tratarEnqueteApi(request, env);
      }
      if (path === "/api/mensagem_admin" && request.method === "POST") {
        return await tratarMensagemAdminApi(request, env, reqUrl);
      }

      const targetUrl = reqUrl.searchParams.get("url");

      // Verificação de saúde rápida usada pelo CinePro TV para detectar a ponte ativa
      if (!targetUrl) {
        return respostaJson({
          ok: true,
          servico: "CinePro TV Ponte Nuvem + Telemetria",
          versao: "2.0",
          painel: `${reqUrl.origin}/painel`,
        });
      }

      let parsedTarget;
      try {
        parsedTarget = new URL(targetUrl);
      } catch {
        return respostaCors("URL inválida", 400);
      }

      if (
        (parsedTarget.protocol !== "http:" && parsedTarget.protocol !== "https:") ||
        ehHostPrivado(parsedTarget.hostname)
      ) {
        return respostaCors("Protocolo ou destino não permitido", 403);
      }

      const upstreamHeaders = obterHeadersOrigem(targetUrl);
      const rangeHeader = request.headers.get("Range");
      if (rangeHeader) {
        upstreamHeaders.Range = rangeHeader;
      }

      const upstreamResp = await fetch(targetUrl, {
        method: request.method === "HEAD" ? "HEAD" : "GET",
        headers: upstreamHeaders,
        redirect: "follow",
      });

      const finalUrl = upstreamResp.url || targetUrl;
      const contentType = upstreamResp.headers.get("Content-Type") || "application/octet-stream";
      const ehM3u8 =
        contentType.toLowerCase().includes("mpegurl") ||
        finalUrl.toLowerCase().includes(".m3u8") ||
        targetUrl.toLowerCase().includes(".m3u8");

      if (ehM3u8 && request.method !== "HEAD") {
        const texto = await upstreamResp.text();
        if (texto.includes("#EXTM3U")) {
          const workerProxyBase = `${reqUrl.origin}/`;
          const linhas = texto.split(/\r?\n/).map((linha) => {
            const limpa = linha.trim();
            if (!limpa) return linha;
            if (limpa.startsWith("#") && limpa.includes('URI="')) {
              return limpa.replace(/URI="([^"]+)"/g, (_, uri) => {
                return `URI="${reescreverUrl(uri, finalUrl, workerProxyBase)}"`;
              });
            }
            if (!limpa.startsWith("#")) {
              return reescreverUrl(limpa, finalUrl, workerProxyBase);
            }
            return limpa;
          });

          return respostaCors(linhas.join("\n"), 200, {
            "Content-Type": "application/vnd.apple.mpegurl; charset=utf-8",
          });
        }
        return respostaCors(texto, upstreamResp.status, {
          "Content-Type": contentType,
        });
      }

      const outHeaders = new Headers(CORS_HEADERS);
      outHeaders.set("Content-Type", contentType);
      const acceptRanges = upstreamResp.headers.get("Accept-Ranges");
      const contentRange = upstreamResp.headers.get("Content-Range");
      const contentLength = upstreamResp.headers.get("Content-Length");
      if (acceptRanges) outHeaders.set("Accept-Ranges", acceptRanges);
      if (contentRange) outHeaders.set("Content-Range", contentRange);
      if (contentLength) outHeaders.set("Content-Length", contentLength);

      return new Response(upstreamResp.body, {
        status: upstreamResp.status,
        headers: outHeaders,
      });
    } catch (err) {
      return respostaCors(`Erro na ponte: ${err.message}`, 502);
    }
  },
};
