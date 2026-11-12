# 🎓 Guia Mestre de Análise e Revisão — Faculdade Uninter (TI)

**Origem no Google Drive:** Pasta `02_ESTUDOS_FACULDADE_E_AUDIOBOOK_TI`  
**Arquivos Sincronizados Localmente:** [Plataforma_Estudos.html](file:///c:/Users/jonas/Downloads/projeto%20de%20estudo/Plataforma_Estudos.html) | [dados_audiobook.json](file:///c:/Users/jonas/Downloads/projeto%20de%20estudo/dados_audiobook.json) | [dados_audiobook.js](file:///c:/Users/jonas/Downloads/projeto%20de%20estudo/dados_audiobook.js)

---

## 📊 Visão Geral da Estrutura Encontrada no Google Drive

A sua pasta da faculdade no Google Drive está dividida em **2 grandes blocos**:
1. **Grade Curricular de TI (Uninter) — 6 Disciplinas (36 Aulas Completas):**
   - `Ferramentas de Desenvolvimento Web` (6 aulas)
   - `Lógica de Programação e Algoritmos` — Foco em **Python** (6 aulas)
   - `Análise e Modelagem de Sistemas` — Foco em **BPMN, Requisitos e UML** (6 aulas)
   - `Pré-Cálculo` — Funções, Trigonometria e Matrizes (6 aulas)
   - `Formação Inicial em Educação a Distância (EaD)` (6 aulas)
   - `Produção Textual Politécnica` (6 aulas)
2. **Acervo Prático e Atividades Extensionistas (`Cursos_TI`):**
   - **Atividades Extensionistas e Gestão/Logística:** Roteirização de Cargas (planilhas `.xlsx` de estudo e modelos), Empreendedorismo, Qualidade Preventiva e Produção 4.0.
   - **Biblioteca Técnica de Infraestrutura e Redes:** E-books completos de Linux (Básico ao Profissional), Redes Windows/Estruturadas, MikroTik, Manutenção de Hardware, Upgrade, Formatação e Eletrônica/Multímetro.

---

## 💻 1. Ferramentas de Desenvolvimento Web
**Docente:** Prof.ª Luciane Yanase Hirabara Kanashiro

### Mapa das 6 Aulas e Conceitos-Chave de Prova:
* **Aula 01 — Software:**
  * **Diferença Clássica (Cai sempre em prova):**
    * **Programa:** Conjunto de instruções/código isolado que executa uma tarefa.
    * **Software:** É mais amplo (Pressman): soma as **instruções (programas)** + **estruturas de dados** + **documentação**.
    * **Sistema:** Conjunto de elementos integrados (hardware, software, pessoas, processos) trabalhando para um objetivo comum.
  * **Sistemas Operacionais (SO):** Gerenciam o hardware (CPU, memória, disco) e fazem a ponte entre o usuário/aplicativos e a máquina.
  * **Ciclo de Vida de Software:** Modelos **Cascata** (sequencial, rígido), **Espiral/Iterativo** (focado em riscos e ciclos) e **Metodologias Ágeis** (Scrum/Kanban, entregas rápidas e adaptáveis).
* **Aula 02 — O Profissional de TI e sua Atuação:**
  * **Crise do Software (anos 1960/70):** Projetos atrasados, acima do orçamento e com baixa qualidade, o que deu origem à **Engenharia de Software**.
  * **Perfis:** Desenvolvedor Front-end (interface), Back-end (regra de negócio/servidor), Fullstack (ambos), Analista de Sistemas, DBA e QA (Testes).
* **Aula 03 — Desenvolvimento Colaborativo:**
  * **Versionamento de Código (Git) e Repositórios (GitHub/GitLab):** Controle de histórico, *branches* (ramificações), *merge* (junção) e prevenção de conflito de código em equipe.
  * **Qualidade e Deploy:** Testes unitários, testes de integração e entrada em produção (*deploy*).
* **Aula 04 — HTML (Estrutura):**
  * Linguagem de **marcação** (não é linguagem de programação).
  * Estrutura base: `<!DOCTYPE html>`, `<html>`, `<head>` (metadados/título) e `<body>` (conteúdo visível).
  * Principais tags: títulos (`<h1>` a `<h6>`), parágrafos (`<p>`), links (`<a href="...">`), imagens (`<img src="...">`), listas (`<ul>`, `<ol>`, `<li>`), tabelas (`<table>`, `<tr>`, `<td>`) e formulários (`<form>`, `<input>`).
* **Aula 05 — CSS (Estilo):**
  * **Seletores fundamentais (Questão certa de prova):**
    * **Universal:** `* { ... }` (afeta todos os elementos).
    * **Por Tag:** `h1 { ... }`, `p { ... }`.
    * **Por Classe (`.`):** `.alerta { color: red; }` — pode ser usado em **vários** elementos (`class="alerta"`).
    * **Por ID (`#`):** `#invertido { ... }` — deve ser **único** na página (`id="invertido"`).
    * **Seletor de Filho Direto (`>`):** `body > p` (seleciona apenas os `<p>` que são filhos diretos de `<body>`).
* **Aula 06 — JavaScript e JSON (Comportamento e Dados):**
  * **JavaScript:** Linguagem de programação executada no navegador (*client-side*) para dar interatividade e manipular o DOM.
  * **JSON (*JavaScript Object Notation*):** Formato leve de troca de dados estruturado em pares `"chave": valor`.

---

## 🐍 2. Lógica de Programação e Algoritmos (Python)
**Docente:** Prof. Vinicius Pozzobon Borin

### Mapa das 6 Aulas e Conceitos-Chave de Prova (e Trabalho Prático):
* **Aula 01 — Introdução à Lógica, Algoritmos e Python:**
  * Formas de representar algoritmos: **Descrição Narrativa** (linguagem natural), **Fluxograma** (gráfico) e **Pseudocódigo** (Portugol).
  * **Compilador vs. Interpretador:** O compilador traduz todo o código-fonte de uma vez para linguagem de máquina; o interpretador (como no Python) lê e executa linha por linha.
* **Aula 02 — Variáveis, Tipos de Dados e Strings:**
  * **Ciclo de Processamento:** Entrada (`input()`) $\rightarrow$ Processamento $\rightarrow$ Saída (`print()`).
  * **Tipos primitivos em Python:** `int` (inteiro), `float` (decimal), `bool` (`True`/`False`) e `str` (texto).
  * **Atenção na prova:** `input()` sempre retorna `str`! Para calcular números, é obrigatório converter: `int(input())` ou `float(input())`.
* **Aula 03 — Estruturas de Seleção/Decisão (`if`, `elif`, `else`):**
  * **Operadores Relacionais:** `==` (igual), `!=` (diferente), `>`, `<`, `>=`, `<=`.
  * **Operadores Lógicos (Álgebra Booleana):**
    * `and` (E): Só é verdadeiro se **ambas** as condições forem verdadeiras.
    * `or` (OU): É verdadeiro se **pelo menos uma** condição for verdadeira.
    * `not` (NÃO): Inverte o valor lógico.
* **Aula 04 — Estruturas de Repetição (`while` e `for`):**
  * `while` (Enquanto): Usado quando **não sabemos** exatamente quantas vezes o laço vai repetir (depende de uma condição). Cuidado com o *loop infinito*!
  * `for` (Para): Usado com `range(inicio, fim, passo)` quando sabemos o número de repetições ou percorremos uma sequência.
  * **Comandos de controle:** `break` (interrompe o laço imediatamente) e `continue` (pula para a próxima repetição).
* **Aula 05 — Funções (`def`):**
  * Modularização e reaproveitamento de código: `def minha_funcao(parametro):`.
  * **Escopo de Variáveis:** Variáveis **locais** (existem apenas dentro da função) vs. variáveis **globais** (existem no programa principal).
  * **Retorno (`return`):** Devolve o resultado processado para quem chamou a função (diferente de apenas dar `print`).
* **Aula 06 — Estruturas de Dados Compostas (Diferença clássica de prova!):**
  * **Tuplas `()`:** **Imutáveis** (não é possível alterar, adicionar ou remover itens após criadas). Ex: `tupla = (10, 20, 30)`.
  * **Listas `[]`:** **Mutáveis** e indexadas por posição (`0, 1, 2...`). Métodos: `.append()`, `.remove()`, `.pop()`. Ex: `lista = [10, 20, 30]`.
  * **Dicionários `{}`:** Coleções **mutáveis** baseadas em **`chave: valor`**. Ex: `aluno = {"nome": "Jonas", "nota": 10}`.

---

## 📐 3. Análise e Modelagem de Sistemas
**Docente:** Prof.ª Adriana Bastos da Costa

### Mapa das 6 Aulas e Conceitos-Chave de Prova:
* **Aula 01 — Processos de Negócio e BPMN:**
  * **AS-IS vs. TO-BE:**
    * **AS-IS ("Como está"):** Mapeamento do processo atual da empresa, identificando gargalos e falhas.
    * **TO-BE ("Como deve ser"):** Redesenho otimizado do processo futuro com melhoria e automação.
  * **Elementos BPMN:** Eventos (círculos: início, intermediário, fim), Atividades/Tarefas (retângulos arredondados), Gateways/Decisões (losangos) e Raias/Piscinas (*Pools* e *Lanes* — definem quem faz o quê).
* **Aula 02 — Análise Estruturada e DFD (Diagrama de Fluxo de Dados):**
  * **4 Componentes do DFD:** Processo (transforma dados), Fluxo de Dados (setas), Depósito de Dados (arquivos/bancos) e Entidade Externa (origem ou destino fora do sistema).
  * **Níveis:** Diagrama de Contexto (Nível 0 — visão macro com um único processo central), Nível 1, Nível 2 (explosão/detalhamento).
* **Aula 03 — Engenharia de Requisitos:**
  * **Requisito Funcional (RF) vs. Requisito Não Funcional (RNF) — Cai em 100% das provas:**
    * **RF (O que o sistema faz):** Funcionalidades diretas. Ex: *"O sistema deve permitir emitir nota fiscal"*, *"O usuário deve poder cadastrar clientes"*.
    * **RNF (Como o sistema se comporta / restrições e qualidade):** Desempenho, segurança, disponibilidade, usabilidade, linguagem exigida. Ex: *"O sistema deve responder em menos de 2 segundos"*, *"Deve usar criptografia HTTPS"*.
  * **Estórias de Usuário (*User Stories* — Ágil):** Formato padrão: *"Como [papel/ator], eu quero [ação/funcionalidade], para que [benefício/valor de negócio]"*.
* **Aula 04 — UML e Diagrama de Caso de Uso:**
  * **Componentes:** Atores (bonecos palito — usuários ou sistemas externos), Casos de Uso (elipses — ações) e Fronteira do Sistema.
  * **Relacionamentos entre Casos de Uso (Pegadinha clássica de prova!):**
    * **`<<include>>` (Inclusão):** Obrigatório! Sempre que o caso de uso base executa, o incluído **também executa** (ex: *Sacar Dinheiro* `<<include>>` *Autenticar Senha*).
    * **`<<extend>>` (Extensão):** Opcional/Condicional! Só executa em situações específicas (ex: *Fazer Pedido* `<<extend>>` *Aplicar Cupom de Desconto*).
* **Aula 05 — Diagrama de Classes (POO):**
  * Representa a estrutura estática do sistema: **Nome da Classe**, **Atributos** (características/dados) e **Métodos** (ações/operações).
  * **Visibilidade:** `+` Público (*public*), `-` Privado (*private*), `#` Protegido (*protected*).
  * **Relacionamentos:** Associação, **Agregação** (losango vazio — o parte vive sem o todo), **Composição** (losango preenchido — relação forte, se o todo morre, a parte morre junto) e **Herança/Generalização** (seta triangular).
* **Aula 06 — Outros Diagramas UML Importantes:**
  * **Diagrama de Estados:** Mostra os estados de um único objeto ao longo do seu ciclo de vida (ex: Pedido *Aberto* $\rightarrow$ *Pago* $\rightarrow$ *Enviado* $\rightarrow$ *Entregue*).
  * **Diagrama de Atividades:** Fluxo de trabalho passo a passo (similar ao fluxograma).
  * **Diagrama de Sequência:** Mostra a troca de mensagens entre objetos **organizada na linha do tempo**.
  * **Diagrama de Componentes:** Arquitetura física/módulos de software e suas dependências.

---

## 📈 4. Pré-Cálculo
* **Aula 01 e 02 — Funções, Funções Lineares e Quadráticas:**
  * **Domínio ($D$):** Valores de entrada ($x$). **Imagem ($Im$):** Valores resultantes ($y$).
  * **Função Linear (1º Grau):** $f(x) = ax + b$ (gráfico é uma **reta**; se $a > 0$ é crescente, se $a < 0$ é decrescente).
  * **Função Quadrática (2º Grau):** $f(x) = ax^2 + bx + c$ (gráfico é uma **parábola**; $a > 0$ concavidade para cima, $a < 0$ concavidade para baixo; raízes por Bhaskara $\Delta = b^2 - 4ac$).
* **Aula 03 — Funções Exponenciais e Logarítmicas:**
  * **Exponencial:** $f(x) = a^x$ (a variável está no expoente).
  * **Logarítmica:** Inversa da exponencial ($\log_a b = x \iff a^x = b$).
* **Aula 04 e 05 — Trigonometria (Partes 1 e 2):**
  * **Conversão Graus $\leftrightarrow$ Radianos:** $180^\circ = \pi\text{ rad}$ (regra de três simples).
  * **Triângulo Retângulo (Teorema de Pitágoras):** $h^2 = c_1^2 + c_2^2$.
  * **Razões Trigonométricas (SOH-CAH-TOA):**
    * $\text{Seno} = \frac{\text{Cateto Oposto}}{\text{Hipotenusa}}$
    * $\text{Cosseno} = \frac{\text{Cateto Adjacente}}{\text{Hipotenusa}}$
    * $\text{Tangente} = \frac{\text{Cateto Oposto}}{\text{Cateto Adjacente}}$
* **Aula 06 — Sistemas Lineares, Matrizes e Determinantes:**
  * **Classificação de Sistemas Lineares (Cai muito!):**
    * **SPD (Sistema Possível e Determinado):** Possui **uma única solução** ($\det \neq 0$).
    * **SPI (Sistema Possível e Indeterminado):** Possui **infinitas soluções**.
    * **SI (Sistema Impossível):** **Não possui solução** (inconsistente).

---

## 🌐 5. Formação Inicial em EaD & ✍️ 6. Produção Textual Politécnica
* **Formação Inicial em EaD (6 aulas):**
  * Evolução histórica da EaD no Brasil (do ensino por correspondência, rádio e TV até os Ambientes Virtuais de Aprendizagem — AVA Univirtus).
  * **Conceitos-chave:** **Autonomia do estudante** (gestão do tempo e protagonismo), **Conectivismo** (aprendizagem em rede mediada por tecnologia) e o papel do **professor/tutor como mediador** do conhecimento.
* **Produção Textual Politécnica (6 aulas):**
  * **Leitura Crítica Multimodal (Aula 1):** Interpretação integrada de textos verbais e **não verbais** (gráficos, tabelas, diagramas e fluxogramas técnicos).
  * **Escrita Técnica e Científica (Aula 2 a 6):** Clareza, concisão, impessoalidade, coesão/coerência e estruturação de **Relatórios Técnicos** (Introdução, Desenvolvimento/Metodologia, Resultados e Conclusão).
