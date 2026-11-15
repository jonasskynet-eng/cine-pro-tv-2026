# ==============================================================================
# UNINTER — LÓGICA DE PROGRAMAÇÃO E ALGORITMOS (2025/2026)
# EXERCÍCIO 1 — APP DE VENDAS NO ATACADO COM DESCONTO
# Aluno: Jonas Mendonça
# ==============================================================================

# Exigência A e G: Mensagem de boas-vindas com o nome e sobrenome do aluno
print("Bem-vindo a Loja do Jonas Mendonça")

# Exigência B: Input do valor unitário do produto e da quantidade
valor_unitario = float(input("Entre com o valor do produto: "))
quantidade = int(input("Entre com a quantidade do produto: "))

# Exigência D: Cálculo do valor total sem desconto
valor_total_sem_desconto = valor_unitario * quantidade

# Exigência C e E: Estruturas condicionais completas (if, elif, else)
# Conforme a tabela de faixas de compras da empresa:
if valor_total_sem_desconto < 2500:
    desconto = 0.00  # 0% de desconto
elif valor_total_sem_desconto < 6000:
    desconto = 0.04  # 4% de desconto (para valores entre 2500 e 5999.99)
elif valor_total_sem_desconto < 10000:
    desconto = 0.07  # 7% de desconto (para valores entre 6000 e 9999.99)
else:
    desconto = 0.11  # 11% de desconto (para valores a partir de 10000)

# Cálculo do valor final com desconto aplicado
valor_total_com_desconto = valor_total_sem_desconto - (valor_total_sem_desconto * desconto)

# Exigência D: Exibição dos resultados no console formatados com duas casas decimais (:.2f)
print(f"O valor SEM desconto: R${valor_total_sem_desconto:.2f}")
print(f"O valor COM desconto: R${valor_total_com_desconto:.2f}")
