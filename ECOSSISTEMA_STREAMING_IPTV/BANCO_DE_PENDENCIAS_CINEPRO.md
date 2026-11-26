# 📋 BANCO DE PENDÊNCIAS E MELHORIAS — CINEPRO TV 2026

**Registrado em:** 25/11/2026 às 23:47  
**Banco SQLite Oficial:** `ECOSSISTEMA_STREAMING_IPTV/vip_privado/banco_clientes_vip.db` (tabela `pendencias_roadmap`)

---

## 🔴 Os 8 Pontos Ruins para Resolvermos nos Próximos Dias

| Ordem | Ponto Ruim | Prioridade | Como Vamos Resolver | Status |
| :---: | :--- | :---: | :--- | :---: |
| **1** | Servidor VIP ainda depende do PC ligado | Alta | Subir o Docker no Render / Hugging Face Spaces 24h | `PENDENTE` |
| **2** | Nuvem grátis dorme e pode zerar cadastros ao reiniciar | Alta | Ligar banco externo (Turso / Neon / D1) ou volume persistente | `PENDENTE` |
| **3** | Sem futebol pago ao vivo (Premiere, SporTV, ESPN, HBO) | Alta | Plugar lista `.m3u` de revenda na pasta `vip_privado` | `PENDENTE` |
| **4** | Sinais gratuitos oscilam mais no horário nobre | Média | Adicionar 2º e 3º links reserva (Plano B e C) nos principais | `PENDENTE` |
| **5** | Guia de programação (EPG) genérico em vários canais 24h | Baixa | Conectar EPG XMLTV completo com nomes dos filmes/séries | `PENDENTE` |
| **6** | IP local (`192.168.100.210`) pode mudar se faltar luz na casa | Média | Fixar IP no Windows/Roteador ou usar endereço fixo da nuvem | `PENDENTE` |
| **7** | Venda e liberação manuais no WhatsApp (sem PIX automático) | Média | Integrar webhook PIX (Mercado Pago / Asaas) criando login na hora | `PENDENTE` |
| **8** | Senha padrão do painel (`jonas2026`) antes de ir para a internet | Alta | Definir senha secreta forte na variável `CINEPRO_ADMIN_PIN` | `PENDENTE` |
