const https = require('https');
const http = require('http');
const urllib = require('url');

exports.handler = async function(event, context) {
    const targetUrl = event.queryStringParameters && event.queryStringParameters.url;
    if (!targetUrl) {
        return { statusCode: 400, body: 'Missing url parameter' };
    }

    try {
        const parsed = urllib.parse(targetUrl);
        const client = parsed.protocol === 'https:' ? https : http;

        return new Promise((resolve) => {
            const req = client.get(targetUrl, {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout: 10000
            }, (res) => {
                // Se for redirect
                if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                    let nextUrl = res.headers.location;
                    if (!nextUrl.startsWith('http')) {
                        nextUrl = urllib.resolve(targetUrl, nextUrl);
                    }
                    // Redireciona via proxy
                    return resolve({
                        statusCode: 302,
                        headers: {
                            'Location': `/.netlify/functions/proxy?url=${encodeURIComponent(nextUrl)}`,
                            'Access-Control-Allow-Origin': '*'
                        }
                    });
                }

                const contentType = res.headers['content-type'] || 'application/vnd.apple.mpegurl';
                const chunks = [];

                res.on('data', chunk => chunks.push(chunk));
                res.on('end', () => {
                    const buffer = Buffer.concat(chunks);
                    const isM3U8 = contentType.includes('mpegurl') || targetUrl.includes('.m3u8');

                    if (isM3U8) {
                        let text = buffer.toString('utf-8');
                        const baseUrl = targetUrl.substring(0, targetUrl.lastIndexOf('/') + 1);

                        const lines = text.split('\n').map(line => {
                            const trimmed = line.trim();
                            if (!trimmed) return line;

                            if (trimmed.startsWith('#') && trimmed.includes('URI="')) {
                                return trimmed.replace(/URI="([^"]+)"/g, (match, uri) => {
                                    const abs = uri.startsWith('http') ? uri : urllib.resolve(baseUrl, uri);
                                    return `URI="/.netlify/functions/proxy?url=${encodeURIComponent(abs)}"`;
                                });
                            } else if (!trimmed.startsWith('#')) {
                                const abs = trimmed.startsWith('http') ? trimmed : urllib.resolve(baseUrl, trimmed);
                                return `/.netlify/functions/proxy?url=${encodeURIComponent(abs)}`;
                            }
                            return line;
                        });

                        return resolve({
                            statusCode: 200,
                            headers: {
                                'Content-Type': 'application/vnd.apple.mpegurl',
                                'Access-Control-Allow-Origin': '*'
                            },
                            body: lines.join('\n')
                        });
                    }

                    // Se for segmento de vídeo (ts, m4s, key, mp4)
                    return resolve({
                        statusCode: 200,
                        headers: {
                            'Content-Type': contentType,
                            'Access-Control-Allow-Origin': '*'
                        },
                        body: buffer.toString('base64'),
                        isBase64Encoded: true
                    });
                });
            });

            req.on('error', (err) => {
                resolve({
                    statusCode: 502,
                    headers: { 'Access-Control-Allow-Origin': '*' },
                    body: `Proxy Error: ${err.message}`
                });
            });
        });
    } catch (e) {
        return {
            statusCode: 500,
            headers: { 'Access-Control-Allow-Origin': '*' },
            body: `Server Error: ${e.message}`
        };
    }
};