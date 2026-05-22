import random
import time
import os
from dotenv import (
    load_dotenv,
)  # Usado para carregar o arquivo .env contendo a chave da API
from google import genai  # SDK oficial do Google Gemini para chamadas de IA

# ==============================================================================
# CONFIGURAÇÃO GERAL
# ==============================================================================
# Carrega as variáveis do arquivo .env (onde a GEMINI_API_KEY deve estar armazenada com segurança)
load_dotenv()


def imprimir_quadro(titulo, linhas):
    """
    Função auxiliar de interface (UI) no terminal.
    Recebe um título e uma lista de strings (linhas) e as formata
    dentro de um quadro de texto estilizado com 85 caracteres de largura.
    """
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
todos_erros = (
    []
)  # Lista global que armazenará todos os erros da Fase 1 para enviar à IA

print("\n" + "=" * 85)
print("Sejam bem-vindos ao sistema de telemetria da MISSÃO AURORA".center(85))
print("Iniciando sequência de 3 testes obrigatórios...".center(85))
print("=" * 85 + "\n")

# Loop principal da Fase 1: exige 3 testes consecutivos para validar a decolagem
while quantidade_testes < 3:
    erros = []  # Zera a lista de erros a cada nova rodada
    quantidade_testes += 1

    # --- Simulação de telemetria (Geração de dados dos sensores) ---
    # Valores aleatórios restritos às zonas seguras da nave
    temp_interna = random.uniform(18.5, 24.5)  # Limite de segurança: 18 a 25
    temp_externa = random.uniform(6.0, 37.0)  # Limite de segurança: 5 a 38
    integridade_estrutural = random.choice(
        [1]
    )  # Mantido o random.choice, mas só com opção OK
    capacidade_energia_kwh = random.uniform(4000, 5000)  # Capacidade sempre alta
    carga_energia_pct = random.uniform(
        95, 100
    )  # Bateria quase cheia (garante o mínimo de 80% final)
    consumo_energia_est = random.uniform(200, 250)  # Consumo otimizado/baixo
    perdas_energia = random.uniform(10, 20)  # Perdas mínimas
    pressao = random.uniform(310, 440)  # Limite de segurança: 300 a 450
    modulos_criticos = random.choice(
        ["OK"]
    )  # Mantido random.choice, mas garantindo aprovação

    # --- Processamento da Análise Energética (Cálculos Matemáticos) ---
    # 1. Calcula a energia real disponível nas baterias com base na % de carga
    energia_bruta_kwh = capacidade_energia_kwh * (carga_energia_pct / 100)
    # 2. Subtrai o custo estimado da decolagem e as perdas do sistema
    energia_restante_kwh = energia_bruta_kwh - perdas_energia - consumo_energia_est
    # 3. Descobre qual será a % de bateria restante após o lançamento (não pode ser menor que 0)
    saldo_pos_decolagem_pct = max(
        0, (energia_restante_kwh / capacidade_energia_kwh) * 100
    )

    # --- Verificações de segurança (Regras de Negócio e Limites de Operação) ---
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

    # --- Processamento do teste individual (Formatação do Relatório) ---
    conteudo_relatorio = [
        "VERIFICAÇÃO DE SEGURANÇA:",
        f"  > Bateria Útil p/ Sistema: {max(0, energia_restante_kwh):.2f} kWh",
        f"  > Custo de Decolagem.....: {consumo_energia_est:.2f} kWh",
        f"  > Autonomia energética pós decolagem...: {saldo_pos_decolagem_pct:.2f}%",
        f"  > Temp. Interna: {temp_interna:.2f} C°",
        f"  > Temp. Externa: {temp_externa:.2f} C°",
        f"  > Integridade: {'OK' if integridade_estrutural == 1 else 'FALHA'}",
        f"  > Pressão: {pressao:.2f} psi",
    ]

    # Avaliação: Se a lista de erros estiver vazia, o teste foi um sucesso
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
            todos_erros.append(
                erro
            )  # Salva o erro no histórico global para a IA ler depois

    # Imprime o resultado desta rodada específica
    imprimir_quadro(
        f"RELATÓRIO DE RODADA: {quantidade_testes}/3",
        [status_individual, info, "-" * 61] + conteudo_relatorio,
    )

