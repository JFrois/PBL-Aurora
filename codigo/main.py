import random

erros = []

# Simulação de telemetria
temperatura_interna = random.uniform(-50, 50)
temperatura_externa = random.uniform(-50, 50)
integridade_estrutural = random.choice([0, 1]) 
# Ajuste na lógica de energia para refletir a porcentagem (0-100)
nivel_energia = random.uniform(0, 100)
pressao = random.uniform(300, 500)
modulosCriticos = random.choice(["OK", "FALHA"])

# Verificações baseadas nos requisitos do projeto
if integridade_estrutural == 0:
    erros.append("FALHA NA INTEGRIDADE ESTRUTURAL")
if nivel_energia < 80:
    erros.append(f"Energia insuficiente: {nivel_energia:.2f}%")
if pressao < 300 or pressao > 450:
    erros.append(f"Pressão fora dos padrões: {pressao:.2f} psi")
if temperatura_interna < 18 or temperatura_interna > 25:
    erros.append(f"Temperatura interna fora do padrão: {temperatura_interna:.2f} C°")
if modulosCriticos == "FALHA":
    erros.append("FALHA NOS MODULOS CRÍTICOS")

# Função para imprimir o quadro
def imprimir_quadro(titulo, linhas):
    largura = 60
    print("*" * largura)
    print(f"| {titulo.center(largura - 4)} |")
    print("|" + " " * (largura - 2) + "|")
    for linha in linhas:
        # Garante que cada linha caiba dentro do quadro com a barra lateral
        print(f"| {linha.ljust(largura - 4)} |")
    print("|" + " " * (largura - 2) + "|")
    print("*" * largura)

# Preparação dos dados para o quadro
conteudo_relatorio = []
if not erros:
    status = "STATUS: PRONTO PARA DECOLAR!"
    conteudo_relatorio.append(f"Temperatura Interna: {temperatura_interna:.2f} C°")
    conteudo_relatorio.append(f"Temperatura Externa: {temperatura_externa:.2f} C°")
    conteudo_relatorio.append(f"Integridade: {'OK' if integridade_estrutural == 1 else 'FALHA'}")
    conteudo_relatorio.append(f"Energia: {nivel_energia:.2f}%")
    conteudo_relatorio.append(f"Pressão: {pressao:.2f} psi")
    conteudo_relatorio.append(f"Módulos: {modulosCriticos}")
else:
    status = "STATUS: DECOLAGEM ABORTADA!"
    conteudo_relatorio.append("MOTIVOS DA FALHA:")
    for erro in erros:
        conteudo_relatorio.append(f"- {erro}")

# Execução da impressão
imprimir_quadro("RELATÓRIO OPERACIONAL - AURORA", [status] + ["-" * 56] + conteudo_relatorio)