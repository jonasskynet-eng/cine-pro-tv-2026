# -*- coding: utf-8 -*-
"""
MÓDULO COMERCIAL DE ANÁLISE DE COORTES DE RETENÇÃO (COHORT RETENTION ENGINE)
Autor: Jonas / Antigravity
Finalidade: Calcular a taxa de retenção mês a mês de safras de clientes/usuários
Zero dependências obrigatórias: Funciona 100% em Python puro (Standard Library)
"""

import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

def gerar_dados_amostra(num_usuarios=600, total_eventos=4000):
    """
    Gera conjunto sintético realista de eventos ao longo de 12 meses.
    """
    random.seed(42)
    start_date = datetime(2025, 1, 1)
    
    # 1. Atribui uma data inicial para cada usuário
    user_start = {}
    for i in range(1, num_usuarios + 1):
        u_id = f"USR_{i:04d}"
        dias_inicio = random.randint(0, 240)
        user_start[u_id] = start_date + timedelta(days=dias_inicio)
        
    # 2. Gera compras/atividades posteriores
    registros = []
    user_list = list(user_start.keys())
    
    for _ in range(total_eventos):
        u = random.choice(user_list)
        base = user_start[u]
        # Decaimento: maior chance de atividade nos primeiros meses
        dias_offset = int(random.expovariate(1.0 / 55.0))
        data_evento = base + timedelta(days=dias_offset)
        registros.append({
            "user_id": u,
            "event_date": data_evento.strftime("%Y-%m-%d")
        })
        
    return registros

def calcular_matriz_coortes(registros):
    """
    Cálculo matemático puro das safras de retenção:
    - Identifica a menor data (mês de entrada) de cada cliente.
    - Calcula a diferença em meses para cada atividade subsequente.
    """
    # Descobre o mês de entrada (Safra) de cada usuário
    primeiro_mes_usuario = {}
    for r in registros:
        u = r["user_id"]
        ano_mes = r["event_date"][:7]  # 'YYYY-MM'
        if u not in primeiro_mes_usuario or ano_mes < primeiro_mes_usuario[u]:
            primeiro_mes_usuario[u] = ano_mes
            
    # Tamanho total de cada safra (Mês 0)
    tamanho_safras = defaultdict(set)
    for u, safra in primeiro_mes_usuario.items():
        tamanho_safras[safra].add(u)
        
    # Atividade por safra e índice de mês decorrido
    usuarios_ativos = defaultdict(lambda: defaultdict(set))
    max_indice = 0
    
    for r in registros:
        u = r["user_id"]
        safra = primeiro_mes_usuario[u]
        ano_mes_evento = r["event_date"][:7]
        
        ano_s, mes_s = int(safra[:4]), int(safra[5:7])
        ano_e, mes_e = int(ano_mes_evento[:4]), int(ano_mes_evento[5:7])
        
        diff_meses = (ano_e - ano_s) * 12 + (mes_e - mes_s)
        if diff_meses >= 0:
            usuarios_ativos[safra][diff_meses].add(u)
            if diff_meses > max_indice:
                max_indice = diff_meses
                
    # Limita a visualização a até 8 períodos para legibilidade
    max_indice = min(max_indice, 7)
    
    return primeiro_mes_usuario, tamanho_safras, usuarios_ativos, max_indice

def exportar_relatorio_csv(tamanho_safras, usuarios_ativos, max_indice, nome_arquivo="relatorio_retencao_cohort.csv"):
    """
    Exporta a matriz de retenção percentual e volumétrica para arquivo CSV.
    """
    safras_ordenadas = sorted(tamanho_safras.keys())
    
    with open(nome_arquivo, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        
        # Cabeçalho
        header = ["Safra (Coorte)", "Tamanho Safra"] + [f"Mes {i} (%)" for i in range(max_indice + 1)]
        writer.writerow(header)
        
        for safra in safras_ordenadas:
            total_safra = len(tamanho_safras[safra])
            linha = [safra, total_safra]
            
            for i in range(max_indice + 1):
                ativos = len(usuarios_ativos[safra][i])
                pct = (ativos / total_safra * 100.0) if total_safra > 0 else 0.0
                linha.append(f"{pct:.2f}%")
                
            writer.writerow(linha)
            
    print(f"-> Relatorio CSV exportado com sucesso: {nome_arquivo}")

def exibir_tabela_terminal(tamanho_safras, usuarios_ativos, max_indice):
    """
    Exibe a tabela formatada com alinhamento visual no terminal.
    """
    safras_ordenadas = sorted(tamanho_safras.keys())
    
    print("\n" + "=" * 95)
    print("MATRIZ DE RETENÇÃO DE COORTES (%) - SAFRAS DE USUÁRIOS".center(95))
    print("=" * 95)
    
    # Cabeçalho
    header_str = f"{'Safra':<10} | {'Base':<6} | " + " | ".join([f"{'Mês '+str(i):<8}" for i in range(max_indice + 1)])
    print(header_str)
    print("-" * 95)
    
    for safra in safras_ordenadas:
        total_safra = len(tamanho_safras[safra])
        colunas = []
        for i in range(max_indice + 1):
            ativos = len(usuarios_ativos[safra][i])
            pct = (ativos / total_safra * 100.0) if total_safra > 0 else 0.0
            colunas.append(f"{pct:>6.1f}%")
        linha_str = f"{safra:<10} | {total_safra:<6} | " + " | ".join([f"{c:<8}" for c in colunas])
        print(linha_str)
        
    print("=" * 95)

def main():
    print("Gerando dados e calculando retencao de safras...")
    registros = gerar_dados_amostra()
    primeiro_mes, tamanho_safras, usuarios_ativos, max_indice = calcular_matriz_coortes(registros)
    
    exibir_tabela_terminal(tamanho_safras, usuarios_ativos, max_indice)
    exportar_relatorio_csv(tamanho_safras, usuarios_ativos, max_indice)

if __name__ == "__main__":
    main()