# --- Decisão Final Fase 1 (GO / NO-GO) ---
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


# --- Inteligência Artificial Fase 1 (Integração Gemini) ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print(
        "\nFalha: variável GEMINI_API_KEY não encontrada no arquivo .env ou no ambiente."
    )
else:
    # Instancia o cliente da IA
    client = genai.Client(api_key=api_key)

# Lógica de montagem do Prompt: varia de acordo com o sucesso ou falha da missão
if testes_sucessos == 3:
    print("\n>>> STATUS FINAL: PRONTO PARA DECOLAR! 🚀")
    print("Todos os testes foram aprovados. Iniciando contagem de ignição...\n")
    prompt_ia = (
        f"Atue como Diretor de Voo Sênior da Missão Aurora. Todos os subsistemas estão nominais e "
        f"o foguete passou nos 3 testes críticos de telemetria de pré-lançamento com 100% de êxito. "
        f"Gere um comunicado oficial e técnico de no máximo três linhas em português do Brasil. "
        f"Na primeira linha, parabenize a equipe de engenharia pela estabilidade do sistema. "
        f"Na segunda linha, faça a classificação dos dados. "
        f"Na terceira linha, declare 'GO FOR LAUNCH' e autorize formalmente o início da sequência de ignição."
        f"Deixar todo o relatório com no máximo 5 linhas para garantir objetividade e clareza na comunicação. "
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
    # Remove erros duplicados usando set() e formata como uma string separada por vírgulas
    erros_formatadas = ", ".join(sorted(set(todos_erros)))

    prompt_ia = (
        f"Atue como Diretor de Voo Sênior da Missão Aurora. Condição NO-GO. O lançamento foi "
        f"imediatamente abortado devido a falhas críticas em {testes_falhas} de 3 testes de verificação. "
        f"Anomalias registradas via telemetria: {erros_formatadas}. "
        f"Faça a classificação dos dados. "
        f"Escreva um boletim técnico de diagnóstico curto em português do Brasil, estruturado da seguinte forma:\n"
        f"- STATUS: Confirme o aborto do lançamento.\n"
        f"- RISCO: Explique tecnicamente por que essas anomalias específicas causam risco de perda de veículo.\n"
        f"- AÇÃO: Defina o foco imediato de investigação para a equipe de engenharia de software e hardware."
        f"Deixar todo o o tom do comunicado sério, técnico e formal, condizente com a gravidade da situação."
        f"Deixar todo o relatório com no máximo 5 linhas para garantir objetividade e clareza na comunicação. "
    )

print("--- ANÁLISE DO DIRETOR DE VOO (IA FASE 1) ---")
try:
    if api_key:
        # Chama a API do Gemini informando o modelo (2.5-flash) e o prompt montado
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt_ia
        )
        print(response.text)
except Exception as e:
    print(f"Falha na comunicação com a IA: {e}")

print("=" * 85)
time.sleep(
    10
)  # Pausa breve antes de iniciar a próxima fase para melhor visualização no terminal


# ==============================================================================
# PROJETO AURORA SIGER - FASE 2: GERENCIAMENTO DE POUSO (MGPEB)
# ==============================================================================
print("\n" + "=" * 85)

print("INICIANDO FASE 2: APROXIMAÇÃO A MARTE E POUSO DE MÓDULOS".center(85))

print("=" * 85 + "\n")
# --- Estruturas de Dados Lineares Fundamentais ---
fila_pouso = (
    []
)  # Queue (Fila - FIFO): Elementos saem pela ordem de chegada/prioridade - pop(0)
lista_pousados = []  # List (Lista): Histórico de módulos que desceram com sucesso
lista_espera = []  # List (Lista): Módulos retidos em órbita por falhas
pilha_alertas = (
    []
)  # Stack (Pilha - LIFO): Registra anomalias, onde a última inserida é a primeira exibida - pop()


