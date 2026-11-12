# 📚 Caderno Completo e Explicado Passo a Passo — Pré-Cálculo (Uninter)

> **Por que este caderno é especial?**  
> Na apostila original da Uninter, os **Exemplos Didáticos** trazem apenas a pergunta e dizem *"Assista ao vídeo de 5 min"*, sem mostrar a conta escrita. Neste caderno completo, **todos os conceitos, todos os exemplos dos vídeos e todos os exercícios da apostila estão resolvidos e explicados linha por linha**, sem pular nenhuma passagem!

---

# 🟦 AULA 01 COMPLETA — FUNÇÕES E GRÁFICOS

## 📖 Conversa Inicial e Base da Disciplina
O objetivo do Pré-Cálculo na Uninter (baseado nos livros de *Sheldon Axler* e *Franklin Demana*) é construir a sua base matemática para cursos de Tecnologia e Engenharia. Tudo na programação e na engenharia começa com o conceito de **Função**.

---

## 🔹 TEMA 1: O Que é Função, Domínio, Contradomínio e Imagem?

### 1.1 A Ideia da "Máquina de Transformar Números"
Imagine uma máquina industrial:
* Você coloca uma matéria-prima na entrada: chamamos essa entrada de **$x$** (**Variável Independente**, porque você escolhe livremente qual número vai colocar).
* Dentro da máquina existe uma **regra matemática** (por exemplo: *"multiplique por 2 e some 1"*).
* Do outro lado sai o produto pronto: chamamos essa saída de **$y$** ou **$f(x)$** (**Variável Dependente**, porque o resultado que sai *depende* do número $x$ que você colocou).

### 1.2 Definição Oficial (Axler, 2016, p. 40)
> *"Uma função associa cada número de um dado conjunto de números reais, chamado **domínio da função**, a exatamente um número real."*

O que isso quer dizer na prática?
1. **Domínio ($D$):** É o conjunto de **todos os números $x$ que podem entrar** na função sem dar erro matemático.
2. **Imagem ($Im$):** É o conjunto de **todos os resultados $y$ que saem** da função após fazermos a conta.
3. **Regra de Existência:** Cada número $x$ que entra só pode gerar **um único** resultado $y$.

### 1.3 As 3 Regras de Ouro do Domínio nos Números Reais ($\mathbb{R}$)
Na prova da Uninter, quando perguntarem **"Qual é o domínio da função?"**, você só precisa olhar se a função tem **fração** ou **raiz**:

* **CASO 1 — Função comum (sem fração com $x$ embaixo e sem raiz):**
  * Exemplo: $f(x) = 2x + 1$ ou $f(x) = x^2 - 4$.
  * Você pode colocar qualquer número no lugar do $x$ (positivo, negativo, zero, fração).
  * **Resposta:** O domínio são **todos os números reais** ($D = \mathbb{R}$).

* **CASO 2 — Função com Fração (onde o $x$ está na parte de baixo / denominador):**
  * **Regra absoluta da Matemática:** **É proibido dividir por ZERO!** (Tente fazer $5 \div 0$ na calculadora: dá erro!).
  * Portanto, a parte de baixo da fração **tem que ser diferente de zero ($\neq 0$)**.
  * Exemplo: $f(x) = \frac{1}{x - 3} \rightarrow$ A parte de baixo é $x - 3$. Fazemos $x - 3 \neq 0 \rightarrow x \neq 3$.

* **CASO 3 — Função com Raiz de Índice Par ($\sqrt{\quad}$, raiz quadrada, quarta, etc.):**
  * **Regra absoluta nos Números Reais:** **Não existe raiz quadrada real de número negativo!** (Por exemplo, $\sqrt{-4}$ não existe nos Reais, pois $(-2) \times (-2) = +4$).
  * Portanto, tudo o que estiver dentro de uma raiz quadrada **tem que ser maior ou igual a zero ($\ge 0$)**.
  * **Atenção:** Se a raiz for **ímpar** (como raiz cúbica $\sqrt[3]{\quad}$), **pode** ter número negativo dentro! (Ex: $\sqrt[3]{-8} = -2$, porque $(-2)\times(-2)\times(-2) = -8$). Logo, na raiz cúbica, o domínio é $D = \mathbb{R}$.

* **CASO 4 — Raiz Quadrada na Parte de Baixo da Fração ($\frac{1}{\sqrt{\quad}}$):**
  * Junta o Caso 2 (não pode ser zero) com o Caso 3 (não pode ser negativo).
  * Portanto, o que está dentro da raiz embaixo da fração tem que ser **estritamente maior que zero ($> 0$)**.

---

## 🔹 TEMA 2: Exemplos Didáticos I (Resolução Completa dos Vídeos da Aula 1)

