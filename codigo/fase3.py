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


# --- MÓDULO 3: PREVISÃO (Pessoa 3) ---
def calcular_regressao(dados_historicos, vento_atual):
    """Calcula a Regressão Linear Simples através do método dos Mínimos Quadrados."""
    n = len(dados_historicos)
    soma_x = sum(p[0] for p in dados_historicos)
    soma_y = sum(p[1] for p in dados_historicos)
    soma_xy = sum(p[0] * p[1] for p in dados_historicos)
    soma_x2 = sum(p[0] ** 2 for p in dados_historicos)

    m = (n * soma_xy - soma_x * soma_y) / (n * soma_x2 - soma_x**2)
    b = (soma_y - m * soma_x) / n
    previsao = m * vento_atual + b
    return max(0.0, min(previsao, 80.0))


# --- MÓDULO 4: ANÁLISE DE EFICIÊNCIA (Pessoa 4) ---
def analisar_uso_energia(geracao, consumo, reserva):
    """
    Compara a energia gerada com o consumo e a reserva da bateria.
    Retorna o diagnóstico de risco, excedente ou equilíbrio.
    """
    saldo = geracao - consumo
    if consumo > geracao:
        deficit = consumo - geracao
        if reserva >= deficit:
            return {
                "status": "RISCO MODERADO",
                "mensagem": "Consumo maior que geração. Usar reserva de energia.",
                "saldo": round(saldo, 2),
                "reserva_restante": round(reserva - deficit, 2),
            }
        else:
            return {
                "status": "ALERTA CRÍTICO",
                "mensagem": "Consumo maior que geração e reserva insuficiente. Reduzir consumo imediatamente.",
                "saldo": round(saldo, 2),
                "reserva_restante": round(reserva, 2),
            }

    elif geracao > consumo:
        excedente = geracao - consumo
        return {
            "status": "ENERGIA EXCEDENTE",
            "mensagem": "Geração maior que consumo. Sugestão: armazenar energia excedente.",
            "saldo": round(saldo, 2),
            "energia_para_armazenar": round(excedente, 2),
        }

    else:
        return {
            "status": "EQUILÍBRIO",
            "mensagem": "Geração igual ao consumo. Sistema energético estável.",
            "saldo": round(saldo, 2),
        }


# --- EXECUÇÃO INTEGRADA ---
def executar_fase3():
    print("\n" + "=" * 85)
    print("INICIANDO FASE 3: SISTEMA INTELIGENTE DA COLÓNIA".center(85))
    print("=" * 85)

    # Dados da Colônia (Pessoa 1)
    dados_colonia = {
        "bateria_kwh": 50.0,  # Tratado como valor absoluto de reserva para a análise
        "clima_vento": 36.0,
        "sistemas": {
            "Suporte Médico": {"consumo": 25.0, "essencial": True, "status": "ligado"},
            "Habitação": {"consumo": 30.0, "essencial": True, "status": "ligado"},
            "Laboratório": {"consumo": 20.0, "essencial": False, "status": "ligado"},
        },
    }

    # 1. Previsão de Vento
    geracao_eolica = calcular_regressao(HISTORICO_EOLICO, dados_colonia["clima_vento"])
    geracao_total = 50.0 + geracao_eolica  # Solar + Eólica

    # 2. Consumo Atual
    consumo_total = sum(
        s["consumo"]
        for s in dados_colonia["sistemas"].values()
        if s["status"] == "ligado"
    )

    # Balanço energético (geração - consumo)
    balanco = geracao_total - consumo_total

    # 3. Executa a Análise da Pessoa 4
    diagnostico = analisar_uso_energia(
        geracao_total, consumo_total, dados_colonia["bateria_kwh"]
    )
    acoes_tomadas = []

    # 4. Lógica de Decisão (Pessoa 2) baseada no diagnóstico da Pessoa 4
    if diagnostico["status"] in ["ALERTA CRÍTICO", "RISCO MODERADO"]:
        for nome, sys in dados_colonia["sistemas"].items():
            if not sys["essencial"]:
                sys["status"] = "desligado"
                acoes_tomadas.append(
                    f"Corte de energia no {nome} efetuado com base no alerta de eficiência."
                )
    
    print("\n" + "=" * 85)
    print("RESUMO TÉCNICO - FASE 3 (COLÔNIA)".center(85))
    print(f"Balanço Energético: {balanco:.2f} MW")
    print(f"Status do Sistema: {diagnostico['status']}")
    print(f"Ações tomadas: {', '.join(acoes_tomadas) if acoes_tomadas else 'Nenhuma'}")
    print("=" * 85)

    return {
        "vento_registrado": dados_colonia["clima_vento"],
        "geracao_prevista_mw": round(geracao_total, 2),
        "consumo_total_mw": round(consumo_total, 2),
        "diagnostico_eficiencia": diagnostico,
        "acoes_seguranca": acoes_tomadas,
    }