def criar_modulo(
    ID_MODULO,
    funcao,
    prioridade,
    criticidade,
    combustivel,
    massa,
    horario,
    sensores_ok=True,
):
    """
    Função construtora (Factory).
    Retorna um dicionário contendo todas as propriedades de um módulo.
    Ao agrupar os dados em um dicionário, movemos a entidade inteira entre as listas e filas.
    """
    return {
        "ID_MODULO": ID_MODULO,
        "funcao": funcao,
        "prioridade": prioridade,
        "criticidade": criticidade,
        "combustivel": combustivel,
        "massa": massa,
        "horario_chegada": horario,
        "sensores_ok": sensores_ok,
    }


def inicializar_cenario():
    """
    Carrega a fila de pouso inicial instanciando os 5 módulos fundamentais
    conforme planejamento da base.
    """
    fila_pouso.append(
        criar_modulo(
            "MOD-LOG-01",
            "Ferramentas",
            4,
            "Média",
            round(random.uniform(5, 100), 1),
            2500.0,  # Massa em kg
            "08:00",
        )
    )
    fila_pouso.append(
        criar_modulo(
            "MOD-HAB-01",
            "Abrigo",
            3,
            "Alta",
            round(random.uniform(5, 100), 1),
            8500.0,
            "08:15",
        )
    )
    fila_pouso.append(
        criar_modulo(
            "MOD-MED-01",
            "Emergência",
            1,
            "Alta",
            round(random.uniform(5, 100), 1),
            3200.0,
            "08:05",
        )
    )
    fila_pouso.append(
        criar_modulo(
            "MOD-LAB-01",
            "Pesquisa",
            5,
            "Média",
            round(random.uniform(5, 100), 1),
            4100.0,
            "08:30",
        )
    )
    # O módulo de energia tem chance aleatória de já nascer com os sensores pifados
    fila_pouso.append(
        criar_modulo(
            "MOD-ENE-01",
            "Geração",
            2,
            "Alta",
            round(random.uniform(5, 100), 1),
            6000.0,
            "08:10",
            sensores_ok=random.choice([True, False]),
        )
    )


def buscar_menor_combustivel(fila):
    """
    Algoritmo de Busca Sequencial.
    Varre a fila inteira linearmente, comparando o combustível atual com o menor já encontrado.
    """
    if not fila:
        return None
    modulo_critico = fila[0]
    for modulo in fila:
        if modulo["combustivel"] < modulo_critico["combustivel"]:
            modulo_critico = modulo
    return modulo_critico


def ordenar_fila_por_prioridade(fila):
    """
    Algoritmo de Ordenação: Insertion Sort (Ordenação por Inserção).
    Garante que os módulos com prioridade menor numéricamente (ex: 1) fiquem no topo da fila.
    """
    for i in range(1, len(fila)):
        chave = fila[i]
        j = i - 1
        while j >= 0 and chave["prioridade"] < fila[j]["prioridade"]:
            fila[j + 1] = fila[j]
            j -= 1
        fila[j + 1] = chave


def analisar_clima_marciano():
    """
    Simula fenômenos naturais (Tempestades, Cisalhamento, Frio Extremo)
    que podem abortar o pouso de última hora.
    """
    fenomenos = [
        "Tempestade de Areia",
        "Cisalhamento de Vento",
        "Frio Extremo Inesperado",
    ]
    # 40% de chance de dar problema no clima durante a janela de pouso
    if random.random() < 0.40:
        qtd_problemas = random.randint(1, 3)
        problemas_ativos = random.sample(fenomenos, qtd_problemas)
        return False, problemas_ativos
    return True, []


