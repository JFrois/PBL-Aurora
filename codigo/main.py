import random

erros=[]

temperatura_interna = random.uniform(-50,50)
temperatura_externa = random.uniform(-50,50)
integridade_estrutural = random.choice([0,1]) 
nivel_energia = (random.randint(0,100)/100)*5000
pressao = random.uniform(300,500)
modulosCriticos = random.choice(["OK","FALHA"])

if integridade_estrutural == 0:
    erros.append("FALHA NA INTEGRIDADE ESTRUTURAL")
if nivel_energia < 80:
    erros.append(f"Energia insuficiente: {nivel_energia}% (Mínimo: 80%)")
if pressao < 300 or pressao > 450:
    erros.append(f"Pressão fora dos padrões: {pressao} psi")
if temperatura_interna < 18 or temperatura_interna > 25:
    erros.append(f"Temperatura interna fora do padrão: {temperatura_interna} C°")
if modulosCriticos == "FALHA":
    erros.append("FALHA NOs MODULOS CRÍTICOS")

if not erros:
    print("--- RELATÓRIO OPERACIONAL ---")
    print("STATUS: PRONTO PARA DECOLAR!")
else:
    print("--- RELATÓRIO OPERACIONAL ---")
    print("STATUS: DECOLAGEM ABORTADA!")
    print("MOTIVOS:")
    for erro in erros:
        print(f"- {erro}")
