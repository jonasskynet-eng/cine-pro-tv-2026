# 🚀 Central de TV Digital Pro 2026 & Ecossistema de Estudos

![Status](https://img.shields.io/badge/Status-100%25%20Funcional-10b981?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HLS](https://img.shields.io/badge/Streaming-HLS%20Live-orange?style=for-the-badge)
![SQLite](https://img.shields.io/badge/Banco-SQLite%203-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Interface](https://img.shields.io/badge/Design-Glassmorphism%20Pro-6366f1?style=for-the-badge)

---

## 📌 Visão Geral do Projeto

Este repositório reúne o ecossistema completo desenvolvido por **Jonas**, integrando:
1. **Central de TV Digital Pro (Cinema Studio 2026):** Plataforma web autônoma e acelerada para streaming de TV aberta e por assinatura, com mais de 2.060 canais ativos, latência ultrabaixa (< 50ms), servidor proxy integrado para contorno de CORS e enquadramento de vídeo cinematográfico.
2. **Núcleo de Estudos de Engenharia, TI & Logística (UNINTER):** Materiais completos de revisão, plataformas interativas de audiobooks e cadernos técnicos de pré-cálculo e gestão da cadeia de suprimentos.

---

## 📺 Módulo 1: Central de TV Digital Pro 2026

### ✨ Principais Recursos

- **Grade Nacional Prioritária (#001 a #024):** Emissoras abertas do Brasil no topo absoluto (SBT, TV Cultura, Canal Futura / Grupo Globo, RecordTV, Band, RedeTV!, TV Brasil, TV Gazeta, etc.).
- **Pacotes VIP Fibra:** Discovery Channel, Discovery Kids, Animal Planet, Cartoon Network, TNT, Space, AXN, Sony Channel, ESPN e BandSports com rota direta por fibra óptica brasileira.
- **Filtros por Tags Multigênero:** Botões dinâmicos para seleção instantânea de **TV Aberta Brasil**, **História**, **Combate & Lutas**, **Comédia & Humor**, **Shows & Música**, **Filmes & Séries** e **Esportes**.
- **Enquadramento Fixo 16:9 / 21:9 / 4:3:** Fim das distorções de tela com ajuste inteligente pelo botão de proporção ou tecla **`A`**.
- **Servidor Streaming com Resolução 302:** Proxy inteligente em Python (`servidor_streaming_local.py`) com resolução dinâmica de URLs redirecionadas e entrega de playlists master e segmentos AES-128 sem bloqueios.
- **Modo Cinema com Glassmorphism:** Ocultação suave de barras laterais para imersão total com um clique.

### ⌨️ Atalhos de Controle Remoto pelo Teclado

| Tecla | Função |
| :---: | :--- |
| **`Espaço`** | Pausar / Reproduzir transmissão |
| **`↓` / `N`** | Próximo canal |
| **`↑` / `P`** | Canal anterior |
| **`A`** | Alternar proporção de tela (Padrão 16:9 ➔ Expandido ➔ Cinema 21:9 ➔ Clássico 4:3) |
| **`M`** | Ligar / Desligar som (Mudo) |
| **`F`** | Modo Tela Cheia |
| **`C`** | Alternar Modo Cinema |
| **`1` a `9`** | Sintonizar canais de 1 a 9 diretamente |
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
│   │   ├── banco_iptv.db                      # Banco SQLite com 2.063 canais validados
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
