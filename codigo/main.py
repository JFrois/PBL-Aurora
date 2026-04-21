import random
import time
import os
from dotenv import load_dotenv
from google import genai

# ==============================================================================
# CONFIGURAÇÃO GERAL
# ==============================================================================
# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()


def imprimir_quadro(titulo, linhas):
    """Função padrão para imprimir relatórios em formato de quadro."""
    largura = 85
    print("-" * largura)
    print(f"| {titulo.center(largura - 4)} |")
    print("|" + " " * (largura - 2) + "|")
    for linha in linhas:
        print(f"| {linha.ljust(largura - 4)} |")
    print("|" + " " * (largura - 2) + "|")
    print("-" * largura)


# ==============================================================================
# PROJETO AURORA SIGER - FASE 1: TELEMETRIA DE DECOLAGEM
# ==============================================================================
quantidade_testes = 0
testes_sucessos = 0
testes_falhas = 0
todos_erros = []  # Guarda os erros para a IA analisar depois

print("\n" + "=" * 85)
print("Sejam bem-vindos ao sistema de telemetria da MISSÃO AURORA".center(85))
print("Iniciando sequência de 3 testes obrigatórios...".center(85))
print("=" * 85 + "\n")

while quantidade_testes < 3:
    erros = []
    quantidade_testes += 1

    # --- Simulação de telemetria ---
    temp_interna = random.uniform(18, 25) # Ajustado para ser mais provável de estar dentro do padrão
    temp_externa = random.uniform(5, 38) # Ajustado para ser mais provável de estar dentro do padrão
    integridade_estrutural = random.choice([0, 1]) # Ajustado para ser mais provável de estar dentro do padrão
    capacidade_energia_kwh = random.uniform(1000, 5000) # Ajustado para ser mais provável de estar dentro do padrão
    carga_energia_pct = random.uniform(0, 100) # Ajustado para ser mais provável de estar dentro do padrão
    consumo_energia_est = random.uniform(200, 500) # Ajustado para ser mais provável de estar dentro do padrão
    perdas_energia = random.uniform(10, 50) # Ajustado para ser mais provável de estar dentro do padrão
    pressao = random.uniform(250, 550) # Ajustado para ser mais provável de estar dentro do padrão
    modulos_criticos = random.choice(["OK", "FALHA"])

    # --- Processamento da Análise Energética ---
    energia_bruta_kwh = capacidade_energia_kwh * (carga_energia_pct / 100)
    energia_restante_kwh = energia_bruta_kwh - perdas_energia - consumo_energia_est
    saldo_pos_decolagem_pct = max(
        0, (energia_restante_kwh / capacidade_energia_kwh) * 100
    )

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
        erros.append(
            f"RISCO DE BLACKOUT: Saldo de {saldo_pos_decolagem_pct:.2f}% (Min: 80%)"
        )

    # --- Processamento do teste individual ---
    conteudo_relatorio = [
        "VERIFICAÇÃO DE SEGURANÇA:",
        f"  > Bateria Útil p/ Sistema: {max(0, energia_restante_kwh):.2f} kWh",
        f"  > Custo de Decolagem.....: {consumo_energia_est:.2f} kWh",
        f"  > Autonomia energética pós decolagem...: {saldo_pos_decolagem_pct:.2f}%",
        f"  > Temp. Interna: {temp_interna:.2f} C°",
        f"  > Temp. Externa: {temp_externa:.2f} C°",
        f"  > Integridade: OK",
        f"  > Pressão: {pressao:.2f} psi",
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
        [status_individual, info, "-" * 61] + conteudo_relatorio,
    )

# --- Decisão Final Fase 1 ---
print("\n" + "=" * 85)
print(
    f"RELATÓRIO DE DECOLAGEM: {testes_sucessos} Sucessos | {testes_falhas} Falhas".center(
        85
    )
)

if testes_falhas == 0:
    print("STATUS: AUTORIZADO PARA DECOLAGEM! 🚀".center(85))
else:
    print("STATUS: ABORTAR MISSÃO! Verifique os erros acima. 🛑".center(85))

# --- Inteligência Artificial Fase 1 ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print(
        "\nFalha: variável GEMINI_API_KEY não encontrada no arquivo .env ou no ambiente."
    )
else:
    client = genai.Client(api_key=api_key)

