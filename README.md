# 🚀 Central de TV Digital Pro 2026 — Versão 03 (v3.0 Híbrida Nuvem & Local)

![Versão](https://img.shields.io/badge/Vers%C3%A3o-v3.0%20Oficial-emerald?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-100%25%20Funcional-10b981?style=for-the-badge)
![Nuvem](https://img.shields.io/badge/Nuvem-Netlify%2024h%20Online-00C7B7?style=for-the-badge&logo=netlify&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HLS](https://img.shields.io/badge/Streaming-HLS%20%2B%20R%C3%A1dios%20Live-orange?style=for-the-badge)
![SQLite](https://img.shields.io/badge/Banco-SQLite%203-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Interface](https://img.shields.io/badge/Design-Glassmorphism%20Pro-6366f1?style=for-the-badge)

---

## 📌 Visão Geral do Projeto

Este repositório reúne o ecossistema completo desenvolvido por **Jonas**, integrando:
1. **Central de TV Digital Pro 2026 (CinePro TV — v3.0 Híbrida):** Plataforma web autônoma e acelerada para streaming de TV aberta, filmes, séries, desenhos e rádios ao vivo (**783 canais estruturados e auditados**: 698 BR, 62 PT, 9 LATAM e 14 Globais + **20 Rádios Brasileiras Ao Vivo**), funcionando tanto no servidor local (`localhost:8080`) quanto 24h na nuvem ([glittery-entremet-d4b633.netlify.app](https://glittery-entremet-d4b633.netlify.app)).
2. **Núcleo de Estudos de Engenharia, TI & Logística (UNINTER):** Materiais completos de revisão, plataformas interativas de audiobooks, pré-cálculo e gestão da cadeia de suprimentos.

---

## 🏷️ Histórico de Versões (Roadmap Oficial)

| Versão | Tag Git | Marcos e Evolução |
| :---: | :---: | :--- |
| **v1.0** | `v1.0` | Inicialização do ecossistema, banco SQLite, proxy HTTP local e scripts de sincronização GitHub. |
| **v2.0** | `v2.0` | Controle remoto por celular via QR Code Wi-Fi, PWA instalável, tela vertical 9:16 mobile e pacote nuvem. |
| **v3.0** | `v3.0` | **Edição Híbrida Nuvem & Local:** Roteamento inteligente HTTPS direto + fallback CORS na nuvem, proxy Python com decodificação GZIP/deflate, restauração da Band TV HD (`#005`), 20 rádios brasileiras agrupadas do `radiosaovivo.net`, expurgo automático de 137 canais estrangeiros infiltrados em BR, barra de categorias `flex-wrap` sem cortes com scrollbar esmeralda, QR Code híbrido funcional na nuvem e **783 canais limpos e auditados**. |

---

## 📺 Módulo 1: Central de TV Digital Pro 2026 (v3.0)

### ✨ Principais Recursos

- **Grade Nacional Limpa & Auditada (783 Canais):** Emissoras abertas brasileiras no topo (SBT Nacional, TV Cultura, RecordTV, Band TV HD, BandNews TV, RedeTV!, TV Brasil, Record News), filmes, séries, desenhos infantis e **20 Rádios Brasileiras Ao Vivo** agrupadas (`#057` a `#076`) com reprodução direta (`ehRadioDireta`).
- **Modo Híbrido Inteligente (Nuvem + PC Local):** Detecção automática de ambiente (`EH_AMBIENTE_LOCAL` + sonda `LOCAL_PROXY_ATIVO`) com `MAPA_FALLBACK_HTTPS_NUVEM` para rodar direto no navegador em **HTTPS** na nuvem sem depender de `/proxy`, mantendo aceleração máxima no proxy local em `localhost:8080`.
- **Proxy Local com Decodificação GZIP (`servidor_streaming_local.py`):** Cabeçalho `Accept-Encoding: identity` e `decodificar_manifesto` automático para evitar quebra de listas HLS compactadas.
- **Barra de Categorias Visível Sem Cortes:** Grade `flex-wrap` organizada com barra de rolagem esmeralda destacada para acesso rápido a TV Aberta, Filmes, Séries, Desenhos e Rádios.
- **QR Code Híbrido & Controle Remoto Wi-Fi:** Modal inteligente que gera o QR Code do controle remoto no PC local (`http://192.168.100.210:8080/controle.html`) e o QR Code da URL oficial da nuvem quando acessado online.
- **Enquadramento Fixo 16:9 / Preencher / Esticar:** Ajuste pelo botão de proporção ou tecla **`A`**, além de inicialização automática no Windows (`Servidor_IPTV_Automatico.vbs`).

### ⌨️ Atalhos de Controle Remoto pelo Teclado

| Tecla | Função |
| :---: | :--- |
| **`Espaço`** | Pausar / Reproduzir transmissão |
| **`↓` / `N`** | Próximo canal |
| **`↑` / `P`** | Canal anterior |
| **`A`** | Alternar proporção de tela (16:9 Cinema ➔ Preencher Tela ➔ Esticar 100%) |
| **`M`** | Ligar / Desligar som (Mudo) |
| **`F`** | Modo Tela Cheia |
| **`C`** | Alternar Modo Cinema |
| **`1` a `9`** | Sintonizar canais diretamente pelo número |
| **`?`** | Abrir painel de atalhos e ajuda |

---

## 📚 Módulo 2: Plataforma de Estudos & Acervo UNINTER

- **`CADERNO_COMPLETO_PRE_CALCULO_UNINTER.md`**: Resumo didático e passo a passo de funções, equações e limites.
- **`CRONOGRAMA_15_DIAS_LOGISTICA_E_TI.md`**: Planejamento intensivo de revisão e estudo orientado a metas práticas.
- **`Plataforma_Estudos.html`**: Aplicação interativa para escuta de audiobooks e fixação de conteúdo acadêmico.
- **`CST_LOGISTICA/`**: Estrutura analítica de logística reversa, transporte e armazenagem.

---

## 🛠️ Como Executar no Windows (Passo a Passo)

### 1. Iniciar o Servidor de Streaming Local
Execute o script em segundo plano ou via PowerShell:
```powershell
python "ECOSSISTEMA_STREAMING_IPTV\servidor_streaming_local.py"
```

### 2. Acessar a Central no Navegador
Abra no Google Chrome, Microsoft Edge ou Brave:
```text
http://localhost:8080/index.html
```
Ou dê dois cliques no arquivo gerado na Área de Trabalho: `ASSISTIR_TV.html`.

### 3. Atualizar e Recompilar Listas
Para auditar a saúde do banco de dados e regenerar o HTML e as playlists M3U:
```powershell
python "ECOSSISTEMA_STREAMING_IPTV\atualizar_central_pro.py"
```

---

## 📁 Estrutura do Repositório

```text
projeto-de-estudo/
│
├── .gitignore                                 # Regras de exclusão do Git
├── README.md                                  # Documentação técnica mestre
├── iniciar_central.bat                        # Inicializador rápido de 1 clique
│
├── ECOSSISTEMA_STREAMING_IPTV/                # Módulo Principal de Streaming
│   ├── atualizar_central_pro.py               # Compilador mestre da interface e filtros
│   ├── servidor_streaming_local.py            # Servidor HTTP proxy multi-threading
│   ├── saida/
│   │   ├── banco_iptv.db                      # Banco SQLite com 783 canais estruturados e auditados
│   │   ├── canais_leves.json                  # Catálogo em JSON estruturado
│   │   └── index.html                         # Interface do player web compilado
│   └── ...                                    # Scripts de auditoria e playlists
│
└── CST_LOGISTICA/                             # Módulo Acadêmico e Cadernos UNINTER
    ├── CADERNO_COMPLETO_PRE_CALCULO_UNINTER.md
    ├── CRONOGRAMA_15_DIAS_LOGISTICA_E_TI.md
    └── Plataforma_Estudos.html
```

---

## 📄 Licença

Desenvolvido para uso pessoal, comercial e educacional sob a licença [MIT](LICENSE).
