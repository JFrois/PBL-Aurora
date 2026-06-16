"""
=====================================================================================
  SIGIC — Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia
                          Base Aurora Siger | FIAP 2026
=====================================================================================
  Fase 4: Modelagem da rede de módulos como grafo, Matriz de Adjacência e
          Menu Interativo de consulta.

  INTEGRAÇÃO COM O PIPELINE:
    - Recebe `resultado_fase2` de main.py para sincronizar o status dos módulos
      (pousados = operacional, em_espera = inativo) com a rede de grafos.
    - Recebe `resultado_fase3` para refletir o diagnóstico energético no status
      do módulo de armazenamento de energia.
    - Retorna um dicionário com o resumo da rede para o bloco de IA do main.py.
=====================================================================================
"""

import time

# =====================================================================
# BLOCO 1 — MODELAGEM DE DADOS
# Estrutura: Dicionário hierárquico (acesso O(1) por chave)
#
# INTEGRAÇÃO: o campo "status" e "status_codigo" são atualizados
# dinamicamente pela função `sincronizar_com_pipeline()` com base
# nos resultados reais das Fases 2 e 3 antes de exibir qualquer menu.
# =====================================================================

# Mapeamento entre os IDs usados na Fase 2 e as chaves do SIGIC
# Permite que sincronizar_com_pipeline() faça a ligação entre os dois sistemas
MAPA_ID_MODULO = {
    "MOD-MED-01": "suporte_medico",
    "MOD-ENE-01": "armazenamento_energia",
    "MOD-HAB-01": "habitacao",
    "MOD-LAB-01": "laboratorio",
    "MOD-LOG-01": "centro_controle",   # LOG-01 representa o Centro de Controle/Logística
}