if testes_sucessos == 3:
    print("\n>>> STATUS FINAL: PRONTO PARA DECOLAR! 🚀")
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
    print("\n>>> STATUS FINAL: DECOLAGEM ABORTADA! ❌")
    print(
        f"A missão requer 3 sucessos consecutivos. Detectamos {testes_falhas} falha(s)."
    )
    print(
        f"{time.localtime().tm_hour:02d}:{time.localtime().tm_min:02d}:{time.localtime().tm_sec:02d} - "
        "A equipe de engenharia está investigando as falhas.\n"
    )
    erros_formatadas = ", ".join(sorted(set(todos_erros)))
    prompt_ia = (
        f"Atue como Diretor de Voo Sênior da Missão Aurora. Condição NO-GO. O lançamento foi "
        f"imediatamente abortado devido a falhas críticas em {testes_falhas} de 3 testes de verificação. "
        f"Anomalias registradas via telemetria: {erros_formatadas}. "
        f"Faça a classificação dos dados."
        f"Escreva um boletim técnico de diagnóstico curto em português do Brasil, estruturado da seguinte forma:\n"
        f"- STATUS: Confirme o aborto do lançamento.\n"
        f"- RISCO: Explique tecnicamente por que essas anomalias específicas causam risco de perda de veículo.\n"
        f"- AÇÃO: Defina o foco imediato de investigação para a equipe de engenharia de software e hardware."
    )

print("--- ANÁLISE DO DIRETOR DE VOO (IA FASE 1) ---")
try:
    if api_key:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt_ia
        )
        print(response.text)
except Exception as e:
    print(f"Falha na comunicação com a IA: {e}")

print("=" * 85)


# ==============================================================================
# PROJETO AURORA SIGER - FASE 2: GERENCIAMENTO DE POUSO (MGPEB)
# ==============================================================================
print("\n" + "=" * 85)
print("INICIANDO FASE 2: APROXIMAÇÃO A MARTE E POUSO DE MÓDULOS".center(85))
print("=" * 85 + "\n")

fila_pouso = []
lista_pousados = []
lista_espera = []
pilha_alertas = []


def criar_modulo(
    nome, funcao, prioridade, criticidade, combustivel, horario, sensores_ok=True
):
    return {
        "nome": nome,
        "funcao": funcao,
        "prioridade": prioridade,
        "criticidade": criticidade,
        "combustivel": combustivel,
        "horario_chegada": horario,
        "sensores_ok": sensores_ok,
    }


def inicializar_cenario():
    fila_pouso.append(
        criar_modulo(
            "Logística",
            "Ferramentas",
            4,
            "Média",
            round(random.uniform(5, 100), 1),
            "08:00",
        )
    )
    fila_pouso.append(
        criar_modulo(
            "Habitação", "Abrigo", 3, "Alta", round(random.uniform(5, 100), 1), "08:15"
        )
    )
    fila_pouso.append(
        criar_modulo(
            "Suporte Médico",
            "Emergência",
            1,
            "Alta",
            round(random.uniform(5, 100), 1),
            "08:05",
        )
    )
    fila_pouso.append(
        criar_modulo(
            "Laboratório",
            "Pesquisa",
            5,
            "Média",
            round(random.uniform(5, 100), 1),
            "08:30",
        )
    )
    fila_pouso.append(
        criar_modulo(
            "Energia",
            "Geração",
            2,
            "Alta",
            round(random.uniform(5, 100), 1),
            "08:10",
            sensores_ok=random.choice([True, False]),
        )
    )


def buscar_menor_combustivel(fila):
    if not fila:
        return None
    modulo_critico = fila[0]
    for modulo in fila:
        if modulo["combustivel"] < modulo_critico["combustivel"]:
            modulo_critico = modulo
    return modulo_critico


def ordenar_fila_por_prioridade(fila):
    for i in range(1, len(fila)):
        chave = fila[i]
        j = i - 1
        while j >= 0 and chave["prioridade"] < fila[j]["prioridade"]:
            fila[j + 1] = fila[j]
            j -= 1
        fila[j + 1] = chave


def analisar_clima_marciano():
    fenomenos = [
        "Tempestade de Areia",
        "Cisalhamento de Vento",
        "Frio Extremo Inesperado",
    ]
    if random.random() < 0.40:
        qtd_problemas = random.randint(1, 3)
        problemas_ativos = random.sample(fenomenos, qtd_problemas)
        return False, problemas_ativos
    return True, []