### 📌 Exemplo 1 da Apostila (Modelagem de Custo de Produção)
> **Enunciado:** Suponha uma empresa que produz uma peça $x$ que tem seu custo de fabricação de $\text{R\$ } 2\text{,00}$ por unidade (Custo Unitário). Sabendo que essa linha de fabricação tem um custo fixo, independentemente da quantidade fabricada, de $\text{R\$ } 1.000\text{,00}$, monte a função que representa o custo produtivo (Custo Total) dessa peça.

**👨‍🏫 Explicação Passo a Passo:**
1. O **Custo Fixo** é aquele que a fábrica paga mesmo se produzir $0$ peças (aluguel do galpão, energia básica, etc.): vale **$\text{R\$ } 1.000\text{,00}$**.
2. O **Custo Variável** depende de quantas peças **$x$** serão fabricadas. Como cada peça custa $\text{R\$ } 2\text{,00}$:
   * Se fabricar $1$ peça: gasta $2 \times 1 = 2$ reais.
   * Se fabricar $10$ peças: gasta $2 \times 10 = 20$ reais.
   * Se fabricar **$x$** peças: gasta **$2 \cdot x$** reais.
3. O **Custo Total $C(x)$** é a soma do Custo Variável com o Custo Fixo:
   $$C(x) = 2x + 1000 \quad \text{(ou } f(x) = 2x + 1000\text{)}$$

---

### 📌 Exemplo 2 da Apostila (Questão ENEM 2017 — Proporção e Conversão de Unidades)
> **Enunciado:** Em alguns países anglo-saxões, a unidade de volume utilizada para indicar o conteúdo de alguns recipientes é a onça fluida britânica. O volume de uma onça fluida britânica corresponde a $28\text{,4130625 ml}$. A título de simplificação, considere uma onça fluida britânica correspondendo a $28\text{ ml}$. Nessas condições, o volume de um recipiente com capacidade de $400$ onças fluidas britânicas, em $\text{cm}^3$, é igual a:  
> a) $11.200$ | b) $1.120$ | c) $112$ | d) $11\text{,2}$ | e) $1\text{,12}$

**👨‍🏫 Explicação Passo a Passo:**
1. **Entendendo a relação entre $\text{ml}$ (mililitro) e $\text{cm}^3$ (centímetro cúbico):**
   * Na Física e na Matemática, **$1\text{ ml}$ é exatamente igual a $1\text{ cm}^3$** ($1\text{ ml} = 1\text{ cm}^3$). Essa é a pegadinha da questão: você não precisa converter no final, pois o valor em $\text{ml}$ já é o próprio valor em $\text{cm}^3$!
2. **Montando a função do volume:**
   * Se $1$ onça fluida tem $28\text{ ml}$ ($28\text{ cm}^3$), então para $x$ onças fluidas a função é:
     $$V(x) = 28 \cdot x$$
3. **Calculando para $x = 400$ onças fluidas:**
   * Multiplicamos $28 \times 400$:
   * Fazendo $28 \times 4 = 112$, e acrescentando os dois zeros do $400$, temos **$11.200\text{ cm}^3$**.
* **Gabarito:** **Alternativa a) $11.200$**.

---

### 📌 Exemplo 3 da Apostila (Cálculo de Valores e Domínio de Função Polinomial)
> **Enunciado:** Dada a função $f(x) = 2x + 1$, responda o que se pede:  
> a) Qual o domínio dessa função?  
> b) $f(2) = \text{?}$  
> c) $f(-1) = \text{?}$  
> d) $f(0) = \text{?}$  
> e) $f\left(\frac{1}{3}\right) = \text{?}$

**👨‍🏫 Explicação Passo a Passo:**
* **a) Qual o domínio dessa função?**
  * Olhamos para $f(x) = 2x + 1$. Tem fração com $x$ embaixo? **Não.** Tem raiz quadrada? **Não.**
  * Então qualquer número real pode entrar no lugar do $x$.
  * **Resposta a):** $D = \mathbb{R}$ (Conjunto dos Números Reais).

* **b) Quanto vale $f(2)$?**
  * O número dentro dos parênteses é o valor que vamos colocar **no lugar da letra $x$**.
  * Onde está escrito $2x + 1$, significa $2 \times x + 1$. Trocando $x$ por $2$:
    $$f(2) = 2 \cdot (2) + 1$$
    $$f(2) = 4 + 1 = \mathbf{5}$$

* **c) Quanto vale $f(-1)$?**
  * Trocamos o $x$ por $-1$ (use parênteses por causa do sinal de menos!):
    $$f(-1) = 2 \cdot (-1) + 1$$
  * Regra de sinais na multiplicação: positivo vezes negativo dá negativo ($2 \times (-1) = -2$):
    $$f(-1) = -2 + 1$$
  * Devo $2$ e tenho $1$: continuo devendo $1$:
    $$f(-1) = \mathbf{-1}$$

