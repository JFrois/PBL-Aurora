import random


def criar_modulo(ID_MODULO, prioridade, combustivel, sensores_ok=True):
    """
    Função auxiliar (Factory) para padronizar a criação de cada módulo.
    Retorna um dicionário que representará a entidade dentro das filas.
    """
    return {
        "ID_MODULO": ID_MODULO,
        "prioridade": prioridade,
        "combustivel": combustivel,
        "sensores_ok": sensores_ok,
    }


def ordenar_fila_por_prioridade(fila):
    """
    Algoritmo de Ordenação: Insertion Sort (Ordenação por Inserção).
    Reorganiza a fila para garantir que a prioridade mais alta (1) seja processada primeiro.
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
    Retorna uma tupla: (Booleano clima_ok, Lista de problemas)
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


def executar_fase2():
    """
    Processa a chegada dos módulos à órbita de Marte.
    Gere a Fila de Pouso (FIFO), Histórico de Sucesso (Lista) e Alertas (LIFO/Pilha).
    """
    print("\n" + "=" * 85)
    print("INICIANDO FASE 2: APROXIMAÇÃO E POUSO (MGPEB)".center(85))
    print("=" * 85)

    # Inicialização da Fila de Pouso com os 5 módulos base da missão
    fila_pouso = [
        criar_modulo("MOD-LOG-01", 4, round(random.uniform(5, 100), 1)),
        criar_modulo("MOD-HAB-01", 3, round(random.uniform(5, 100), 1)),
        criar_modulo("MOD-MED-01", 1, round(random.uniform(5, 100), 1)),
        criar_modulo("MOD-LAB-01", 5, round(random.uniform(5, 100), 1)),
        criar_modulo(
            "MOD-ENE-01",
            2,
            round(random.uniform(5, 100), 1),
            random.choice([True, False]),
        ),
    ]

    # Ordenação inicial obrigatória
    ordenar_fila_por_prioridade(fila_pouso)

    # Estruturas para armazenar o destino das entidades
    lista_pousados = []  # Armazena os IDs dos módulos que pousaram com sucesso
    lista_espera = []  # Armazena IDs dos módulos retidos em órbita devido a falhas
    pilha_alertas = []  # Pilha LIFO para os registos de anomalias
    area_livre = True  # Validação de espaço no espaçoporto

    print("\n--- INICIANDO PROTOCOLO DE POUSO ---")

    # Processa enquanto houver elementos na fila (Conceito FIFO: pop(0))
    while len(fila_pouso) > 0:
        modulo = fila_pouso.pop(0)

        print(
            f"\n[Analisando] {modulo['ID_MODULO']} (Prioridade {modulo['prioridade']} | Combustível: {modulo['combustivel']}%)"
        )

        clima_ok, problemas_clima = analisar_clima_marciano()
        combustivel_ok = modulo["combustivel"] > 15
        sensores_ok = modulo["sensores_ok"]

        # ----------------------------------------------------------------------
        # REGRA EXCEPCIONAL 1: Sem combustível e não é prioridade máxima
        # ----------------------------------------------------------------------
        if not combustivel_ok and modulo["prioridade"] > 2:
            print("   -> ALERTA: Combustível crítico! Reavaliando prioridade.")
            pilha_alertas.append(f"Alerta de Combustível: {modulo['ID_MODULO']}")

            # Força prioridade máxima e devolve à fila
            modulo["prioridade"] = 1
            fila_pouso.append(modulo)

            # Aplica o Insertion Sort para garantir que ele vá pro topo da fila
            ordenar_fila_por_prioridade(fila_pouso)
            continue

        # ----------------------------------------------------------------------
        # REGRA EXCEPCIONAL 2: Clima ruim AND sensores pifados (Perigo de queda)
        # ----------------------------------------------------------------------
        if not clima_ok and not sensores_ok:
            msg_alerta = f"ALERTA MÁXIMO: Falha de Sensores + Clima Adverso ({problemas_clima[0]}) no módulo {modulo['ID_MODULO']}"
            print(f"   -> {msg_alerta}")
            pilha_alertas.append(msg_alerta)
            lista_espera.append(modulo["ID_MODULO"])
            continue

        # ----------------------------------------------------------------------
        # PORTA LÓGICA PRINCIPAL (AND Estrito)
        # ----------------------------------------------------------------------
        if clima_ok and sensores_ok and combustivel_ok and area_livre:
            print(f"   -> SUCESSO: Pouso autorizado.")
            lista_pousados.append(modulo["ID_MODULO"])
            area_livre = False  # Simula que a área foi momentaneamente ocupada
        else:
            print("   -> FALHA: Pouso negado.")
            lista_espera.append(modulo["ID_MODULO"])

            # Registro detalhado do motivo da retenção
            if not sensores_ok:
                print(
                    "      Motivo: Falha nos sensores. Adiado para análise em órbita."
                )
                pilha_alertas.append(f"Falha de sensor: {modulo['ID_MODULO']}")
            elif not area_livre:
                print("      Motivo: Área de pouso ocupada. Entrando em espera.")
            elif not clima_ok:
                fenomenos_str = ", ".join(problemas_clima)
                print(f"      Motivo: Condição atmosférica adversa ({fenomenos_str}).")

        # Reseta o booleano de área para o próximo loop (liberação da pista)
        area_livre = True

    # Retorna o resultado estruturado e super detalhado para o orquestrador (main.py)
    return {
        "pousados": lista_pousados,
        "em_espera": lista_espera,
        "alertas": pilha_alertas,
    }
