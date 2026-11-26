# ☁️ Como Subir o CinePro VIP na Nuvem 24h (Grátis — Sem PC Ligado)

Este guia coloca seu servidor completo (com **1.007 canais**, painel `/admin`, modo **Smart TV Samsung** `/tv` e **PIX automático**) no ar 24 horas por dia de graça.

---

## Opção 1 — Render.com (Mais Fácil — 2 Cliques)

1. Crie uma conta gratuita em **https://render.com** (pode entrar com sua conta do GitHub `jonasskynet-eng`).
2. Clique em **New +** → **Blueprint**, escolha o repositório **`cine-pro-tv-2026`** e clique em **Apply**.
   - O arquivo `render.yaml` já cria tudo sozinho e gera um **PIN secreto automático** em `CINEPRO_ADMIN_PIN` (você vê ou edita ele na aba **Environment** do Render).
3. *(Recomendado para nunca perder clientes ao reiniciar)* Na aba **Environment** no Render, preencha:
   - `CINEPRO_CLOUD_SYNC_URL`: `https://cinepro-tv-proxy.jonasskynet.workers.dev/api/sync-clientes-vip`
   - `CINEPRO_CLOUD_SYNC_TOKEN`: a mesma senha do seu Worker (`ADMIN_SENHA`)
   - `PIX_WEBHOOK_SECRET`: uma palavra secreta sua para proteger o webhook do PIX
   - `VIP_M3U_URL`: *(opcional)* link direto de uma lista `.m3u` de revenda paga, ou cole direto no painel `/admin`.

---

## Opção 2 — Hugging Face Spaces (16 GB RAM Grátis)

1. Crie um Space novo em **https://huggingface.co/spaces** escolhendo **Docker** → **Blank**.
2. Conecte ou envie os arquivos do repositório `cine-pro-tv-2026` (o `Dockerfile` já usa a porta `7860` automática do Hugging Face).
3. Em **Settings → Variables and secrets**, adicione `CINEPRO_ADMIN_PIN`, `CINEPRO_CLOUD_SYNC_URL`, `CINEPRO_CLOUD_SYNC_TOKEN` e `PIX_WEBHOOK_SECRET`.

---

## ✅ Depois de Subir na Nuvem

- **Painel de Clientes:** `https://SEU-SITE-NA-NUVEM/admin`
- **Player Web/Celular:** `https://SEU-SITE-NA-NUVEM/`
- **Modo TV Samsung Leve:** `https://SEU-SITE-NA-NUVEM/tv`
- **Webhook PIX 24h:** `https://SEU-SITE-NA-NUVEM/api/webhook/pix`