* **d) Quanto vale $f(0)$?**
  * Trocamos o $x$ por $0$:
    $$f(0) = 2 \cdot (0) + 1 = 0 + 1 = \mathbf{1}$$

* **e) Quanto vale $f\left(\frac{1}{3}\right)$?**
  * Trocamos o $x$ pela fração $\frac{1}{3}$:
    $$f\left(\frac{1}{3}\right) = 2 \cdot \left(\frac{1}{3}\right) + 1$$
  * Na multiplicação de $2$ por $\frac{1}{3}$, multiplicamos o $2$ pelo número de cima ($2 \times 1 = 2$):
    $$f\left(\frac{1}{3}\right) = \frac{2}{3} + 1$$
  * Como somar a fração $\frac{2}{3}$ com o número inteiro $1$? O número $1$ inteiro equivale a $\frac{3}{3}$ (pois $3 \div 3 = 1$). Assim deixamos os dois com o mesmo denominador $3$:
    $$f\left(\frac{1}{3}\right) = \frac{2}{3} + \frac{3}{3} = \frac{2 + 3}{3} = \mathbf{\frac{5}{3}} \quad (\text{ou } \approx 1\text{,67})$$

---

## 🔹 TEMA 3 e TEMA 4: Exemplos Didáticos II e III (Frações, Raízes e Função Composta)

### 📌 Exemplo 4 da Apostila (Função com Fração)
> **Enunciado:** Dada a função $f(x) = \frac{1}{x + 1}$, responda o que se pede:  
> a) Qual o domínio dessa função? | b) $f(1) = \text{?}$ | c) $f(-2) = \text{?}$ | d) $f(0) = \text{?}$ | e) $f\left(\frac{1}{2}\right) = \text{?}$

**👨‍🏫 Explicação Passo a Passo:**
* **a) Domínio:**
  * Como tem $x$ na parte de baixo da fração ($x + 1$), a parte de baixo **não pode dar zero**:
    $$x + 1 \neq 0$$
  * Passamos o $+1$ para o outro lado trocando o sinal para $-1$:
    $$x \neq -1$$
  * **Resposta a):** $D = \{x \in \mathbb{R} \mid x \neq -1\}$ (Todos os reais, exceto o $-1$, pois se $x = -1$, teríamos $-1 + 1 = 0$ embaixo!).

* **b) Cálculo de $f(1)$:** Trocamos $x$ por $1$:
  $$f(1) = \frac{1}{1 + 1} = \mathbf{\frac{1}{2}} \quad (\text{ou } 0\text{,5})$$

* **c) Cálculo de $f(-2)$:** Trocamos $x$ por $-2$:
  $$f(-2) = \frac{1}{-2 + 1} = \frac{1}{-1} = \mathbf{-1}$$

* **d) Cálculo de $f(0)$:** Trocamos $x$ por $0$:
  $$f(0) = \frac{1}{0 + 1} = \frac{1}{1} = \mathbf{1}$$

* **e) Cálculo de $f\left(\frac{1}{2}\right)$:** Trocamos $x$ por $\frac{1}{2}$:
  $$f\left(\frac{1}{2}\right) = \frac{1}{\frac{1}{2} + 1}$$
  * Somando embaixo: $\frac{1}{2} + 1 = \frac{1}{2} + \frac{2}{2} = \frac{3}{2}$.
  * Agora temos $1$ dividido por $\frac{3}{2}$. **Regra de divisão de fração:** conservamos o de cima ($1$) e multiplicamos pelo de baixo **invertido** ($\frac{2}{3}$):
    $$f\left(\frac{1}{2}\right) = 1 \cdot \frac{2}{3} = \mathbf{\frac{2}{3}}$$

---

### 📌 Exemplo 5 da Apostila (Função com Raiz Quadrada)
> **Enunciado:** Dada a função $f(x) = \sqrt{x - 3}$, responda:  
> a) Qual o domínio dessa função? | b) $f(4) = \text{?}$ | c) $f\left(\frac{7}{2}\right) = \text{?}$

**👨‍🏫 Explicação Passo a Passo:**
* **a) Domínio:**
  * É uma raiz quadrada (índice 2, par). O que está dentro dela ($x - 3$) tem que ser **maior ou igual a zero ($\ge 0$)**:
    $$x - 3 \ge 0 \implies x \ge 3$$
  * **Resposta a):** $D = \{x \in \mathbb{R} \mid x \ge 3\}$ (Só aceita números de $3$ para cima!).

