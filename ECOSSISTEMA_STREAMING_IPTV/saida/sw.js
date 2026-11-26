const CACHE_NAME = 'cinepro-tv-v2026-perf2';
const APP_SHELL = [
    './',
    './index.html',
    './controle.html',
    './manifest.json',
    './cinepro-icon.svg'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(APP_SHELL).catch(() => {}))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
            )
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;
    const url = event.request.url;

    // Nunca interceptar streams ao vivo, chaves AES, APIs ou chamadas de proxy
    if (
        url.includes('/proxy') ||
        url.includes('/api/') ||
        url.includes('/healthz') ||
        url.includes('workers.dev') ||
        /\.(m3u8|ts|mp4|aac|mp3|ogg|key)(\?|$)/i.test(url)
    ) {
        return;
    }

    // Network-First para catalogos dinamicos (canais.json e epg_br.json)
    if (url.includes('canais.json') || url.includes('epg_br.json')) {
        event.respondWith(
            fetch(event.request)
                .then((resp) => {
                    if (resp && resp.ok) {
                        const clone = resp.clone();
                        caches.open(CACHE_NAME).then((c) => c.put(event.request, clone)).catch(() => {});
                    }
                    return resp;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // Stale-While-Revalidate para shell e bibliotecas HLS/MPEG-TS
    const mesmoOrigem = url.startsWith(self.location.origin);
    const ehPlayerLib = url.includes('cdn.jsdelivr.net/npm/hls.js') || url.includes('cdn.jsdelivr.net/npm/mpegts.js');
    if (mesmoOrigem || ehPlayerLib) {
        event.respondWith(
            caches.match(event.request).then((cached) => {
                const netFetch = fetch(event.request)
                    .then((resp) => {
                        if (resp && resp.ok) {
                            const clone = resp.clone();
                            caches.open(CACHE_NAME).then((c) => c.put(event.request, clone)).catch(() => {});
                        }
                        return resp;
                    })
                    .catch(() => cached);
                return cached || netFetch;
            })
        );
    }
});