# Dicionário-mestre: mapeia o identificador do módulo aos seus atributos
MODULOS_COLONIA: dict = {
    "habitacao": {
        # TUPLA: dados de configuração estática — nunca mudam em runtime
        "descricao": ("Habitação", "Módulo residencial da tripulação"),
        "coordenadas_xy": (100, 200),
        # DICIONÁRIO: dados operacionais — atualizados pelo pipeline
        "consumo_kw": 45.0,
        "prioridade": 1,
        "capacidade": "12 tripulantes",
        "status": "aguardando_pouso",   # valor inicial — será sobrescrito
        "status_codigo": 0,
    },
    "centro_controle": {
        "descricao": ("Centro de Controle", "Núcleo de comando e monitoramento da base"),
        "coordenadas_xy": (200, 300),
        "consumo_kw": 60.0,
        "prioridade": 2,
        "capacidade": "8 estações de trabalho",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "armazenamento_energia": {
        "descricao": ("Armazenamento de Energia", "Baterias e painéis solares da colônia"),
        "coordenadas_xy": (300, 100),
        "consumo_kw": 10.0,
        "prioridade": 3,
        "capacidade": "500 kWh",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "agricultura": {
        "descricao": ("Agricultura", "Estufas pressurizadas para produção de alimentos"),
        "coordenadas_xy": (300, 500),
        "consumo_kw": 35.0,
        "prioridade": 4,
        "capacidade": "200 m² de área cultivável",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "laboratorio": {
        "descricao": ("Laboratório Científico", "Pesquisa geológica, biológica e química"),
        "coordenadas_xy": (500, 400),
        "consumo_kw": 55.0,
        "prioridade": 7,
        "capacidade": "6 bancadas de pesquisa",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "comunicacao": {
        "descricao": ("Comunicação", "Antenas de rádio e link laser com a Terra"),
        "coordenadas_xy": (500, 200),
        "consumo_kw": 40.0,
        "prioridade": 5,
        "capacidade": "Link laser 10 Gbps / Rádio UHF backup",
        "status": "operacional",        # comunicação já estava ativa nas fases anteriores
        "status_codigo": 1,
    },
    "suporte_medico": {
        "descricao": ("Suporte Médico", "Enfermaria, UTI e estoque de medicamentos"),
        "coordenadas_xy": (100, 400),
        "consumo_kw": 30.0,
        "prioridade": 2,
        "capacidade": "4 leitos de UTI",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "producao_oxigenio": {
        "descricao": ("Produção de Oxigênio", "Eletrolisadores e sistemas de reciclagem de CO₂"),
        "coordenadas_xy": (400, 300),
        "consumo_kw": 50.0,
        "prioridade": 1,
        "capacidade": "Até 15 kg O₂/dia",
        "status": "operacional",        # essencial — já operava desde o pouso base
        "status_codigo": 1,
    },
}

# =====================================================================
# BLOCO 2 — LISTA DE NOMES (ÍNDICE DA MATRIZ)
# =====================================================================

NOMES_MODULOS: list = [
    "habitacao",             # índice 0
    "centro_controle",       # índice 1
    "armazenamento_energia", # índice 2
    "agricultura",           # índice 3
    "laboratorio",           # índice 4
    "comunicacao",           # índice 5
    "suporte_medico",        # índice 6
    "producao_oxigenio",     # índice 7
]

N = len(NOMES_MODULOS)

# =====================================================================
# BLOCO 3 — MATRIZ DE ADJACÊNCIA (Lista de Listas — estrutura 2D)
# MATRIZ[i][j] = distância em metros | 0 = sem conexão direta
#
# Índices:
#   0=habitacao  1=centro_controle  2=armazenamento_energia  3=agricultura
#   4=laboratorio  5=comunicacao  6=suporte_medico  7=producao_oxigenio
# =====================================================================

MATRIZ_ADJACENCIA: list = [
    # hab  ctrl  ener  agri   lab   com   med   oxi
    [   0,  140,  220,  360,    0,    0,  200,    0],  # 0: habitacao
    [ 140,    0,  220,    0,  320,  320,  140,  200],  # 1: centro_controle
    [ 220,  220,    0,  400,    0,  220,    0,  220],  # 2: armazenamento_energia
    [ 360,    0,  400,    0,  220,    0,  220,  220],  # 3: agricultura
    [   0,  320,    0,  220,    0,  200,    0,  140],  # 4: laboratorio
    [   0,  320,  220,    0,  200,    0,    0,  140],  # 5: comunicacao
    [ 200,  140,    0,  220,    0,    0,    0,  320],  # 6: suporte_medico
    [   0,  200,  220,  220,  140,  140,  320,    0],  # 7: producao_oxigenio
]


# =====================================================================
# BLOCO 4 — INTEGRAÇÃO COM O PIPELINE (PONTO DE CONEXÃO CENTRAL)
# =====================================================================

def sincronizar_com_pipeline(resultado_fase2: dict, resultado_fase3: dict):
    """
    Lê os resultados reais das Fases 2 e 3 e atualiza o status de cada
    módulo no dicionário MODULOS_COLONIA antes de qualquer interação.

    Regras de sincronização:
      - Módulo presente em resultado_fase2["pousados"]  → status = "operacional"
      - Módulo presente em resultado_fase2["em_espera"] → status = "inativo"
      - Módulo de energia com diagnóstico de alerta/crítico da Fase 3
        → status = "alerta" ou "crítico"
    """
    pousados  = resultado_fase2.get("pousados", [])
    em_espera = resultado_fase2.get("em_espera", [])

    # Itera sobre o mapeamento ID_Fase2 ↔ chave_SIGIC
    for id_modulo, chave_sigic in MAPA_ID_MODULO.items():
        if id_modulo in pousados:
            MODULOS_COLONIA[chave_sigic]["status"] = "operacional"
            MODULOS_COLONIA[chave_sigic]["status_codigo"] = 1
        elif id_modulo in em_espera:
            MODULOS_COLONIA[chave_sigic]["status"] = "inativo"
            MODULOS_COLONIA[chave_sigic]["status_codigo"] = 0

    # Refinamento com dados energéticos da Fase 3
    status_energia = resultado_fase3.get("diagnostico_eficiencia", {}).get("status", "")
    if "CRÍTICO" in status_energia:
        MODULOS_COLONIA["armazenamento_energia"]["status"] = "crítico"
        MODULOS_COLONIA["armazenamento_energia"]["status_codigo"] = 3
    elif "MODERADO" in status_energia or "ALERTA" in status_energia:
        if MODULOS_COLONIA["armazenamento_energia"]["status_codigo"] == 1:
            MODULOS_COLONIA["armazenamento_energia"]["status"] = "alerta"
            MODULOS_COLONIA["armazenamento_energia"]["status_codigo"] = 2


def exibir_resumo_sincronizacao(resultado_fase2: dict):
    """
    Exibe um log claro mostrando como os dados da Fase 2 foram
    mapeados para o grafo do SIGIC — torna a integração visível ao usuário.
    """
    print("\n  [SIGIC] Sincronizando rede com resultados do pouso orbital...")
    time.sleep(0.6)

    pousados  = resultado_fase2.get("pousados", [])
    em_espera = resultado_fase2.get("em_espera", [])

    for id_modulo, chave_sigic in MAPA_ID_MODULO.items():
        nome = MODULOS_COLONIA[chave_sigic]["descricao"][0]
        if id_modulo in pousados:
            print(f"    ✅  {id_modulo} → {nome}: ATIVADO na rede")
        elif id_modulo in em_espera:
            print(f"    ⚫  {id_modulo} → {nome}: INATIVO (retido em órbita)")

    # Módulos sem correspondência na Fase 2 (já operacionais desde o início)
    sem_correspondencia = ["comunicacao", "producao_oxigenio", "agricultura"]
    for chave in sem_correspondencia:
        nome = MODULOS_COLONIA[chave]["descricao"][0]
        status = MODULOS_COLONIA[chave]["status"]
        print(f"    🔵  {nome}: {status.upper()} (infraestrutura base da colônia)")

    print()


# =====================================================================
# BLOCO 5 — FUNÇÕES AUXILIARES DE EXIBIÇÃO
# =====================================================================

def exibir_cabecalho_sigic():
    print("\n" + "=" * 85)
    print("  SIGIC — Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia  ")
    print("                    Base Aurora Siger | Fase 4                               ")
    print("=" * 85)


def exibir_matriz_adjacencia():
    print("\n" + "=" * 85)
    print("  REDE DE INFRAESTRUTURA — MATRIZ DE ADJACÊNCIA (distâncias em metros)  ")
    print("  (0 = sem conexão direta | módulos inativos mantêm arestas para futura ativação)")
    print("=" * 85)

    abreviacoes = ["HAB", "CTR", "ENE", "AGR", "LAB", "COM", "MED", "OXI"]
    mapa_status = {1: "🟢", 2: "🟡", 3: "🔴", 0: "⚫"}

    print(f"{'':>6}", end="")
    for abrev in abreviacoes:
        print(f"{abrev:>6}", end="")
    print()
    print(f"{'':>6}" + "-" * (6 * N))

    for i in range(N):
        chave  = NOMES_MODULOS[i]
        icone  = mapa_status.get(MODULOS_COLONIA[chave]["status_codigo"], "?")
        print(f"{abreviacoes[i]:>4}{icone}|", end="")
        for j in range(N):
            valor = MATRIZ_ADJACENCIA[i][j]
            print(f"{'  —':>6}" if valor == 0 else f"{valor:>6}", end="")
        print()

    print("\n  Legenda (abreviação → módulo | ícone = status atual):")
    for i, (abrev, chave) in enumerate(zip(abreviacoes, NOMES_MODULOS)):
        nome   = MODULOS_COLONIA[chave]["descricao"][0]
        icone  = mapa_status.get(MODULOS_COLONIA[chave]["status_codigo"], "?")
        status = MODULOS_COLONIA[chave]["status"]
        print(f"    {abrev} → {nome}  {icone} {status}")

    total_conexoes = sum(
        1 for i in range(N) for j in range(i + 1, N)
        if MATRIZ_ADJACENCIA[i][j] > 0
    )
    print(f"\n  Total de arestas no grafo: {total_conexoes}")
    print("=" * 85)


def consultar_status_modulo(chave: str):
    if chave not in MODULOS_COLONIA:
        print(f"\n  [!] Módulo '{chave}' não encontrado.")
        return

    modulo = MODULOS_COLONIA[chave]   # acesso direto O(1)
    mapa_status = {1: "🟢 OPERACIONAL", 2: "🟡 ALERTA", 3: "🔴 CRÍTICO", 0: "⚫ INATIVO"}

    nome_modulo  = modulo["descricao"][0]
    descricao    = modulo["descricao"][1]
    coords       = modulo["coordenadas_xy"]
    status_label = mapa_status.get(modulo["status_codigo"], "DESCONHECIDO")

    print("\n" + "=" * 85)
    print(f"  STATUS DO MÓDULO: {nome_modulo.upper()}")
    print("=" * 85)
    print(f"  Descrição    : {descricao}")
    print(f"  Identificador: {chave}")
    print(f"  Coordenadas  : X={coords[0]} m, Y={coords[1]} m")
    print(f"  Prioridade   : {modulo['prioridade']}  (1=crítico → 8=baixo impacto)")
    print(f"  Consumo      : {modulo['consumo_kw']} kW")
    print(f"  Capacidade   : {modulo['capacidade']}")
    print(f"  Status atual : {status_label}")

    if chave in NOMES_MODULOS:
        idx = NOMES_MODULOS.index(chave)
        vizinhos = []
        for j in range(N):
            if MATRIZ_ADJACENCIA[idx][j] > 0:
                nome_viz   = MODULOS_COLONIA[NOMES_MODULOS[j]]["descricao"][0]
                status_viz = MODULOS_COLONIA[NOMES_MODULOS[j]]["status"]
                vizinhos.append(f"{nome_viz} ({MATRIZ_ADJACENCIA[idx][j]} m | {status_viz})")
        if vizinhos:
            print(f"  Conexões     : {chr(10) + '               '.join([''] + vizinhos)}")

    print("=" * 85)


def listar_todos_modulos():
    mapa_status = {1: "🟢", 2: "🟡", 3: "🔴", 0: "⚫"}

    print("\n" + "=" * 85)
    print("  INVENTÁRIO DE MÓDULOS — BASE AURORA SIGER")
    print("=" * 85)
    print(f"  {'#':<4} {'MÓDULO':<30} {'PRIORIDADE':<12} {'CONSUMO (kW)':<15} {'STATUS'}")
    print("  " + "-" * 75)

    operacionais = 0
    consumo_ativo = 0.0
    for i, chave in enumerate(NOMES_MODULOS, start=1):
        modulo  = MODULOS_COLONIA[chave]
        nome    = modulo["descricao"][0]
        icone   = mapa_status.get(modulo["status_codigo"], "?")
        status  = modulo["status"]
        print(f"  {i:<4} {nome:<30} {modulo['prioridade']:<12} {modulo['consumo_kw']:<15.1f} {icone} {status}")
        if modulo["status_codigo"] == 1:
            operacionais += 1
            consumo_ativo += modulo["consumo_kw"]

    consumo_total = sum(m["consumo_kw"] for m in MODULOS_COLONIA.values())
    print("  " + "-" * 75)
    print(f"  Módulos operacionais: {operacionais}/{N}  |  "
          f"Consumo ativo: {consumo_ativo:.1f} kW  |  Capacidade total: {consumo_total:.1f} kW")
    print("=" * 85)


# =====================================================================
# BLOCO 6 — STUBS DOS ALGORITMOS (Pedro)
# =====================================================================

def algoritmo_dijkstra(origem: str, destino: str):
    """
    Encontra o caminho de menor distância (em metros) entre dois módulos
    utilizando o algoritmo de Dijkstra com seleção linear do mínimo.

    Complexidade: O(N²) — adequada para grafos pequenos como este (N=8).

    Parâmetros:
        origem  (str): chave do módulo de partida (ex: "armazenamento_energia")
        destino (str): chave do módulo de chegada  (ex: "suporte_medico")

    Retorna:
        dict {"caminho": list[str], "distancia": int}  se houver caminho
        None se origem/destino inválidos ou sem caminho possível
    """
    # Validação das entradas
    if origem not in NOMES_MODULOS or destino not in NOMES_MODULOS:
        print("\n  [!] Módulo de origem ou destino inválido.")
        return None

    if origem == destino:
        print("\n  [!] Origem e destino são o mesmo módulo.")
        return None

    idx_origem  = NOMES_MODULOS.index(origem)
    idx_destino = NOMES_MODULOS.index(destino)

    # Inicialização: distâncias como infinito para todos os nós
    INF      = float("inf")
    dist     = [INF] * N        # distância acumulada mínima até cada nó
    anterior = [-1]  * N        # nó anterior no caminho ótimo (para reconstrução)
    visitado = [False] * N      # controle de nós já finalizados

    dist[idx_origem] = 0        # custo zero para sair da origem

    for _ in range(N):
        # Seleciona o nó não visitado com menor distância acumulada (O(N))
        u = -1
        for v in range(N):
            if not visitado[v] and (u == -1 or dist[v] < dist[u]):
                u = v

        if u == -1 or dist[u] == INF:
            break               # sem mais nós alcançáveis

        visitado[u] = True

        if u == idx_destino:
            break               # destino finalizado — encerra cedo

        # Relaxamento: atualiza a distância dos vizinhos de u
        for v in range(N):
            peso = MATRIZ_ADJACENCIA[u][v]
            if peso > 0 and not visitado[v]:
                nova_dist = dist[u] + peso
                if nova_dist < dist[v]:
                    dist[v]     = nova_dist
                    anterior[v] = u     # registra de onde viemos para reconstruir o caminho

    # Verifica alcançabilidade
    if dist[idx_destino] == INF:
        print(f"\n  [!] Não existe caminho entre '{origem}' e '{destino}'.")
        return None

    # Reconstrói o caminho percorrendo o vetor `anterior` de trás para frente
    caminho_idx = []
    atual = idx_destino
    while atual != -1:
        caminho_idx.append(atual)
        atual = anterior[atual]
    caminho_idx.reverse()

    caminho_chaves = [NOMES_MODULOS[i] for i in caminho_idx]

    # ── Exibição detalhada ──────────────────────────────────────────
    print("\n" + "=" * 85)
    print("  DIJKSTRA — CAMINHO DE MENOR DISTÂNCIA")
    print("=" * 85)
    print(f"  Origem  : {MODULOS_COLONIA[origem]['descricao'][0]}")
    print(f"  Destino : {MODULOS_COLONIA[destino]['descricao'][0]}")
    print()
    print("  Trajeto detalhado:")
    for i in range(len(caminho_chaves) - 1):
        a      = caminho_chaves[i]
        b      = caminho_chaves[i + 1]
        trecho = MATRIZ_ADJACENCIA[NOMES_MODULOS.index(a)][NOMES_MODULOS.index(b)]
        nome_a = MODULOS_COLONIA[a]["descricao"][0]
        nome_b = MODULOS_COLONIA[b]["descricao"][0]
        print(f"    {nome_a}  →  {nome_b}  ({trecho} m)")

    nomes_caminho = [MODULOS_COLONIA[c]["descricao"][0] for c in caminho_chaves]
    print()
    print(f"  Caminho completo : {' → '.join(nomes_caminho)}")
    print(f"  Distância total  : {dist[idx_destino]} metros")
    print(f"  Saltos           : {len(caminho_chaves) - 1}")
    print("=" * 85)

    return {"caminho": caminho_chaves, "distancia": dist[idx_destino]}


def algoritmo_bfs(origem: str):
    """
    Percorre o grafo em Largura (Breadth-First Search) a partir de um módulo,
    visitando primeiro todos os vizinhos diretos antes de avançar para os
    vizinhos dos vizinhos.

    Utiliza uma fila (list usado como deque FIFO) para garantir a ordem correta.
    Complexidade: O(N + A), onde A é o número de arestas.

    Uso prático no SIGIC: mapear todos os módulos alcançáveis a partir de
    um ponto de falha e verificar a conectividade geral da rede.

    Parâmetros:
        origem (str): chave do módulo de partida

    Retorna:
        list[str] com as chaves dos módulos na ordem de visita BFS
    """
    if origem not in NOMES_MODULOS:
        print("\n  [!] Módulo de origem inválido.")
        return []

    idx_origem = NOMES_MODULOS.index(origem)

    visitado = [False] * N
    fila     = [idx_origem]     # fila FIFO: insere no fim, remove do início
    ordem    = []               # sequência de visita resultante

    visitado[idx_origem] = True

    while fila:
        u = fila.pop(0)         # remove o primeiro (FIFO)
        ordem.append(NOMES_MODULOS[u])

        # Enfileira vizinhos não visitados em ordem crescente de índice
        # (garante resultado determinístico para a mesma entrada)
        for v in range(N):
            if MATRIZ_ADJACENCIA[u][v] > 0 and not visitado[v]:
                visitado[v] = True
                fila.append(v)

    # ── Exibição detalhada ──────────────────────────────────────────
    print("\n" + "=" * 85)
    print("  BFS — BUSCA EM LARGURA (Breadth-First Search)")
    print("=" * 85)
    nome_origem = MODULOS_COLONIA[origem]["descricao"][0]
    print(f"  Ponto de partida  : {nome_origem}")
    print(f"  Módulos alcançados: {len(ordem)}/{N}")
    print()
    print("  Ordem de visita (nível a nível a partir da origem):")
    for i, chave in enumerate(ordem, start=1):
        nome   = MODULOS_COLONIA[chave]["descricao"][0]
        status = MODULOS_COLONIA[chave]["status"]
        print(f"    {i:>2}. {nome}  ({status})")

    if len(ordem) < N:
        nao_alcancados = [
            MODULOS_COLONIA[c]["descricao"][0]
            for c in NOMES_MODULOS if c not in ordem
        ]
        print(f"\n  ⚠ Módulos não alcançáveis a partir de {nome_origem}:")
        for nome in nao_alcancados:
            print(f"       • {nome}")
    else:
        print("\n  ✅ Grafo totalmente conexo a partir deste módulo.")

    print("=" * 85)

    return ordem


def algoritmo_dfs(origem: str):
    """
    Percorre o grafo em Profundidade (Depth-First Search) a partir de um módulo,
    explorando cada ramo até o fim antes de retroceder (backtracking).

    Implementado de forma iterativa com pilha explícita para evitar o limite
    de recursão do Python em grafos maiores.
    Complexidade: O(N + A), onde A é o número de arestas.

    Uso prático no SIGIC: detectar conexões críticas (pontes na rede),
    identificar componentes conectados e auditar rotas de contingência.

    Parâmetros:
        origem (str): chave do módulo de partida

    Retorna:
        list[str] com as chaves dos módulos na ordem de visita DFS
    """
    if origem not in NOMES_MODULOS:
        print("\n  [!] Módulo de origem inválido.")
        return []

    idx_origem = NOMES_MODULOS.index(origem)

    visitado = [False] * N
    pilha    = [idx_origem]     # pilha LIFO: insere e remove pelo topo
    ordem    = []

    while pilha:
        u = pilha.pop()         # remove do topo (LIFO — comportamento DFS)

        if visitado[u]:
            continue            # nó já processado por outro ramo — pula
        visitado[u] = True
        ordem.append(NOMES_MODULOS[u])

        # Empilha vizinhos em ordem reversa para manter exploração por
        # índice crescente (o vizinho de menor índice é o primeiro visitado)
        for v in range(N - 1, -1, -1):
            if MATRIZ_ADJACENCIA[u][v] > 0 and not visitado[v]:
                pilha.append(v)

    # ── Exibição detalhada ──────────────────────────────────────────
    print("\n" + "=" * 85)
    print("  DFS — BUSCA EM PROFUNDIDADE (Depth-First Search)")
    print("=" * 85)
    nome_origem = MODULOS_COLONIA[origem]["descricao"][0]
    print(f"  Ponto de partida  : {nome_origem}")
    print(f"  Módulos alcançados: {len(ordem)}/{N}")
    print()
    print("  Ordem de visita (explorando cada ramo até o fim antes de retroceder):")
    for i, chave in enumerate(ordem, start=1):
        nome   = MODULOS_COLONIA[chave]["descricao"][0]
        status = MODULOS_COLONIA[chave]["status"]
        print(f"    {i:>2}. {nome}  ({status})")

    if len(ordem) < N:
        nao_alcancados = [
            MODULOS_COLONIA[c]["descricao"][0]
            for c in NOMES_MODULOS if c not in ordem
        ]
        print(f"\n  ⚠ Módulos não alcançáveis a partir de {nome_origem}:")
        for nome in nao_alcancados:
            print(f"       • {nome}")
        print("\n  ⚠ Grafo parcialmente desconexo — existem módulos isolados.")
    else:
        print("\n  ✅ Grafo totalmente conexo a partir deste módulo.")

    print("=" * 85)

    return ordem


# =====================================================================
# BLOCO 7 — MENU INTERATIVO
# =====================================================================

def exibir_menu_principal():
    print("\n" + "-" * 85)
    print("  PAINEL DE CONTROLE — SIGIC")
    print("-" * 85)
    print("  [1]  Visualizar Rede (Matriz de Adjacência + status real)")
    print("  [2]  Listar Todos os Módulos (Inventário atualizado)")
    print("  [3]  Consultar Status de um Módulo  [busca O(1)]")
    print("  [4]  Executar Dijkstra (Caminho Mínimo)")
    print("  [5]  Executar BFS (Busca em Largura) ")
    print("  [6]  Executar DFS (Busca em Profundidade)")
    print("  [0]  Encerrar SIGIC e retornar ao pipeline")
    print("-" * 85)


def menu_selecionar_modulo(prompt_texto: str) -> str:
    print("\n  Módulos disponíveis:")
    for i, chave in enumerate(NOMES_MODULOS, start=1):
        nome   = MODULOS_COLONIA[chave]["descricao"][0]
        status = MODULOS_COLONIA[chave]["status"]
        print(f"    [{i}] {nome}  ({chave}) — {status}")

    escolha = input(f"\n  {prompt_texto} (número): ").strip()
    try:
        idx = int(escolha) - 1
        if 0 <= idx < N:
            return NOMES_MODULOS[idx]
        print("  [!] Número fora do intervalo válido.")
        return ""
    except ValueError:
        print("  [!] Entrada inválida. Digite apenas o número.")
        return ""


def rodar_menu_interativo():
    """Loop do menu interativo. Chamado internamente por executar_fase4()."""
    while True:
        exibir_menu_principal()
        opcao = input("  Digite a opção desejada: ").strip()

        if opcao == "1":
            exibir_matriz_adjacencia()

        elif opcao == "2":
            listar_todos_modulos()

        elif opcao == "3":
            chave = menu_selecionar_modulo("Selecione o módulo para consultar")
            if chave:
                consultar_status_modulo(chave)

        elif opcao == "4":
            print("\n  [DIJKSTRA] Módulo de ORIGEM:")
            origem = menu_selecionar_modulo("Módulo de origem")
            if origem:
                print("\n  [DIJKSTRA] Módulo de DESTINO:")
                destino = menu_selecionar_modulo("Módulo de destino")
                if destino:
                    resultado = algoritmo_dijkstra(origem, destino)
                    if resultado:
                        print(f"\n  Caminho: {' → '.join(resultado['caminho'])}")
                        print(f"  Distância total: {resultado['distancia']} metros")

        elif opcao == "5":
            print("\n  [BFS] Módulo de ORIGEM:")
            origem = menu_selecionar_modulo("Módulo de origem")
            if origem:
                visitados = algoritmo_bfs(origem)
                if visitados:
                    nomes = [MODULOS_COLONIA[c]["descricao"][0] for c in visitados]
                    print(f"\n  Ordem BFS: {' → '.join(nomes)}")

        elif opcao == "6":
            print("\n  [DFS] Módulo de ORIGEM:")
            origem = menu_selecionar_modulo("Módulo de origem")
            if origem:
                visitados = algoritmo_dfs(origem)
                if visitados:
                    nomes = [MODULOS_COLONIA[c]["descricao"][0] for c in visitados]
                    print(f"\n  Ordem DFS: {' → '.join(nomes)}")

        elif opcao == "0":
            print("\n  [SIGIC] Encerrando painel de controle...\n")
            time.sleep(0.5)
            break

        else:
            print("\n  [!] Opção inválida. Escolha entre 0 e 6.")

        time.sleep(0.2)


# =====================================================================
# BLOCO 8 — PONTO DE ENTRADA DA FASE 4 (chamado pelo main.py)
# =====================================================================

def executar_fase4(resultado_fase2: dict, resultado_fase3: dict) -> dict:
    """
    Função principal da Fase 4. Segue o mesmo padrão das outras fases:
    recebe os resultados anteriores, processa e retorna um dicionário
    com o resumo para o bloco de IA do main.py.

    Parâmetros:
        resultado_fase2 (dict): retorno de executar_fase2()
        resultado_fase3 (dict): retorno de executar_fase3()

    Retorna:
        dict com o snapshot final da rede para a IA analisar.
    """
    exibir_cabecalho_sigic()

    # 1. Sincroniza o grafo com a realidade das fases anteriores
    sincronizar_com_pipeline(resultado_fase2, resultado_fase3)
    exibir_resumo_sincronizacao(resultado_fase2)

    # 2. Exibe o inventário atualizado automaticamente (sem precisar do menu)
    listar_todos_modulos()

    print(f"\n  {N} módulos indexados | {N}×{N} Matriz de Adjacência configurada.")
    print("  Abrindo painel de controle interativo...\n")
    time.sleep(1.0)

    # 3. Abre o menu interativo para o usuário explorar a rede
    rodar_menu_interativo()

    # 4. Monta o resumo de retorno para o main.py passar à IA
    operacionais = [
        MODULOS_COLONIA[c]["descricao"][0]
        for c in NOMES_MODULOS
        if MODULOS_COLONIA[c]["status_codigo"] == 1
    ]
    inativos = [
        MODULOS_COLONIA[c]["descricao"][0]
        for c in NOMES_MODULOS
        if MODULOS_COLONIA[c]["status_codigo"] == 0
    ]
    alertas = [
        MODULOS_COLONIA[c]["descricao"][0]
        for c in NOMES_MODULOS
        if MODULOS_COLONIA[c]["status_codigo"] in [2, 3]
    ]
    consumo_ativo = sum(
        MODULOS_COLONIA[c]["consumo_kw"]
        for c in NOMES_MODULOS
        if MODULOS_COLONIA[c]["status_codigo"] == 1
    )

    return {
        "modulos_operacionais": operacionais,
        "modulos_inativos": inativos,
        "modulos_em_alerta": alertas,
        "total_modulos": N,
        "total_arestas_grafo": sum(
            1 for i in range(N) for j in range(i + 1, N)
            if MATRIZ_ADJACENCIA[i][j] > 0
        ),
        "consumo_ativo_kw": consumo_ativo,
        "status_rede": "parcialmente_operacional" if inativos else "totalmente_operacional",
    }


# =====================================================================
# EXECUÇÃO STANDALONE (testes isolados sem o pipeline completo)
# =====================================================================
if __name__ == "__main__":
    print("[SIGIC] Usando dados simulados para teste.\n")

    # Dados simulados para rodar sem o main.py
    res_f2_simulado = {
        "pousados":  ["MOD-ENE-01", "MOD-HAB-01", "MOD-LOG-01"],
        "em_espera": ["MOD-MED-01", "MOD-LAB-01"],
        "alertas":   [],
    }
    res_f3_simulado = {
        "diagnostico_eficiencia": {"status": "ENERGIA EXCEDENTE"},
    }

    executar_fase4(res_f2_simulado, res_f3_simulado)