* **b) Cálculo de $f(4)$:** Trocamos $x$ por $4$:
  $$f(4) = \sqrt{4 - 3} = \sqrt{1} = \mathbf{1}$$

* **c) Cálculo de $f\left(\frac{7}{2}\right)$:** Trocamos $x$ por $\frac{7}{2}$ (que é $3\text{,5}$):
  * Em fração: $\frac{7}{2} - 3 = \frac{7}{2} - \frac{6}{2} = \frac{1}{2}$.
  * Tirando a raiz:
    $$f\left(\frac{7}{2}\right) = \sqrt{\frac{1}{2}} = \frac{\sqrt{1}}{\sqrt{2}} = \frac{1}{\sqrt{2}}$$
  * **Racionalizando** (multiplicando em cima e embaixo por $\sqrt{2}$ para tirar a raiz de baixo):
    $$\frac{1 \cdot \sqrt{2}}{\sqrt{2} \cdot \sqrt{2}} = \mathbf{\frac{\sqrt{2}}{2}} \quad (\approx 0\text{,707})$$

---

### 📌 Exemplo 6 da Apostila (Função com Raiz Cúbica — Índice Ímpar!)
> **Enunciado:** Dada a função $f(x) = \sqrt[3]{x + 2}$, responda:  
> a) Qual o domínio dessa função? | b) $f(6) = \text{?}$ | c) $f(-29) = \text{?}$

**👨‍🏫 Explicação Passo a Passo:**
* **a) Domínio:**
  * Olhe o número pequenininho em cima da raiz: é um **$3$** (raiz cúbica, **ímpar**!).
  * Raiz ímpar aceita números positivos, zero e também **negativos**!
  * **Resposta a):** $D = \mathbb{R}$ (Todos os números reais).

* **b) Cálculo de $f(6)$:**
  $$f(6) = \sqrt[3]{6 + 2} = \sqrt[3]{8}$$
  * Qual número multiplicado por ele mesmo $3$ vezes dá $8$? É o $2$, pois $2 \times 2 \times 2 = 8$.
  * **Resposta b):** $f(6) = \mathbf{2}$.

* **c) Cálculo de $f(-29)$:**
  $$f(-29) = \sqrt[3]{-29 + 2} = \sqrt[3]{-27}$$
  * Qual número multiplicado por ele mesmo $3$ vezes dá $-27$? É o **$-3$**, pois $(-3) \times (-3) \times (-3) = (+9) \times (-3) = -27$.
  * **Resposta c):** $f(-29) = \mathbf{-3}$.

---

### 📌 Exemplo 7 da Apostila (Raiz Quadrada no Denominador da Fração)
> **Enunciado:** Dada a função $f(x) = \frac{1}{\sqrt{x + 1}}$, responda:  
> a) Qual o domínio dessa função? | b) $f(1) = \text{?}$ | c) $f(0) = \text{?}$

**👨‍🏫 Explicação Passo a Passo:**
* **a) Domínio:**
  * A raiz quadrada está **embaixo da fração**. Logo, $x + 1$ não pode ser negativo (por causa da raiz) e **também não pode ser zero** (por estar embaixo da fração).
  * Então usamos apenas o sinal de **maior que zero ($> 0$)**:
    $$x + 1 > 0 \implies \mathbf{x > -1}$$
  * **Resposta a):** $D = \{x \in \mathbb{R} \mid x > -1\}$.

* **b) Cálculo de $f(1)$:**
  $$f(1) = \frac{1}{\sqrt{1 + 1}} = \frac{1}{\sqrt{2}} = \mathbf{\frac{\sqrt{2}}{2}}$$

* **c) Cálculo de $f(0)$:**
  $$f(0) = \frac{1}{\sqrt{0 + 1}} = \frac{1}{\sqrt{1}} = \frac{1}{1} = \mathbf{1}$$

---

### 📌 Exemplo 8 da Apostila (Função Composta $f(g(x))$ — Cai muito na APOL!)
> **Enunciado:** Temos as seguintes funções: $f(x) = 2x + 1$ e $g(x) = x^3 - 2$. Determine a função composta $f(g(x))$.

**👨‍🏫 Explicação Passo a Passo (Sem complicação!):**
* O que significa **$f(g(x))$**? Significa pegar a fórmula inteira da função **$g(x)$** e colocá-la **dentro do lugar da letra $x$** da função **$f$**!
1. Escreva a função de fora ($f$):
   $$f(\text{entrada}) = 2 \cdot (\text{entrada}) + 1$$
2. Quem é a entrada agora? É a função $g(x) = x^3 - 2$. Então colocamos $(x^3 - 2)$ no lugar da entrada:
   $$f(g(x)) = 2 \cdot (x^3 - 2) + 1$$