def simular_pouso(area_livre):
    print("\n--- INICIANDO PROTOCOLO DE POUSO ---")
    while len(fila_pouso) > 0:
        modulo_atual = fila_pouso.pop(0)
        print(
            f"\n[Analisando] {modulo_atual['nome']} (Prioridade {modulo_atual['prioridade']} | Combustível: {modulo_atual['combustivel']}%)"
        )

        clima_ok, problemas_clima = analisar_clima_marciano()

        if not clima_ok:
            print(
                f"   -> RADAR METEOROLÓGICO: Detectado(s) {', '.join(problemas_clima)}!"
            )

        combustivel_ok = modulo_atual["combustivel"] > 15
        sensores_ok = modulo_atual["sensores_ok"]
        prioridade_alta = modulo_atual["prioridade"] <= 2

        if not combustivel_ok and not prioridade_alta:
            print(f"   -> ALERTA: Combustível crítico! Reavaliando prioridade.")
            pilha_alertas.append(f"Alerta de Combustível: {modulo_atual['nome']}")
            modulo_atual["prioridade"] = 0
            fila_pouso.append(modulo_atual)
            ordenar_fila_por_prioridade(fila_pouso)
            continue

        if not clima_ok and not sensores_ok:
            msg_alerta = f"ALERTA MÁXIMO: Falha de Sensores + Clima Adverso ({problemas_clima[0]}) no módulo {modulo_atual['nome']}"
            print(f"   -> {msg_alerta}")
            pilha_alertas.append(msg_alerta)
            lista_espera.append(modulo_atual)
            continue

        if combustivel_ok and sensores_ok and clima_ok and area_livre:
            print(f"   -> SUCESSO: Pouso autorizado.")
            lista_pousados.append(modulo_atual)
            area_livre = False
        else:
            print(f"   -> FALHA: Pouso negado.")
            if not sensores_ok:
                print("      Motivo: Falha nos sensores. Adiado para análise.")
                lista_espera.append(modulo_atual)
                pilha_alertas.append(f"Falha de sensor: {modulo_atual['nome']}")
            elif not area_livre:
                print("      Motivo: Área de pouso ocupada. Entrando em espera.")
                lista_espera.append(modulo_atual)
            elif not clima_ok:
                print("      Motivo: Condição atmosférica adversa. Entrando em espera.")
                lista_espera.append(modulo_atual)

        area_livre = True


# ==============================================================================
# EXECUÇÃO DA FASE 2
# ==============================================================================
if __name__ == "__main__":
    inicializar_cenario()

    modulo_menos_combustivel = buscar_menor_combustivel(fila_pouso)
    print(
        f"Módulo com menor combustível detectado: {modulo_menos_combustivel['nome']} ({modulo_menos_combustivel['combustivel']}%)"
    )

    ordenar_fila_por_prioridade(fila_pouso)
    print("\nFila de pouso configurada e ordenada por prioridade.")

    simular_pouso(area_livre=True)

    # --- Relatório Final Fase 2 (Visual em Quadro) ---
    linhas_quadro = []
    linhas_quadro.append(f"Módulos Pousados ({len(lista_pousados)}):")
    for m in lista_pousados:
        linhas_quadro.append(f"  [+] {m['nome']}")

    linhas_quadro.append("")
    linhas_quadro.append(f"Módulos em Espera ({len(lista_espera)}):")
    for m in lista_espera:
        linhas_quadro.append(f"  [-] {m['nome']}")

    linhas_quadro.append("")
    linhas_quadro.append(f"Alertas Críticos na Pilha ({len(pilha_alertas)}):")

    # Cópia da pilha para a IA
    alertas_gerados = list(pilha_alertas)

    if not pilha_alertas:
        linhas_quadro.append("  Nenhum alerta registrado.")
    while pilha_alertas:
        linhas_quadro.append(f"  (!) {pilha_alertas.pop()}")

    print("\n")
    imprimir_quadro("RELATÓRIO FINAL DE OPERAÇÃO - MGPEB", linhas_quadro)

    # --- Inteligência Artificial Fase 2 ---
    nomes_pousados = (
        ", ".join([m["nome"] for m in lista_pousados]) if lista_pousados else "Nenhum"
    )
    nomes_espera = (
        ", ".join([m["nome"] for m in lista_espera]) if lista_espera else "Nenhum"
    )
    lista_de_alertas = (
        ", ".join(alertas_gerados) if alertas_gerados else "Nenhum alerta"
    )

    prompt_ia_fase2 = (
        f"Atue como Diretor de Voo Sênior da Missão Aurora. O processo de descida da Fase 2 terminou. "
        f"Resultado: {len(lista_pousados)} módulos pousados com sucesso ({nomes_pousados}) e "
        f"{len(lista_espera)} módulos retidos em órbita ({nomes_espera}). "
        f"Alertas registrados: {lista_de_alertas}. "
        f"Escreva um boletim técnico de diagnóstico curto em português do Brasil:\n"
        f"- STATUS: Resuma o resultado da operação de pouso.\n"
        f"- RISCO: Explique tecnicamente os riscos gerados pelos módulos que ficaram em espera ou alertas críticos.\n"
        f"- AÇÃO: Defina o foco imediato de investigação em órbita e na superfície."
    )

    print("\n--- ANÁLISE DO DIRETOR DE VOO (IA FASE 2) ---")
    try:
        if api_key:
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt_ia_fase2
            )
            print(response.text)
    except Exception as e:
        print(f"Falha na comunicação com a IA: {e}")

    print("=" * 85)
