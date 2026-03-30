import random
import time
import os
from google import genai
from dotenv import load_dotenv

# 1. Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

print("Testando a nova branch")

# 2. Puxa a chave de forma segura
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Função para imprimir o quadro
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
todos_erros = [] # Guarda os erros para a IA analisar depois

print("\nSejam bem-vindos ao sistema de telemetria da Missão Aurora!")
print("Iniciando sequência de 3 testes obrigatórios...\n")

while quantidade_testes < 3:    
    erros = []
    quantidade_testes += 1
    
    # Simulação de telemetria 
    temp_interna = random.uniform(10, 35)
    temp_externa = random.uniform(-50, 50)
    integridade_estrutural = random.choice([0, 1]) 
    nivel_energia = random.uniform(0, 100)
    pressao = random.uniform(250, 550)
    modulos_criticos = random.choice(["OK", "FALHA"])

    # Verificações de segurança 
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

    # Processamento do teste individual
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
            todos_erros.append(erro)

    imprimir_quadro(f"RELATÓRIO DE RODADA: {quantidade_testes}/3", [status_individual, info, "-" * 61] + conteudo_relatorio)

# Decisão Final da Missão 
print("\n" + "="*65)
print(f"RESUMO FINAL: {testes_sucessos} Sucessos | {testes_falhas} Falhas")

# Montando o prompt dinâmico para a IA baseando-se nos resultados reais
if testes_sucessos == 3:
    print(">>> STATUS FINAL: PRONTO PARA DECOLAR! 🚀")
    print("Todos os testes foram aprovados. Iniciando contagem de ignição...\n") 
    prompt_ia = "Aja como um engenheiro de voo sênior. O foguete Aurora passou nos 3 testes de telemetria com 100% de sucesso. Escreva um breve relatório de duas linhas parabenizando a equipe e autorizando o lançamento em português do Brasil."
else:
    print(">>> STATUS FINAL: DECOLAGEM ABORTADA! ❌")
    print(f"A missão requer 3 sucessos consecutivos. Detectamos {testes_falhas} falha(s).")
    print(f"{time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} - A equipe de engenharia está investigando as falhas.\n")
    
    # Passa a lista de erros reais para o Gemini explicar
    erros_formatados = ", ".join(set(todos_erros))
    prompt_ia = f"Aja como um engenheiro de voo sênior. O lançamento do foguete Aurora foi abortado pois falhou em {testes_falhas} de 3 testes. As anomalias detectadas foram: {erros_formatados}. Em português do Brasil, explique de forma técnica e concisa por que essas anomalias impedem o lançamento e o que a equipe deve investigar."

# 3. Chamada da IA com o contexto correto
# 3. Chamada da IA com o contexto correto e Lógica de Retentativa (Retry)
print("--- ANÁLISE DO DIRETOR DE VOO (IA) ---")
print("Conectando aos servidores de IA...\n")

tentativas_maximas = 3
sucesso_ia = False

for tentativa in range(1, tentativas_maximas + 1):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt_ia
        )
        print(response.text)
        sucesso_ia = True
        break 
        
    except Exception as e:
        erro_str = str(e)
        if "503" in erro_str:
            print(f"[Aviso] Servidor ocupado (Tentativa {tentativa}/{tentativas_maximas}). Aguardando 5 segundos para tentar novamente...")
            time.sleep(5) # Espera 5 segundos antes de tentar de novo
        else:
            print(f"Falha inesperada na comunicação com a IA: {e}")
            break 
if not sucesso_ia:
    print("A análise de IA não pôde ser gerada no momento devido à alta demanda da rede. Por favor, tente novamente mais tarde.")
    
print("="*65)