3. Fazemos a multiplicação (chuveirinho) do $2$ por quem está dentro dos parênteses ($2 \cdot x^3 = 2x^3$ e $2 \cdot (-2) = -4$):
   $$f(g(x)) = 2x^3 - 4 + 1$$
4. Juntamos os números finais ($-4 + 1 = -3$):
   $$\mathbf{f(g(x)) = 2x^3 - 3}$$

---

## 🔹 TEMA 5: Interpretação Gráfica (Exemplo 9 da Apostila)

> **Enunciado:** Seguindo o Exemplo 1 (empresa que produz a peça $x$ com custo unitário de $\text{R\$ } 2\text{,00}$ e custo fixo de $\text{R\$ } 1.000\text{,00}$, cuja função é $f(x) = 2x + 1000$), como construímos o gráfico?

**👨‍🏫 Explicação Passo a Passo:**
Para desenhar qualquer reta no gráfico, só precisamos escolher **2 valores para $x$** (por exemplo, $x = 0$ e $x = 500$ peças):
1. Quando **$x = 0$ peças** (fábrica parada):
   $$y = 2(0) + 1000 = 1000 \implies \text{Ponto } A = (0, 1000)$$
2. Quando **$x = 500$ peças**:
   $$y = 2(500) + 1000 = 1000 + 1000 = 2000 \implies \text{Ponto } B = (500, 2000)$$
3. No gráfico:
   * O eixo horizontal ($x$, Domínio) começa em $0$ (não existe quantidade negativa de peças fabricadas: $x \ge 0$).
   * O eixo vertical ($y$, Imagem/Custo) começa em $\text{R\$ } 1.000\text{,00}$ e sobe em linha reta passando por $(500, 2000)$.

---

## 🏆 RESOLUÇÃO DETALHADA DOS 10 EXERCÍCIOS PROPOSTOS DA AULA 01

Aqui estão todos os 10 exercícios do final da Aula 01 resolvidos passo a passo:

### Exercício 01:
> **Calcule o domínio da função fracionária:** $f(x) = \frac{x^2 + 5x + 6}{x^2 - 4}$
* **Passo 1:** Na fração, a parte de cima não importa para o domínio; apenas a **parte de baixo não pode ser zero**:
  $$x^2 - 4 \neq 0$$
* **Passo 2:** Passamos o $-4$ para o outro lado como $+4$:
  $$x^2 \neq 4$$
* **Passo 3:** Tiramos a raiz quadrada dos dois lados (lembrando que tanto $(+2)^2$ quanto $(-2)^2$ dão $4$!):
  $$x \neq \pm\sqrt{4} \implies \mathbf{x \neq 2 \text{ e } x \neq -2}$$

### Exercício 02:
> **Qual é o domínio da função:** $f(x) = \sqrt{2x - 14}$
* **Passo 1:** Raiz quadrada exige que o interior seja $\ge 0$:
  $$2x - 14 \ge 0$$
* **Passo 2:** Passamos o $-14$ para a direita como $+14$:
  $$2x \ge 14$$
* **Passo 3:** O $2$ que está multiplicando passa dividindo:
  $$x \ge \frac{14}{2} \implies \mathbf{x \ge 7}$$

### Exercício 03:
> **Dada a função $f(x) = \sqrt[3]{x - 3}$, responda:**  
> **a) Domínio:** Como a raiz é cúbica (índice $3$, ímpar), aceita qualquer número real: **$D = \mathbb{R}$**.  
> **b) $f(4)$:** $f(4) = \sqrt[3]{4 - 3} = \sqrt[3]{1} = \mathbf{1}$.  
> **c) $f(-5)$:** $f(-5) = \sqrt[3]{-5 - 3} = \sqrt[3]{-8} = \mathbf{-2}$ (pois $(-2)^3 = -8$).

### Exercício 04:
> **Dada a função $f(x) = \frac{1}{\sqrt{x - 1}}$, responda:**  
> **a) Domínio:** Raiz quadrada no denominador exige interior estritamente maior que zero: $x - 1 > 0 \implies \mathbf{x > 1}$.  
> **b) $f(2)$:** $f(2) = \frac{1}{\sqrt{2 - 1}} = \frac{1}{\sqrt{1}} = \mathbf{1}$.  
> **c) $f(-2)$:** $f(-2) = \frac{1}{\sqrt{-2 - 1}} = \frac{1}{\sqrt{-3}} \implies$ **Não existe nos Números Reais ($\nexists \in \mathbb{R}$)**, pois $-2$ está fora do domínio ($x > 1$)!

