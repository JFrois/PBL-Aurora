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

# --- Correção 25/05 --- 2 #
def calcular_regressao(dados_historicos, vento_atual):
    """Calcula a Regressão Linear Simples (Mínimos Quadrados) e o R²."""
    n = len(dados_historicos)
    soma_x  = sum(p[0] for p in dados_historicos)
    soma_y  = sum(p[1] for p in dados_historicos)
    soma_xy = sum(p[0] * p[1] for p in dados_historicos)
    soma_x2 = sum(p[0] ** 2 for p in dados_historicos)

    m = (n * soma_xy - soma_x * soma_y) / (n * soma_x2 - soma_x ** 2)
    b = (soma_y - m * soma_x) / n
    previsao = m * vento_atual + b

    # --- Cálculo do R² ---
    media_y = soma_y / n
    ss_tot  = sum((p[1] - media_y) ** 2 for p in dados_historicos)
    ss_res  = sum((p[1] - (m * p[0] + b)) ** 2 for p in dados_historicos)
    r2      = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

    print(f"  [Regressão] m={m:.4f}  b={b:.4f}  R²={r2:.4f} "
          f"({'excelente ajuste' if r2 >= 0.95 else 'ajuste aceitável'})")

    return max(0.0, min(previsao, 80.0))
# --- Correção 25/05 --- 2 #

# --- Correção 25/05 --- 1 #

def obter_dados_colonia(vento_atual):
    """
    Retorna a estrutura hierárquica completa da colônia.
    Navegação: sistema_energetico -> tipo_geracao -> solar / eolico

    """
    geracao_eolica = calcular_regressao(HISTORICO_EOLICO, vento_atual)

    return {
        "clima_vento": vento_atual,
        "sistema_energetico": {
            "tipo_geracao": {
                "solar": {
                    "capacidade_mw": 50.0,
                    "status": "ativo",
                },
                "eolico": {
                    "velocidade_vento_kmh": vento_atual,
                    "previsao_geracao_mw": round(geracao_eolica, 2),
                    "status": "ativo",
                },
            },
            "bateria_kwh": 50.0,
        },
        "sistemas": {
            "Suporte Médico": {"consumo": 25.0, "essencial": True,  "status": "ligado"},
            "Habitação":      {"consumo": 30.0, "essencial": True,  "status": "ligado"},
            "Laboratório":    {"consumo": 20.0, "essencial": False, "status": "ligado"},
        },
    }

# --- Correção 25/05 --- 1 #

# --- MÓDULO 3: PREVISÃO (Pessoa 3) ---



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
# --- Correção 25/05 --- 3 #
def aplicar_logica_de_decisao(dados_colonia, diagnostico):
    """
    Toma decisões automáticas combinando o status do diagnóstico E/OU
    o nível absoluto da bateria.

    Regras compostas (operadores lógicos explícitos):
      - (ALERTA CRÍTICO ou RISCO MODERADO) AND bateria baixa → corte imediato + modo economia
      - (ALERTA CRÍTICO ou RISCO MODERADO) com bateria ok   → corte de não-essenciais
      - ENERGIA EXCEDENTE AND bateria não cheia             → sugestão de armazenamento
    """
    acoes = []
    bateria = dados_colonia["sistema_energetico"]["bateria_kwh"]
    status  = diagnostico["status"]

    # Regra 1: situação crítica OU moderada AND bateria abaixo de 20 kWh
    if (status in ["ALERTA CRÍTICO", "RISCO MODERADO"]) and (bateria < 20.0):
        acoes.append("MODO ECONOMIA ATIVADO: bateria crítica + déficit de geração.")
        for nome, sys in dados_colonia["sistemas"].items():
            if not sys["essencial"]:
                sys["status"] = "desligado"
                acoes.append(f"  → Corte imediato: {nome} desligado (não-essencial, bateria crítica).")

    # Regra 2: situação crítica OU moderada com bateria suficiente
    elif status in ["ALERTA CRÍTICO", "RISCO MODERADO"]:
        for nome, sys in dados_colonia["sistemas"].items():
            if not sys["essencial"] and sys["status"] == "ligado":
                sys["status"] = "desligado"
                acoes.append(f"  → Corte preventivo: {nome} desligado (déficit de geração).")

    # Regra 3: excedente AND bateria ainda não na capacidade máxima (100 kWh)
    elif status == "ENERGIA EXCEDENTE" and bateria < 100.0:
        acoes.append(f"  → Armazenando excedente de {diagnostico.get('energia_para_armazenar', 0):.2f} MW na bateria.")

    return acoes
# --- Correção 25/05 --- 3 #

# --- EXECUÇÃO INTEGRADA ---
# --- Correção 25/05 --- 4 #
def executar_fase3():
    print("\n" + "=" * 85)
    print("INICIANDO FASE 3: SISTEMA INTELIGENTE DA COLÓNIA".center(85))
    print("=" * 85)

    # 1. Estrutura hierárquica de dados
    VENTO_ATUAL = 36.0
    dados_colonia = obter_dados_colonia(VENTO_ATUAL)

    # 2. Navegando a hierarquia para obter os valores de geração
    solar  = dados_colonia["sistema_energetico"]["tipo_geracao"]["solar"]["capacidade_mw"]
    eolico = dados_colonia["sistema_energetico"]["tipo_geracao"]["eolico"]["previsao_geracao_mw"]
    geracao_total = solar + eolico

    print(f"\n  [Hierarquia] sistema_energetico → tipo_geracao → solar={solar} MW | eolico={eolico:.2f} MW")

    # 3. Consumo total dos sistemas ativos
    consumo_total = sum(
        s["consumo"]
        for s in dados_colonia["sistemas"].values()
        if s["status"] == "ligado"
    )

    bateria = dados_colonia["sistema_energetico"]["bateria_kwh"]
    balanco = geracao_total - consumo_total

    # 4. Diagnóstico de eficiência energética
    diagnostico = analisar_uso_energia(geracao_total, consumo_total, bateria)

    # 5. Lógica de decisão composta (AND / OR explícitos)
    acoes_tomadas = aplicar_logica_de_decisao(dados_colonia, diagnostico)

    # --- Relatório final ---
    print("\n" + "=" * 85)
    print("RESUMO TÉCNICO - FASE 3 (COLÔNIA)".center(85))
    print(f"  Geração Total  : {geracao_total:.2f} MW  (Solar {solar} + Eólico {eolico:.2f})")
    print(f"  Consumo Total  : {consumo_total:.2f} MW")
    print(f"  Balanço        : {balanco:.2f} MW")
    print(f"  Bateria        : {bateria:.2f} kWh")
    print(f"  Status         : {diagnostico['status']}")
    print(f"  Mensagem       : {diagnostico['mensagem']}")
    print(f"  Ações tomadas  :")
    if acoes_tomadas:
        for a in acoes_tomadas:
            print(f"    {a}")
    else:
        print("    Nenhuma ação necessária.")
    print("=" * 85)

    return {
        "vento_registrado": dados_colonia["clima_vento"],
        "geracao_solar_mw": solar,
        "geracao_eolica_mw": eolico,
        "geracao_total_mw": round(geracao_total, 2),
        "consumo_total_mw": round(consumo_total, 2),
        "bateria_kwh": bateria,
        "diagnostico_eficiencia": diagnostico,
        "acoes_seguranca": acoes_tomadas,
    }
# --- Correção 25/05 --- 4 #
