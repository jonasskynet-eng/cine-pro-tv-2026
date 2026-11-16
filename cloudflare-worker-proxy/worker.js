/**
 * CinePro TV — Ponte Gratuita na Nuvem (Cloudflare Workers)
 * Libera canais HTTP (ex.: 170.83.16.50 Discovery) e streams com restrição de origem (ex.: Pluto TV / jmp2.uk)
 * para rodar direto em HTTPS no GitHub Pages e celulares.
 */

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
  "Access-Control-Allow-Headers": "*",
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

export default {
  async fetch(request) {
    if (request.method === "OPTIONS") {
      return respostaCors(null, 204);
    }

    const reqUrl = new URL(request.url);
    const targetUrl = reqUrl.searchParams.get("url");

    // Verificação de saúde rápida usada pelo CinePro TV para detectar a ponte ativa
    if (!targetUrl) {
      return respostaCors(
        JSON.stringify({
          ok: true,
          servico: "CinePro TV Ponte Nuvem",
          versao: "1.0",
        }),
        200,
        { "Content-Type": "application/json; charset=utf-8" }
      );
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

    try {
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

      // Segmentos de vídeo/áudio/chave: repassar fluxo direto sem estourar memória
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