### Exercício 05:
> **Dada a função $f(x) = x + 1$, responda:**  
> **a) Domínio:** $D = \mathbb{R}$ (não tem fração nem raiz).  
> **b) $f(1)$:** $1 + 1 = \mathbf{2}$.  
> **c) $f(-3)$:** $-3 + 1 = \mathbf{-2}$.  
> **d) $f(0)$:** $0 + 1 = \mathbf{1}$.  
> **e) $f\left(\frac{1}{5}\right)$:** $\frac{1}{5} + 1 = \frac{1}{5} + \frac{5}{5} = \mathbf{\frac{6}{5}}$ (ou $1\text{,2}$).

### Exercício 06:
> **Sendo $f(x) = x - 1$ e $g(x) = x^3 - 1$, determine a composta $f(g(x))$:**
* Colocamos $g(x)$ no lugar do $x$ da função $f$:
  $$f(g(x)) = (x^3 - 1) - 1 = \mathbf{x^3 - 2}$$

### Exercício 07:
> **Sendo $f(x) = 2x + 1$ e $g(x) = 3x - 2$, determine a composta $g(f(x))$:**
* Atenção à ordem! Agora quem está por fora é a função **$g$**, então colocamos $f(x)$ dentro do $x$ da função $g$:
  $$g(f(x)) = 3 \cdot (2x + 1) - 2$$
* Multiplicamos o $3$ pelo parêntese ($3 \cdot 2x = 6x$ e $3 \cdot 1 = 3$):
  $$g(f(x)) = 6x + 3 - 2 = \mathbf{6x + 1}$$

### Exercício 08:
> **Sabendo que $f(x) = \frac{4x}{3x}$ (ou $4x^3 \cdot x$), qual o valor de $f(2)$?**
* Na apostila a expressão aparece como potência/produto $4 \cdot 2^3 \cdot 2$ ou fração:
  * Se for $f(x) = 4x^3$: $f(2) = 4 \cdot (2^3) = 4 \cdot 8 = \mathbf{32}$.
  * Se for $f(x) = 4 \cdot x^{3x}$ para $x=2$: $4 \cdot 2^{6} = 4 \cdot 64 = \mathbf{256}$.

### Exercício 09 (ENEM 2017 — Proporcionalidade Direta):
> **Enunciado:** Para uma TV de $32$ polegadas, a distância ideal é de $1\text{,8 metro}$. Qual é a distância ideal para uma TV de $60$ polegadas?
* **Passo 1:** Montamos a regra de três direta:
  $$\frac{32\text{ pol}}{60\text{ pol}} = \frac{1\text{,8 m}}{x}$$
* **Passo 2:** Multiplicamos cruzado:
  $$32 \cdot x = 60 \cdot 1\text{,8}$$
  $$32x = 108$$
* **Passo 3:** Dividimos $108$ por $32$:
  $$x = \frac{108}{32} = \mathbf{3\text{,375 metros}} \implies \text{Alternativa }\mathbf{d)\text{ }3\text{,37}}$$

### Exercício 10 (ENEM 2012 — Economia de Água):
> **Enunciado:** Uma bacia antiga gasta $15\text{ litros}$ por descarga e consome $60\text{ litros por dia}$. A nova bacia ecológica gasta $6\text{ litros}$ por descarga. Qual será a **economia diária** de água?
* **Passo 1:** Descobrir quantas descargas são dadas por dia:
  * Se gasta $60\text{ litros}$ no dia e cada descarga antiga consome $15\text{ litros}$: $60 \div 15 = \mathbf{4\text{ descargas por dia}}$.
* **Passo 2:** Calcular quanto a bacia ecológica vai gastar nessas $4$ descargas:
  * $4 \times 6\text{ litros} = \mathbf{24\text{ litros por dia}}$.
* **Passo 3:** Calcular a **economia** (o que gastava antes menos o que gasta agora):
  * $\text{Economia} = 60 - 24 = \mathbf{36\text{ litros por dia}} \implies \text{Alternativa }\mathbf{b)\text{ }36\text{ litros}}$.
*(Cuidado para não marcar 24 litros! 24 é o consumo novo; a pergunta pede a economia: $60 - 24 = 36$!)*

---

# 🟩 AULA 02 COMPLETA — FUNÇÕES LINEARES, QUADRÁTICAS E POLINOMIAIS

## 🔹 TEMA 1 e 2: Função Linear / Afim ($f(x) = ax + b$)
* **Exemplo 1 da Apostila (Reservatório de $2.000\text{ L}$, $2$ moradores gastando $120\text{ L}$ cada um por dia):**
  * Consumo diário total = $2 \times 120 = 240\text{ litros por dia}$.
  * Como a água está *saindo* do reservatório de $2.000\text{ L}$, a taxa $a$ é negativa ($-240$ por dia $x$):
    $$V(x) = 2000 - 240x$$
