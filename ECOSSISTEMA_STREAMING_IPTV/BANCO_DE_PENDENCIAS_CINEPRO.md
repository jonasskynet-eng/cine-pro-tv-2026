# 📋 BANCO DE PENDÊNCIAS E MELHORIAS — CINEPRO TV 2026

**Atualizado em:** 26/11/2026  
**Banco SQLite Oficial:** `ECOSSISTEMA_STREAMING_IPTV/vip_privado/banco_clientes_vip.db` (tabela `pendencias_roadmap`)

---

## ✅ Status da Sequência 1 até 8

| Ordem | Ponto Ruim | Prioridade | Como Foi Resolvido / O Que Falta | Status |
| :---: | :--- | :---: | :--- | :---: |
| **1** | Servidor VIP ainda depende do PC ligado | Alta | `render.yaml`, `Dockerfile` (7860/8090) e guia `SUBIR_NA_NUVEM_24H.md` prontos (só dar 1 clique no Render/HF) | `PRONTO_DEPLOY` |
| **2** | Nuvem grátis dorme e pode zerar cadastros ao reiniciar | Alta | Sync automático com Cloudflare D1 (`/api/sync-clientes-vip` em `worker.js` + `servidor_streaming_local.py`) | `CONCLUIDO` |
| **3** | Sem futebol pago ao vivo (Premiere, SporTV, ESPN, HBO) | Alta | Campo direto de Lista VIP/Revenda `.m3u` no `/admin` + pasta `vip_privado` (só colar link pago quando tiver) | `PRONTO_USO` |
| **4** | Sinais gratuitos oscilam mais no horário nobre | Média | `enriquecer_reservas.py` + `docs/tv.html` com troca automática Plano B e Plano C | `CONCLUIDO` |
| **5** | Guia de programação (EPG) genérico em vários canais 24h | Baixa | `atualizar_epg_br.py` turbinado com guia oficial Pluto TV BR (`epg_br.json`) | `CONCLUIDO` |
| **6** | IP local (`192.168.100.210`) pode mudar se faltar luz na casa | Média | Criado `FIXAR_IP_CASA_TV.bat` e atalho no `GERENCIAR_DOCKER_VIP.bat` | `CONCLUIDO` |
| **7** | Venda e liberação manuais no WhatsApp (sem PIX automático) | Média | `POST /api/webhook/pix` (Mercado Pago / Asaas / Direto) + tabela `pagamentos_pix` + simulador no `/admin` | `CONCLUIDO` |
| **8** | Senha padrão do painel (`jonas2026`) antes de ir para a internet | Alta | Removida senha fixa de `docs/admin.html` e `render.yaml` (`generateValue: true`) | `CONCLUIDO` |
