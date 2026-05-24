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

    # ALGORITMO: Insertion Sort (Ordenação por Inserção)
    # Reorganiza a fila para garantir que a prioridade mais alta (1) seja processada primeiro
    for i in range(1, len(fila_pouso)):
        chave = fila_pouso[i]
        j = i - 1
        while j >= 0 and chave["prioridade"] < fila_pouso[j]["prioridade"]:
            fila_pouso[j + 1] = fila_pouso[j]
            j -= 1
        fila_pouso[j + 1] = chave

    # Estruturas para armazenar o destino das entidades
    lista_pousados = []  # Armazena os módulos que pousaram com sucesso
    lista_espera = []  # Armazena módulos retidos em órbita devido a falhas
    pilha_alertas = []  # Pilha LIFO para os registos de anomalias

    print("\n--- INICIANDO PROTOCOLO DE POUSO ---")

    # Processa enquanto houver elementos na fila (Conceito FIFO: pop(0))
    while len(fila_pouso) > 0:
        modulo = fila_pouso.pop(0)

        # Simula 40% de probabilidade de mau tempo
        clima_ok = True if random.random() > 0.40 else False

        # Variável booleana para combustível
        combustivel_ok = modulo["combustivel"] > 15

        # Regra Excecional: Se estiver sem combustível, altera a prioridade para emergência (1)
        if not combustivel_ok and modulo["prioridade"] > 2:
            modulo["prioridade"] = 1
            fila_pouso.append(modulo)  # Recoloca no final da fila para ser reprocessado
            continue

        # Porta Lógica AND: O pouso só ocorre se tudo estiver em ordem
        if clima_ok and modulo["sensores_ok"] and combustivel_ok:
            print(f"[+] {modulo['ID_MODULO']} pousou com sucesso.")
            lista_pousados.append(modulo["ID_MODULO"])
        else:
            print(f"[-] {modulo['ID_MODULO']} retido em órbita.")
            lista_espera.append(modulo["ID_MODULO"])
            pilha_alertas.append(f"Anomalia no {modulo['ID_MODULO']}")

    # Retorna o resultado estruturado para o orquestrador (main.py)
    return {
        "pousados": lista_pousados,
        "em_espera": lista_espera,
        "alertas": pilha_alertas,
    }