* **Exemplo 2 da Apostila (Achar a função sabendo que $f(1) = 4$ e $f(2) = 6$):**
  * Como $f(x) = ax + b$:
    * Quando $x = 1$, o resultado é $4$: $1a + b = 4$
    * Quando $x = 2$, o resultado é $6$: $2a + b = 6$
  * Fazendo a segunda linha menos a primeira: $(2a - 1a) + (b - b) = 6 - 4 \implies \mathbf{a = 2}$.
  * Substituindo $a = 2$ na primeira linha: $2 + b = 4 \implies b = 4 - 2 \implies \mathbf{b = 2}$.
  * **Função pronta:** $\mathbf{f(x) = 2x + 2}$.

## 🔹 TEMA 3 e 4: Função Quadrática ($f(x) = ax^2 + bx + c$) e Lucro Máximo
* **Forma Fatorada:** Quando conhecemos as duas raízes $x_1$ e $x_2$, podemos escrever a função como:
  $$f(x) = a \cdot (x - x_1) \cdot (x - x_2)$$
* **Exemplo 9 da Apostila (ENEM 2013 — Lucro Máximo dos Bonés):**
  * Expressão do lucro: $L(x) = -x^2 + 12x - 20$ (onde $a = -1$, $b = 12$, $c = -20$).
  * Quando a questão pede a **quantidade $x$ que gera o Lucro Máximo** (o topo da parábola, chamado **Vértice $x_v$**), usamos a fórmula rápida do $x$ do vértice:
    $$x_v = \frac{-b}{2a}$$
  * Substituindo $b = 12$ e $a = -1$:
    $$x_v = \frac{-12}{2 \cdot (-1)} = \frac{-12}{-2} = \mathbf{6\text{ bonés}} \quad (\text{Alternativa b})$$
* **Exemplo 10 da Apostila (Área máxima de um terreno retangular com perímetro de $100\text{ m}$):**
  * Perímetro é a soma dos 4 lados: $2x + 2y = 100 \implies x + y = 50 \implies y = 50 - x$.
  * A área é base vezes altura: $A(x) = x \cdot y = x \cdot (50 - x) = -x^2 + 50x$.
  * O lado que dá a área máxima é o vértice: $x_v = \frac{-50}{2(-1)} = 25\text{ m}$.
  * Logo, a área máxima é $25\text{ m} \times 25\text{ m} = \mathbf{625\text{ m}^2}$.

## 🔹 TEMA 5: Produtos Notáveis e Polinômios de 3º Grau
* **3 Produtos Notáveis Obrigatórios:**
  1. **Quadrado da soma:** $(a + b)^2 = a^2 + 2ab + b^2$
  2. **Quadrado da diferença:** $(a - b)^2 = a^2 - 2ab + b^2$
  3. **Produto da soma pela diferença:** $(a - b)(a + b) = a^2 - b^2$
* **Exemplo 12 da Apostila (Raízes de $f(x) = x^3 - x$):**
  * Igualamos a zero e colocamos o $x$ em evidência:
    $$x^3 - x = 0 \implies x \cdot (x^2 - 1) = 0$$
  * Daí saem as 3 raízes: $x_1 = 0$ e $x^2 - 1 = 0 \implies x^2 = 1 \implies x = \pm 1$.
  * **Raízes:** $\{-1, 0, 1\}$.

---

# 🟨 AULA 03 COMPLETA — FUNÇÕES EXPONENCIAIS E LOGARÍTMICAS

* **Exemplo 1 da Apostila (Meia-vida de substância: $1200\text{ mg}$ cai pela metade a cada hora, após $6\text{ horas}$):**
  * A cada hora dividimos por $2$ (ou multiplicamos por $\frac{1}{2}$):
    $$f(t) = 1200 \cdot \left(\frac{1}{2}\right)^t$$
  * Para $t = 6\text{ horas}$: $\left(\frac{1}{2}\right)^6 = \frac{1}{64}$.
  * Conta: $1200 \div 64 = \mathbf{18\text{,75 mg}}$.
* **Exemplo 5 da Apostila (Escala Richter: diferença entre terremoto grau 7 e grau 5):**
  * Como a escala Richter é logarítmica de base $10$, cada ponto a mais multiplica a intensidade por $10$:
    $$\frac{S_7}{S_5} = 10^{7 - 5} = 10^2 = \mathbf{100\text{ vezes mais intenso!}}$$
* **Exemplo 8 da Apostila (Juros Compostos: $\text{R\$ } 1.000\text{,00}$ a $1\%\text{ a.m.}$ por $12\text{ meses}$):**
  * Fórmula: $M = C \cdot (1 + i)^n$, onde $C = 1000$, $i = 1\% = 0\text{,01}$ e $n = 12$:
    $$M = 1000 \cdot (1 + 0\text{,01})^{12} = 1000 \cdot (1\text{,01})^{12} \approx 1000 \cdot 1\text{,1268} = \mathbf{\text{R\$ } 1.126\text{,83}}$$