def simular_pouso(area_livre):
    """
    Motor central da Fase 2 do MGPEB.
    Processa a fila de pouso aplicando estritamente as regras de lógica Booleana.
    """
    print("\n--- INICIANDO PROTOCOLO DE POUSO ---")

    while len(fila_pouso) > 0:
        modulo_atual = fila_pouso.pop(0)
        print(
            f"\n[Analisando] {modulo_atual['ID_MODULO']} (Prioridade {modulo_atual['prioridade']} | Combustível: {modulo_atual['combustivel']}%)"
        )

        clima_ok, problemas_clima = analisar_clima_marciano()

        if not clima_ok:
            print(
                f"   -> RADAR METEOROLÓGICO: Detectado(s) {', '.join(problemas_clima)}!"
            )

        # Declaração das variáveis booleanas da regra de decisão
        combustivel_ok = modulo_atual["combustivel"] > 15
        sensores_ok = modulo_atual["sensores_ok"]
        prioridade_alta = modulo_atual["prioridade"] <= 2

        # REGRA EXCEPCIONAL 1: Se estiver sem combustível, mas não for prioridade, fura a fila.
        if not combustivel_ok and not prioridade_alta:
            print(f"   -> ALERTA: Combustível crítico! Reavaliando prioridade.")
            pilha_alertas.append(f"Alerta de Combustível: {modulo_atual['ID_MODULO']}")
            modulo_atual["prioridade"] = (
                1  # Alterado de 0 para 1 para respeitar o limite (1 a 5)
            )
            fila_pouso.append(modulo_atual)
            ordenar_fila_por_prioridade(fila_pouso)
            continue

        # REGRA EXCEPCIONAL 2: Clima ruim AND sensores pifados = Alerta crítico e Retenção
        if not clima_ok and not sensores_ok:
            msg_alerta = f"ALERTA MÁXIMO: Falha de Sensores + Clima Adverso ({problemas_clima[0]}) no módulo {modulo_atual['ID_MODULO']}"
            print(f"   -> {msg_alerta}")
            pilha_alertas.append(msg_alerta)
            lista_espera.append(modulo_atual)
            continue

        # PORTA LÓGICA PRINCIPAL (AND Estrito)
        if combustivel_ok and sensores_ok and clima_ok and area_livre:
            print(f"   -> SUCESSO: Pouso autorizado.")
            lista_pousados.append(modulo_atual)
            area_livre = False

        # TRATAMENTO DE FALHAS
        else:
            print(f"   -> FALHA: Pouso negado.")
            if not sensores_ok:
                print("      Motivo: Falha nos sensores. Adiado para análise.")
                lista_espera.append(modulo_atual)
                pilha_alertas.append(f"Falha de sensor: {modulo_atual['ID_MODULO']}")
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
        f"Módulo com menor combustível detectado: {modulo_menos_combustivel['ID_MODULO']} ({modulo_menos_combustivel['combustivel']}%)"
    )

    ordenar_fila_por_prioridade(fila_pouso)
    print("\nFila de pouso configurada e ordenada por prioridade.")

    simular_pouso(area_livre=True)

    # --- Relatório Final Fase 2 ---
    linhas_quadro = []
    linhas_quadro.append(f"Módulos Pousados ({len(lista_pousados)}):")
    for m in lista_pousados:
        linhas_quadro.append(f"  [+] {m['ID_MODULO']}")

    linhas_quadro.append("")
    linhas_quadro.append(f"Módulos em Espera ({len(lista_espera)}):")
    for m in lista_espera:
        linhas_quadro.append(f"  [-] {m['ID_MODULO']}")

    linhas_quadro.append("")
    linhas_quadro.append(f"Alertas Críticos na Pilha ({len(pilha_alertas)}):")

    alertas_gerados = list(pilha_alertas)

    if not pilha_alertas:
        linhas_quadro.append("  Nenhum alerta registrado.")

    while pilha_alertas:
        linhas_quadro.append(f"  (!) {pilha_alertas.pop()}")

    print("\n")
    imprimir_quadro("RELATÓRIO FINAL DE OPERAÇÃO - MGPEB", linhas_quadro)

    # --- Inteligência Artificial Fase 2 (Boletim Diagnóstico) ---
    nomes_pousados = (
        ", ".join([m["ID_MODULO"] for m in lista_pousados])
        if lista_pousados
        else "Nenhum"
    )
    nomes_espera = (
        ", ".join([m["ID_MODULO"] for m in lista_espera]) if lista_espera else "Nenhum"
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
        f"- AÇÃO: Defina o foco imediato de investigação em órbita e na superfície.\n"
        f"Deixar todo o o tom do comunicado sério, técnico e formal, condizente com a gravidade da situação.\n"
        f"Deixar todo o relatório com no máximo 5 linhas para garantir objetividade e clareza na comunicação. "
    )

    print("\n--- ANÁLISE DO DIRETOR DE VOO (IA FASE 2) ---")
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None

    try:
        if api_key:
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt_ia_fase2
            )
            print(response.text)
    except Exception as e:
        print(f"Falha na comunicação com a IA: {e}")

    print("=" * 85)
