import random

# Função para imprimir o quadro conforme especificações do projeto 
def imprimir_quadro(titulo, linhas):
    largura = 65
    print("-" * largura)
    print(f"| {titulo.center(largura - 4)} |")
    print("|" + " " * (largura - 2) + "|")
    for linha in linhas:
        print(f"| {linha.ljust(largura - 4)} |")
    print("|" + " " * (largura - 2) + "|")
    print("-" * largura)

quantidade_testes = 0
testes_sucessos = 0
testes_falhas = 0

print("\nSejam bem-vindos ao sistema de telemetria da Missão Aurora!")
print("Iniciando sequência de 3 testes obrigatórios...\n")

while quantidade_testes < 3:    
    erros = []
    quantidade_testes += 1
    
    # 1. Simulação de telemetria 
    temp_interna = random.uniform(10, 35)
    temp_externa = random.uniform(-50, 50)
    integridade_estrutural = random.choice([0, 1]) 
    nivel_energia = random.uniform(0, 100)
    pressao = random.uniform(250, 550)
    modulos_criticos = random.choice(["OK", "FALHA"])

    # 2. Verificações de segurança baseadas nas faixas seguras 
    if integridade_estrutural == 0:
        erros.append("FALHA NA INTEGRIDADE ESTRUTURAL")
    if nivel_energia < 80:
        erros.append(f"Energia insuficiente: {nivel_energia:.2f}% (Min: 80%)")
    if pressao < 300 or pressao > 450:
        erros.append(f"Pressão fora dos padrões: {pressao:.2f} psi")
    if temp_interna < 18 or temp_interna > 25:
        erros.append(f"Temperatura interna fora do padrão: {temp_interna:.2f} C°")
    if modulos_criticos == "FALHA":
        erros.append("FALHA NOS MÓDULOS CRÍTICOS")

    # 3. Processamento do resultado do teste individual
    conteudo_relatorio = []
    if not erros:
        testes_sucessos += 1
        status_individual = "TESTE BEM-SUCEDIDO"
        info = f"Rodada {quantidade_testes}: Parâmetros nominais."
        conteudo_relatorio.extend([
            f"Temp. Interna: {temp_interna:.2f} C°",
            f"Integridade: OK",
            f"Energia: {nivel_energia:.2f}%",
            f"Pressão: {pressao:.2f} psi"
        ])
    else:
        testes_falhas += 1
        status_individual = "TESTE FALHOU"
        info = f"Rodada {quantidade_testes}: Anomalias detectadas."
        conteudo_relatorio.append("ERROS ENCONTRADOS:")
        for erro in erros:
            conteudo_relatorio.append(f"- {erro}")

    # Impressão do quadro da rodada atual
    imprimir_quadro(f"RELATÓRIO DE RODADA: {quantidade_testes}/3", [status_individual, info, "-" * 61] + conteudo_relatorio)

# 4. Decisão Final da Missão 
print("\n" + "="*65)
print(f"RESUMO FINAL: {testes_sucessos} Sucessos | {testes_falhas} Falhas")

if testes_sucessos == 3:
    print(">>> STATUS FINAL: PRONTO PARA DECOLAR! 🚀")
    print("Todos os testes foram aprovados. Iniciando contagem de ignição...") 
else:
    print(">>> STATUS FINAL: DECOLAGEM ABORTADA! ❌")
    print(f"A missão requer 3 sucessos consecutivos. Detectamos {testes_falhas} falha(s).")
print("="*65)