---

# 🟧 AULAS 04 e 05 COMPLETAS — TRIGONOMETRIA (PARTES 1 E 2)

* **Exemplo 5 da Aula 4 (Pizza de $40\text{ cm}$ de diâmetro cortada em $12$ fatias):**
  * O diâmetro é $40\text{ cm}$, logo o **raio ($r$)** é a metade: **$r = 20\text{ cm}$**.
  * **a) Ângulo de cada fatia:** O círculo inteiro tem $360^\circ$. Dividindo por $12$: $360^\circ \div 12 = \mathbf{30^\circ}$ por fatia.
  * **b) Área total da pizza ($A = \pi \cdot r^2$):** $A = 3\text{,14} \times 20^2 = 3\text{,14} \times 400 = \mathbf{1.256\text{ cm}^2}$.
  * **c) Área de 1 fatia:** $1.256 \div 12 = \mathbf{104\text{,67 cm}^2}$.
* **Exemplo 6 da Aula 4 (Roda de bicicleta com raio $r = 290\text{ mm} = 0\text{,29 m}$):**
  * **a) Distância de 1 volta (Comprimento da circunferência $C = 2 \cdot \pi \cdot r$):**
    $$C = 2 \times 3\text{,14} \times 0\text{,29 m} = \mathbf{1\text{,8212 metros por volta}}$$
  * **b) Quantas voltas em $5\text{ km}$ ($5.000\text{ metros}$):**
    $$\text{Voltas} = 5.000 \div 1\text{,8212} \approx \mathbf{2.745\text{ voltas}}$$
* **Funções Inversas na Aula 5 (Cossecante, Secante e Cotangente):**
  * **Cossecante ($\csc$):** É o inverso do **Seno** ($\csc x = \frac{1}{\text{sen } x}$). *(Dica: **Co**ssecante inverte o **Se**no — trocam as iniciais!).*
  * **Secante ($\sec$):** É o inverso do **Cosseno** ($\sec x = \frac{1}{\cos x}$).
  * **Cotangente ($\text{cotg}$):** É o inverso da **Tangente** ($\text{cotg } x = \frac{1}{\text{tg } x} = \frac{\cos x}{\text{sen } x}$).

---

# 🟪 AULA 06 COMPLETA — SISTEMAS LINEARES, MATRIZES E DETERMINANTES

* **Operações com Matrizes (Exemplo 8 da Apostila):**
  * **Soma ($A + B$) e Subtração ($A - B$):** Basta somar ou diminuir os números que estão na **mesma posição** (canto superior esquerdo com canto superior esquerdo, etc.).
  * **Multiplicação ($A \times B$):** Multiplica **Linha da primeira por Coluna da segunda**!
* **Determinante de 3ª Ordem ($3 \times 3$ — Regra de Sarrus):**
  1. Copie as duas primeiras colunas ao lado direito da matriz.
  2. Multiplique as 3 diagonais que descem para a direita ($\searrow$) e some os resultados.
  3. Multiplique as 3 diagonais que descem para a esquerda ($\swarrow$) e subtraia os resultados.
* **Exercício 09 da Aula 6 (UFMT — Matriz de Temperaturas no Carnaval):**
  * Na matriz $A$, as **linhas ($i$)** são os momentos ($1^\circ, 2^\circ, 3^\circ$) e as **colunas ($j$)** são os dias ($1^\circ, 2^\circ, 3^\circ, 4^\circ$).
  * O maior número da tabela é **$40\text{,3}^\circ\text{C}$**, que está na **2ª linha** (2º momento) e **1ª ou 2ª coluna** conforme o enunciado original.
* **Exercício 10 da Aula 6 (Orçamento dos Combos A, B e C):**
  * Montamos o sistema:
    $$\begin{cases} 2A + 3B + 2C = 1050 \\ 3A + 1B + 1C = 650 \\ 0A + 2B + 3C = 900 \end{cases}$$
  * Resolvendo o sistema: encontramos **$A = \text{R\$ } 100\text{,00}$**, **$B = \text{R\$ } 150\text{,00}$** e **$C = \text{R\$ } 200\text{,00}$**!
    * Prova real no Combo 1: $2(100) + 3(150) + 2(200) = 200 + 450 + 400 = \text{R\$ } 1.050\text{,00}$!
    * Prova real no Combo 2: $3(100) + 1(150) + 1(200) = 300 + 150 + 200 = \text{R\$ } 650\text{,00}$!
    * Prova real no Combo 3: $0(100) + 2(150) + 3(200) = 0 + 300 + 600 = \text{R\$ } 900\text{,00}$!
