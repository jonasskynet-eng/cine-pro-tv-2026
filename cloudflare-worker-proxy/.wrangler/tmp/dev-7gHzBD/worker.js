var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker.js
var CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
  "Access-Control-Allow-Headers": "*",
  "Access-Control-Expose-Headers": "*"
};
function respostaCors(body, status = 200, extraHeaders = {}) {
  return new Response(body, {
    status,
    headers: {
      ...CORS_HEADERS,
      "Cache-Control": "no-store",
      ...extraHeaders
    }
  });
}
__name(respostaCors, "respostaCors");
function ehHostPrivado(hostname) {
  const h = (hostname || "").toLowerCase();
  if (!h) return true;
  if (h === "localhost" || h.endsWith(".local")) return true;
  if (/^(127\.|10\.|192\.168\.|169\.254\.|0\.)/.test(h)) return true;
  const m172 = h.match(/^172\.(\d+)\./);
  if (m172 && Number(m172[1]) >= 16 && Number(m172[1]) <= 31) return true;
  return false;
}
__name(ehHostPrivado, "ehHostPrivado");
function obterHeadersOrigem(targetUrl) {
  const parsed = new URL(targetUrl);
  const lower = targetUrl.toLowerCase();
  const headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    Accept: "*/*",
    Referer: `${parsed.origin}/`,
    Origin: parsed.origin
  };
  if (lower.includes("pluto.tv") || lower.includes("plutotv.net") || lower.includes("jmp2.uk")) {
    headers.Origin = "https://pluto.tv";
    headers.Referer = "https://pluto.tv/";
  }
  return headers;
}
__name(obterHeadersOrigem, "obterHeadersOrigem");
function reescreverUrl(link, baseUrl, workerProxyBase) {
  try {
    const abs = new URL(link, baseUrl).toString();
    return `${workerProxyBase}?url=${encodeURIComponent(abs)}`;
  } catch {
    return link;
  }
}
__name(reescreverUrl, "reescreverUrl");
var worker_default = {
  async fetch(request) {
    if (request.method === "OPTIONS") {
      return respostaCors(null, 204);
    }
    const reqUrl = new URL(request.url);
    const targetUrl = reqUrl.searchParams.get("url");
    if (!targetUrl) {
      return respostaCors(
        JSON.stringify({
          ok: true,
          servico: "CinePro TV Ponte Nuvem",
          versao: "1.0"
        }),
        200,
        { "Content-Type": "application/json; charset=utf-8" }
      );
    }
    let parsedTarget;
    try {
      parsedTarget = new URL(targetUrl);
    } catch {
      return respostaCors("URL inv\xE1lida", 400);
    }
    if (parsedTarget.protocol !== "http:" && parsedTarget.protocol !== "https:" || ehHostPrivado(parsedTarget.hostname)) {
      return respostaCors("Protocolo ou destino n\xE3o permitido", 403);
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
        redirect: "follow"
      });
      const finalUrl = upstreamResp.url || targetUrl;
      const contentType = upstreamResp.headers.get("Content-Type") || "application/octet-stream";
      const ehM3u8 = contentType.toLowerCase().includes("mpegurl") || finalUrl.toLowerCase().includes(".m3u8") || targetUrl.toLowerCase().includes(".m3u8");
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
            "Content-Type": "application/vnd.apple.mpegurl; charset=utf-8"
          });
        }
        return respostaCors(texto, upstreamResp.status, {
          "Content-Type": contentType
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
        headers: outHeaders
      });
    } catch (err) {
      return respostaCors(`Erro na ponte: ${err.message}`, 502);
    }
  }
};

// ../../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// ../../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    const body = JSON.stringify(error);
    const headers = {
      "Content-Type": "application/json",
      "MF-Experimental-Error-Stack": "true"
    };
    const encoded = encodeURIComponent(body);
    if (encoded.length <= 8192) {
      headers["MF-Experimental-Error-Stack-Payload"] = encoded;
    }
    return new Response(body, { status: 500, headers });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-Ywbh1c/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = worker_default;

// ../../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-Ywbh1c/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class ___Facade_ScheduledController__ {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  scheduledTime;
  cron;
  static {
    __name(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=worker.js.map
