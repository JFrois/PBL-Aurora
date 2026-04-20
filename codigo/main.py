import random
import time
import os
from dotenv import load_dotenv
from google import genai

# 1. Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# Função para imprimir o quadro
def imprimir_quadro(titulo, linhas):
    largura = 85
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
todos_erros = [] # Guarda os erros para a IA analisar depois

print("\n" + "="*85)
print("Sejam bem-vindos ao sistema de telemetria da MISSÃO AURORA".center(85))
print("Iniciando sequência de 3 testes obrigatórios...".center(85))
print("="*85 + "\n")


# ---> 2
while quantidade_testes < 3:
    erros = []
    quantidade_testes += 1

    # --- Simulação de telemetria ---
    temp_interna = random.uniform(10, 35)
    temp_externa = random.uniform(-30, 50)
    integridade_estrutural = random.choice([0, 1])
    capacidade_energia_kwh = random.uniform(1000, 5000)
    carga_energia_pct = random.uniform(0, 100)
    consumo_energia_est = random.uniform(200, 500)
    perdas_energia = random.uniform(10, 50)
    pressao = random.uniform(250, 550)
    modulos_criticos = random.choice(["OK", "FALHA"])

    # --- Processamento da Análise Energética ---
    #Energia disponível antes da decolagem
    energia_bruta_kwh = capacidade_energia_kwh * (carga_energia_pct / 100)

    #Energia restante após decolagem (considerando perdas)
    energia_restante_kwh = energia_bruta_kwh - perdas_energia - consumo_energia_est

    #Autonomia residual em %
    saldo_pos_decolagem_pct = max(0, (energia_restante_kwh / capacidade_energia_kwh) * 100)



    # --- Verificações de segurança ---
    if integridade_estrutural == 0:
        erros.append("FALHA NA INTEGRIDADE ESTRUTURAL")
    if pressao < 300 or pressao > 450:
        erros.append(f"Pressão fora dos padrões: {pressao:.2f} psi")
    if temp_interna < 18 or temp_interna > 25:
        erros.append(f"Temperatura interna fora do padrão: {temp_interna:.2f} C°")
    if temp_externa < 5 or temp_externa > 38:
        erros.append(f"Temperatura externa fora do padrão: {temp_externa:.2f} C°")
    if modulos_criticos == "FALHA":
        erros.append("FALHA NOS MÓDULOS CRÍTICOS")
    if saldo_pos_decolagem_pct < 80:
        erros.append(f"RISCO DE BLACKOUT: Saldo de {saldo_pos_decolagem_pct:.2f}% (Min: 80%)")


    # Processamento do teste individual
    conteudo_relatorio = [

        "VERIFICAÇÃO DE SEGURANÇA:",
        f"  > Bateria Útil p/ Sistema: {max(0, energia_restante_kwh):.2f} kWh",
        f"  > Custo de Decolagem.....: {consumo_energia_est:.2f} kWh",
        f"  > Autonomia energética pós decolagem...: {saldo_pos_decolagem_pct:.2f}%",
        f"  > Temp. Interna: {temp_interna:.2f} C°",
        f"  > Temp. Externa: {temp_externa:.2f} C°",
        f"  > Integridade: OK",
        f"  > Pressão: {pressao:.2f} psi"
    ]

    if not erros:
        testes_sucessos += 1
        status_individual = "TESTE BEM-SUCEDIDO"
        info = f"Rodada {quantidade_testes}: Parâmetros nominais."
    else:
        testes_falhas += 1
        status_individual = "TESTE FALHOU"
        info = f"Rodada {quantidade_testes}: Anomalias detectadas."
        conteudo_relatorio.append("-" * 65)
        conteudo_relatorio.append("ERROS ENCONTRADOS:")
        for erro in erros:
            conteudo_relatorio.append(f"- {erro}")
            todos_erros.append(erro)

    imprimir_quadro(
        f"RELATÓRIO DE RODADA: {quantidade_testes}/3",
        [status_individual, info, "-" * 61] + conteudo_relatorio
        )

# Decisão Final
print("" + "="*65)
print(f"RELATÓRIO DE RODADA: {testes_sucessos} Sucessos | {testes_falhas} Falhas")

if testes_falhas == 0:
    print("STATUS: AUTORIZADO PARA DECOLAGEM! 🚀")
else:
    print("STATUS: ABORTAR MISSÃO! Verifique os erros acima. 🛑")


# ---> 3
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")



if not api_key:
    print("Falha: variável GEMINI_API_KEY não encontrada no arquivo .env ou no ambiente.")
else:
    client = genai.Client(api_key=api_key)


# Initialize erros_formatadas to prevent NameError
erros_formatadas = ""

# Montando o prompt dinâmico para a IA baseando-se nos resultados reais
if testes_sucessos == 3:
    print(">>> STATUS FINAL: PRONTO PARA DECOLAR! 🚀")
    print("Todos os testes foram aprovados. Iniciando contagem de ignição...\n")
    prompt_ia = (
    f"Atue como Diretor de Voo Sênior da Missão Aurora. Todos os subsistemas estão nominais e"
    f"o foguete passou nos 3 testes críticos de telemetria de pré-lançamento com 100% de êxito. "
    f"Gere um comunicado oficial e técnico de no máximo três linhas em português do Brasil. "
    f"Na primeira linha, parabenize a equipe de engenharia pela estabilidade do sistema. "
    f"Na segunda linha, faça a classificação dos dados."
    f"Na terceira linha, declare 'GO FOR LAUNCH' e autorize formalmente o início da sequência de ignição."
) 
else:
    print(">>> STATUS FINAL: DECOLAGEM ABORTADA! ❌")
    print(f"A missão requer 3 sucessos consecutivos. Detectamos {testes_falhas} falha(s).")
    print(
            f"{time.localtime().tm_hour:02d}:"
            f"{time.localtime().tm_min:02d}:"
            f"{time.localtime().tm_sec:02d} - "
            "A equipe de engenharia está investigando as falhas.\n"
    )

    # Passa a lista de erros reais para o Gemini explicar
    erros_formatadas = ", ".join(sorted(set(todos_erros)))
    prompt_ia = (
    f"Atue como Diretor de Voo Sênior da Missão Aurora. Condição NO-GO. O lançamento foi "
    "Não precisa colocar data e nome do diretor."
    f"imediatamente abortado devido a falhas críticas em {testes_falhas} de 3 testes de verificação. "
    f"Anomalias registradas via telemetria: {erros_formatadas}. "
    f"Faça a classificação dos dados."
    f"Escreva um boletim técnico de diagnóstico curto em português do Brasil, estruturado da seguinte forma:\n"
    f"- STATUS: Confirme o aborto do lançamento.\n"
    f"- RISCO: Explique tecnicamente por que essas anomalias específicas causam risco de perda de veículo.\n"
    f"- AÇÃO: Defina o foco imediato de investigação para a equipe de engenharia de software e hardware."
)
#Chama IA com o contexto correto
print("--- ANÁLISE DO DIRETOR DE VOO (IA) ---")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_ia
    )
    print(response.text)
except Exception as e:
    print(f"Falha na comunicação com a IA: {e}")

print("="*65)    