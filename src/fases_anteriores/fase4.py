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
import os


def limpar_tela():
    """Limpa o terminal para manter a interface CLI organizada."""
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\n[Pressione Enter para continuar...]")


# =====================================================================
# BLOCO 1 — MODELAGEM DE DADOS
# Estrutura: Dicionário hierárquico (acesso O(1) por chave)
# =====================================================================

MODULOS_COLONIA: dict = {
    "habitacao": {
        "descricao": ("Habitação", "Módulo residencial da tripulação"),
        "coordenadas_xy": (100, 200),
        "necessidade_comunicacao": ("Wi-Fi mesh interno", 10, "media"),
        "consumo_kw": 45.0,
        "prioridade": 1,
        "capacidade": "12 tripulantes",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "centro_controle": {
        "descricao": (
            "Centro de Controle",
            "Núcleo de comando e monitoramento da base",
        ),
        "coordenadas_xy": (200, 300),
        "necessidade_comunicacao": ("Ethernet + RF interno", 100, "alta"),
        "consumo_kw": 60.0,
        "prioridade": 2,
        "capacidade": "8 estações de trabalho",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "armazenamento_energia": {
        "descricao": (
            "Armazenamento de Energia",
            "Baterias e painéis solares da colônia",
        ),
        "coordenadas_xy": (300, 100),
        "necessidade_comunicacao": ("RF interno", 5, "alta"),
        "consumo_kw": 10.0,
        "prioridade": 3,
        "capacidade": "500 kWh",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "agricultura": {
        "descricao": (
            "Agricultura",
            "Estufas pressurizadas para produção de alimentos",
        ),
        "coordenadas_xy": (300, 500),
        "necessidade_comunicacao": ("Wi-Fi mesh interno", 2, "baixa"),
        "consumo_kw": 35.0,
        "prioridade": 4,
        "capacidade": "200 m² de área cultivável",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "laboratorio": {
        "descricao": (
            "Laboratório Científico",
            "Pesquisa geológica, biológica e química",
        ),
        "coordenadas_xy": (500, 400),
        "necessidade_comunicacao": ("Ethernet + laser Terra", 50, "media"),
        "consumo_kw": 55.0,
        "prioridade": 7,
        "capacidade": "6 bancadas de pesquisa",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "comunicacao": {
        "descricao": ("Comunicação", "Antenas de rádio e link laser com a Terra"),
        "coordenadas_xy": (500, 200),
        "necessidade_comunicacao": ("Laser 10 Gbps + UHF backup", 1000, "alta"),
        "consumo_kw": 40.0,
        "prioridade": 5,
        "capacidade": "Link laser 10 Gbps / Rádio UHF backup",
        "status": "operacional",
        "status_codigo": 1,
    },
    "suporte_medico": {
        "descricao": ("Suporte Médico", "Enfermaria, UTI e estoque de medicamentos"),
        "coordenadas_xy": (100, 400),
        "necessidade_comunicacao": ("RF interno dedicado", 20, "alta"),
        "consumo_kw": 30.0,
        "prioridade": 2,
        "capacidade": "4 leitos de UTI",
        "status": "aguardando_pouso",
        "status_codigo": 0,
    },
    "producao_oxigenio": {
        "descricao": (
            "Produção de Oxigênio",
            "Eletrolisadores e sistemas de reciclagem de CO₂",
        ),
        "coordenadas_xy": (400, 300),
        "necessidade_comunicacao": ("RF interno dedicado", 5, "alta"),
        "consumo_kw": 50.0,
        "prioridade": 1,
        "capacidade": "Até 15 kg O₂/dia",
        "status": "operacional",
        "status_codigo": 1,
    },
}

# =====================================================================
# BLOCO 2 E 3 — ÍNDICES E MATRIZ DE ADJACÊNCIA
# =====================================================================

NOMES_MODULOS: list = [
    "habitacao",
    "centro_controle",
    "armazenamento_energia",
    "agricultura",
    "laboratorio",
    "comunicacao",
    "suporte_medico",
    "producao_oxigenio",
]
N = len(NOMES_MODULOS)

MATRIZ_ADJACENCIA: list = [
    [0, 140, 220, 360, 0, 0, 200, 0],
    [140, 0, 220, 0, 320, 320, 140, 200],
    [220, 220, 0, 400, 0, 220, 0, 220],
    [360, 0, 400, 0, 220, 0, 220, 220],
    [0, 320, 0, 220, 0, 200, 0, 140],
    [0, 320, 220, 0, 200, 0, 0, 140],
    [200, 140, 0, 220, 0, 0, 0, 320],
    [0, 200, 220, 220, 140, 140, 320, 0],
]

# =====================================================================
# BLOCO 4 — INTEGRAÇÃO COM O PIPELINE
# =====================================================================


def sincronizar_com_pipeline(resultado_fase2: dict, resultado_fase3: dict):
    pousados = resultado_fase2.get("pousados", []) if resultado_fase2 else []
    em_espera = resultado_fase2.get("em_espera", []) if resultado_fase2 else []

    modulos_transporte_fase2 = [
        "habitacao",
        "centro_controle",
        "armazenamento_energia",
        "laboratorio",
        "suporte_medico",
    ]

    for chave_sigic in modulos_transporte_fase2:
        if chave_sigic in pousados:
            MODULOS_COLONIA[chave_sigic]["status"] = "operacional"
            MODULOS_COLONIA[chave_sigic]["status_codigo"] = 1
        elif chave_sigic in em_espera:
            MODULOS_COLONIA[chave_sigic]["status"] = "inativo"
            MODULOS_COLONIA[chave_sigic]["status_codigo"] = 0

    if resultado_fase3:
        status_energia = resultado_fase3.get("diagnostico_eficiencia", {}).get(
            "status", ""
        )
        if "CRÍTICO" in status_energia:
            MODULOS_COLONIA["armazenamento_energia"]["status"] = "crítico"
            MODULOS_COLONIA["armazenamento_energia"]["status_codigo"] = 3
        elif "MODERADO" in status_energia or "ALERTA" in status_energia:
            if MODULOS_COLONIA["armazenamento_energia"]["status_codigo"] == 1:
                MODULOS_COLONIA["armazenamento_energia"]["status"] = "alerta"
                MODULOS_COLONIA["armazenamento_energia"]["status_codigo"] = 2


def exibir_resumo_sincronizacao(resultado_fase2: dict):
    print("\n  [SIGIC] Sincronizando rede com resultados do pouso orbital...")
    time.sleep(0.6)

    pousados = resultado_fase2.get("pousados", []) if resultado_fase2 else []
    em_espera = resultado_fase2.get("em_espera", []) if resultado_fase2 else []

    modulos_transporte_fase2 = [
        "habitacao",
        "centro_controle",
        "armazenamento_energia",
        "laboratorio",
        "suporte_medico",
    ]

    for chave_sigic in modulos_transporte_fase2:
        nome = MODULOS_COLONIA[chave_sigic]["descricao"][0]
        if chave_sigic in pousados:
            print(f"    ✅  {nome}: ATIVADO na rede")
        elif chave_sigic in em_espera:
            print(f"    ⚫  {nome}: INATIVO (retido em órbita)")

    sem_correspondencia = ["comunicacao", "producao_oxigenio", "agricultura"]
    for chave in sem_correspondencia:
        nome = MODULOS_COLONIA[chave]["descricao"][0]
        status = MODULOS_COLONIA[chave]["status"]
        print(f"    🔵  {nome}: {status.upper()} (infraestrutura base da colônia)")
    print()


# =====================================================================
# BLOCO 5, 6 e 7 — EXIBIÇÃO E ALGORITMOS (MANTIDOS IGUAIS E COM LIMPEZA DE TELA)
# =====================================================================


def exibir_cabecalho_sigic():
    limpar_tela()
    print("=" * 85)
    print(
        "  SIGIC — Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia  ".center(
            85
        )
    )
    print("Base Aurora Siger | Fase 4".center(85))
    print("=" * 85)


def exibir_matriz_adjacencia():
    limpar_tela()
    print("=" * 85)
    print("  REDE DE INFRAESTRUTURA — MATRIZ DE ADJACÊNCIA (distâncias em metros)  ")
    print(
        "  (0 = sem conexão direta | módulos inativos mantêm arestas para futura ativação)"
    )
    print("=" * 85)

    abreviacoes = ["HAB", "CTR", "ENE", "AGR", "LAB", "COM", "MED", "OXI"]
    mapa_status = {1: "🟢", 2: "🟡", 3: "🔴", 0: "⚫"}

    print(f"{'':>6}", end="")
    for abrev in abreviacoes:
        print(f"{abrev:>6}", end="")
    print(f"\n{'':>6}" + "-" * (6 * N))

    for i in range(N):
        chave = NOMES_MODULOS[i]
        icone = mapa_status.get(MODULOS_COLONIA[chave]["status_codigo"], "?")
        print(f"{abreviacoes[i]:>4}{icone}|", end="")
        for j in range(N):
            valor = MATRIZ_ADJACENCIA[i][j]
            print(f"{'  —':>6}" if valor == 0 else f"{valor:>6}", end="")
        print()

    print("\n  Legenda (abreviação → módulo | ícone = status atual):")
    for i, (abrev, chave) in enumerate(zip(abreviacoes, NOMES_MODULOS)):
        nome = MODULOS_COLONIA[chave]["descricao"][0]
        icone = mapa_status.get(MODULOS_COLONIA[chave]["status_codigo"], "?")
        status = MODULOS_COLONIA[chave]["status"]
        print(f"    {abrev} → {nome}  {icone} {status}")
    print("=" * 85)
    pausar()


def consultar_status_modulo(chave: str):
    limpar_tela()
    if chave not in MODULOS_COLONIA:
        return

    modulo = MODULOS_COLONIA[chave]
    mapa_status = {
        1: "🟢 OPERACIONAL",
        2: "🟡 ALERTA",
        3: "🔴 CRÍTICO",
        0: "⚫ INATIVO",
    }

    print("=" * 85)
    print(f"  STATUS DO MÓDULO: {modulo['descricao'][0].upper()}")
    print("=" * 85)
    print(
        f"  Status atual : {mapa_status.get(modulo['status_codigo'], 'DESCONHECIDO')}"
    )
    print(f"  Descrição    : {modulo['descricao'][1]}")
    print(f"  Consumo      : {modulo['consumo_kw']} kW")

    idx = NOMES_MODULOS.index(chave)
    vizinhos = [
        f"{MODULOS_COLONIA[NOMES_MODULOS[j]]['descricao'][0]} ({MATRIZ_ADJACENCIA[idx][j]}m)"
        for j in range(N)
        if MATRIZ_ADJACENCIA[idx][j] > 0
    ]
    if vizinhos:
        print(f"  Conexões     : {', '.join(vizinhos)}")
    print("=" * 85)
    pausar()


def listar_todos_modulos():
    limpar_tela()
    mapa_status = {1: "🟢", 2: "🟡", 3: "🔴", 0: "⚫"}

    print("=" * 85)
    print("  INVENTÁRIO DE MÓDULOS — BASE AURORA SIGER")
    print("=" * 85)
    for i, chave in enumerate(NOMES_MODULOS, start=1):
        modulo = MODULOS_COLONIA[chave]
        icone = mapa_status.get(modulo["status_codigo"], "?")
        print(
            f"  {i:<2}. {modulo['descricao'][0]:<25} | {modulo['consumo_kw']:>5} kW | {icone} {modulo['status']}"
        )
    print("=" * 85)
    pausar()


# ---- ALGORITMOS (Simplificados para exibição, lógica mantida intacta) ----
def algoritmo_dijkstra(origem: str, destino: str):
    limpar_tela()
    idx_origem, idx_destino = NOMES_MODULOS.index(origem), NOMES_MODULOS.index(destino)
    dist, anterior, visitado = [float("inf")] * N, [-1] * N, [False] * N
    dist[idx_origem] = 0

    for _ in range(N):
        u = -1
        for v in range(N):
            if not visitado[v] and (u == -1 or dist[v] < dist[u]):
                u = v
        if u == -1 or dist[u] == float("inf"):
            break
        visitado[u] = True
        if u == idx_destino:
            break
        for v in range(N):
            if MATRIZ_ADJACENCIA[u][v] > 0 and not visitado[v]:
                if dist[u] + MATRIZ_ADJACENCIA[u][v] < dist[v]:
                    dist[v], anterior[v] = dist[u] + MATRIZ_ADJACENCIA[u][v], u

    if dist[idx_destino] == float("inf"):
        print(f"\n  [!] Sem caminho entre '{origem}' e '{destino}'.")
        pausar()
        return

    caminho = []
    atual = idx_destino
    while atual != -1:
        caminho.append(NOMES_MODULOS[atual])
        atual = anterior[atual]
    caminho.reverse()

    print("=" * 85)
    print("  DIJKSTRA — CAMINHO DE MENOR DISTÂNCIA")
    print(
        f"  Caminho: {' → '.join([MODULOS_COLONIA[c]['descricao'][0] for c in caminho])}"
    )
    print(f"  Distância total: {dist[idx_destino]} metros")
    print("=" * 85)
    pausar()


def detectar_bridges():
    limpar_tela()
    timestamp, visitado, discovery_time, low, bridges = (
        [0],
        [False] * N,
        [-1] * N,
        [-1] * N,
        [],
    )

    def dfs_bridge(u, pai=-1):
        visitado[u] = True
        discovery_time[u] = low[u] = timestamp[0]
        timestamp[0] += 1
        for v in range(N):
            if MATRIZ_ADJACENCIA[u][v] == 0:
                continue
            if not visitado[v]:
                dfs_bridge(v, u)
                if low[v] > discovery_time[u]:
                    bridges.append(
                        (
                            MODULOS_COLONIA[NOMES_MODULOS[u]]["descricao"][0],
                            MODULOS_COLONIA[NOMES_MODULOS[v]]["descricao"][0],
                            MATRIZ_ADJACENCIA[u][v],
                        )
                    )
                low[u] = min(low[u], low[v])
            elif v != pai:
                low[u] = min(low[u], discovery_time[v])

    for i in range(N):
        if not visitado[i]:
            dfs_bridge(i)

    print("=" * 85)
    print("  CONEXÕES CRÍTICAS — BRIDGES")
    if not bridges:
        print("  ✅ Nenhuma conexão crítica. Rede tolerante a falhas.")
    else:
        for i, (mod_a, mod_b, dist) in enumerate(bridges, start=1):
            print(f"    [{i}] {mod_a} ←→ {mod_b}  ({dist} m)")
    print("=" * 85)
    pausar()


def algoritmo_bfs(origem: str):
    limpar_tela()
    idx_origem = NOMES_MODULOS.index(origem)
    visitado, fila, ordem = [False] * N, [idx_origem], []
    visitado[idx_origem] = True

    while fila:
        u = fila.pop(0)
        ordem.append(NOMES_MODULOS[u])
        for v in range(N):
            if MATRIZ_ADJACENCIA[u][v] > 0 and not visitado[v]:
                visitado[v] = True
                fila.append(v)

    print("=" * 85)
    print(
        f"  BFS — BUSCA EM LARGURA a partir de: {MODULOS_COLONIA[origem]['descricao'][0]}"
    )
    for i, chave in enumerate(ordem, start=1):
        print(f"    {i:>2}. {MODULOS_COLONIA[chave]['descricao'][0]}")
    print("=" * 85)
    pausar()


def algoritmo_dfs(origem: str):
    limpar_tela()
    visitado, pilha, ordem = [False] * N, [NOMES_MODULOS.index(origem)], []

    while pilha:
        u = pilha.pop()
        if visitado[u]:
            continue
        visitado[u] = True
        ordem.append(NOMES_MODULOS[u])
        for v in range(N - 1, -1, -1):
            if MATRIZ_ADJACENCIA[u][v] > 0 and not visitado[v]:
                pilha.append(v)

    print("=" * 85)
    print(
        f"  DFS — BUSCA EM PROFUNDIDADE a partir de: {MODULOS_COLONIA[origem]['descricao'][0]}"
    )
    for i, chave in enumerate(ordem, start=1):
        print(f"    {i:>2}. {MODULOS_COLONIA[chave]['descricao'][0]}")
    print("=" * 85)
    pausar()


# =====================================================================
# MENUS
# =====================================================================
def exibir_menu_principal():
    limpar_tela()
    print("-" * 85)
    print("  PAINEL DE CONTROLE — SIGIC (FASE 4)".center(85))
    print("-" * 85)
    print("  [1]  Visualizar Rede (Matriz de Adjacência)")
    print("  [2]  Listar Todos os Módulos")
    print("  [3]  Consultar Status de um Módulo")
    print("  [4]  Executar Dijkstra (Caminho Mínimo)")
    print("  [5]  Executar BFS (Busca em Largura) ")
    print("  [6]  Executar DFS (Busca em Profundidade)")
    print("  [7]  Detectar Conexões Críticas (Bridges)")
    print("  [0]  Encerrar SIGIC e retornar ao pipeline")
    print("-" * 85)


def menu_selecionar_modulo(prompt_texto: str) -> str:
    print("\n  Módulos disponíveis:")
    for i, chave in enumerate(NOMES_MODULOS, start=1):
        print(f"    [{i}] {MODULOS_COLONIA[chave]['descricao'][0]}")
    escolha = input(f"\n  {prompt_texto} (número): ").strip()
    try:
        idx = int(escolha) - 1
        if 0 <= idx < N:
            return NOMES_MODULOS[idx]
    except ValueError:
        pass
    return ""


def rodar_menu_interativo():
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
            origem = menu_selecionar_modulo("Módulo de origem")
            if origem:
                destino = menu_selecionar_modulo("Módulo de destino")
                if destino:
                    algoritmo_dijkstra(origem, destino)
        elif opcao == "5":
            origem = menu_selecionar_modulo("Módulo de origem")
            if origem:
                algoritmo_bfs(origem)
        elif opcao == "6":
            origem = menu_selecionar_modulo("Módulo de origem")
            if origem:
                algoritmo_dfs(origem)
        elif opcao == "7":
            detectar_bridges()
        elif opcao == "0":
            break


# =====================================================================
# PONTO DE ENTRADA
# =====================================================================
def executar_fase4(resultado_fase2: dict, resultado_fase3: dict) -> dict:
    exibir_cabecalho_sigic()
    sincronizar_com_pipeline(resultado_fase2, resultado_fase3)
    exibir_resumo_sincronizacao(resultado_fase2)
    pausar()

    rodar_menu_interativo()

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

    return {
        "modulos_operacionais": operacionais,
        "modulos_inativos": inativos,
        "modulos_em_alerta": alertas,
        "status_rede": (
            "parcialmente_operacional" if inativos else "totalmente_operacional"
        ),
    }
