# Dados históricos do comportamento dos ventos vs. geração de energia na colónia
HISTORICO_EOLICO = [
    (5.0, 3.0),
    (10.0, 8.0),
    (15.0, 14.0),
    (20.0, 19.0),
    (30.0, 29.0),
    (36.0, 30.0),
    (45.0, 44.0),
    (60.0, 63.0),
]


def calcular_regressao(dados_historicos, vento_atual):
    """
    Calcula a Regressão Linear Simples através do método dos Mínimos Quadrados.
    Descobre a equação da reta (y = mx + b) e retorna a previsão 'y' para um dado 'x'.
    Isto cumpre a regra de NÃO utilizar bibliotecas externas (como scikit-learn).
    """
    n = len(dados_historicos)
    soma_x = sum(p[0] for p in dados_historicos)
    soma_y = sum(p[1] for p in dados_historicos)
    soma_xy = sum(p[0] * p[1] for p in dados_historicos)
    soma_x2 = sum(p[0] ** 2 for p in dados_historicos)

    # Cálculo do coeficiente angular (m) e linear (b)
    m = (n * soma_xy - soma_x * soma_y) / (n * soma_x2 - soma_x**2)
    b = (soma_y - m * soma_x) / n

    # y = mx + b
    previsao = m * vento_atual + b

    # Limita fisicamente a previsão entre 0 MW e a capacidade máxima teórica (80 MW)
    return max(0.0, min(previsao, 80.0))


def executar_fase3():
    """
    Gere o balanceamento de carga da colónia.
    Desliga sistemas não essenciais em caso de défice energético iminente.
    """
    print("\n" + "=" * 85)
    print("INICIANDO FASE 3: SISTEMA INTELIGENTE DA COLÓNIA".center(85))
    print("=" * 85)

    # Estruturação hierárquica em Dicionários Aninhados
    dados_colonia = {
        "bateria_pct": 25.0,
        "clima_vento": 36.0,
        "sistemas": {
            "Suporte Médico": {"consumo": 25.0, "essencial": True, "status": "ligado"},
            "Habitação": {"consumo": 30.0, "essencial": True, "status": "ligado"},
            "Laboratório": {"consumo": 20.0, "essencial": False, "status": "ligado"},
        },
    }

    # 1. Executa a Previsão Matemática (Regressão)
    geracao_eolica = calcular_regressao(HISTORICO_EOLICO, dados_colonia["clima_vento"])

    # 2. Calcula Geração Total (Considerando que o sistema Solar produz uns 50 MW fixos neste teste)
    geracao_total = 50.0 + geracao_eolica

    # 3. Analisa o Consumo somando as cargas apenas dos módulos ligados
    consumo_total = sum(
        s["consumo"]
        for s in dados_colonia["sistemas"].values()
        if s["status"] == "ligado"
    )

    # 4. Avalia a Eficiência e o Balanço Energético
    balanco = geracao_total - consumo_total
    acoes_tomadas = []

    # Lógica de Decisão Automática (Triagem de Carga)
    if dados_colonia["bateria_pct"] < 30 or balanco < 0:
        for nome, sys in dados_colonia["sistemas"].items():
            if not sys["essencial"]:
                sys["status"] = "desligado"
                acoes_tomadas.append(
                    f"Corte de energia no {nome} efetuado para preservar baterias."
                )

    return {
        "vento_registrado": dados_colonia["clima_vento"],
        "geracao_prevista_mw": round(geracao_total, 2),
        "consumo_total_mw": round(consumo_total, 2),
        "balanco_mw": round(balanco, 2),
        "acoes_seguranca": acoes_tomadas,
    }
