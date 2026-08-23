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
    """Calcula a Regressão Linear Simples (Mínimos Quadrados) e o R²."""
    n = len(dados_historicos)
    soma_x = sum(p[0] for p in dados_historicos)
    soma_y = sum(p[1] for p in dados_historicos)
    soma_xy = sum(p[0] * p[1] for p in dados_historicos)
    soma_x2 = sum(p[0] ** 2 for p in dados_historicos)

    m = (n * soma_xy - soma_x * soma_y) / (n * soma_x2 - soma_x**2)
    b = (soma_y - m * soma_x) / n
    previsao = m * vento_atual + b

    # Cálculo do R²
    media_y = soma_y / n
    ss_tot = sum((p[1] - media_y) ** 2 for p in dados_historicos)
    ss_res = sum((p[1] - (m * p[0] + b)) ** 2 for p in dados_historicos)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

    print(
        f"  [Regressão] m={m:.4f}  b={b:.4f}  R²={r2:.4f} "
        f"({'excelente ajuste' if r2 >= 0.95 else 'ajuste aceitável'})"
    )

    return max(0.0, min(previsao, 80.0))


# Recebe os dados reais de quem pousou na Fase 2
def obter_dados_colonia(vento_atual, res_f2):
    geracao_eolica = calcular_regressao(HISTORICO_EOLICO, vento_atual)

    # Catálogo de consumo dos módulos de transporte
    info_modulos_transporte = {
        "suporte_medico": {
            "nome": "Suporte Médico",
            "consumo": 30.0,
            "essencial": True,
        },
        "habitacao": {"nome": "Habitação", "consumo": 45.0, "essencial": True},
        "laboratorio": {"nome": "Laboratório", "consumo": 55.0, "essencial": False},
        "centro_controle": {
            "nome": "Centro de Controle",
            "consumo": 60.0,
            "essencial": True,
        },
        # armazenamento_energia não entra no array de consumo, ele é a bateria
    }

    sistemas_dinamicos = {}

    # 1. Módulos Base que já estavam na colônia
    sistemas_dinamicos["Produção de Oxigênio"] = {
        "consumo": 50.0,
        "essencial": True,
        "status": "ligado",
    }
    sistemas_dinamicos["Comunicação"] = {
        "consumo": 40.0,
        "essencial": True,
        "status": "ligado",
    }

    # 2. Adiciona dinamicamente APENAS os que pousaram com sucesso
    pousados = res_f2.get("pousados", []) if res_f2 else []
    for mod_id in pousados:
        if mod_id in info_modulos_transporte:
            nome = info_modulos_transporte[mod_id]["nome"]
            sistemas_dinamicos[nome] = {
                "consumo": info_modulos_transporte[mod_id]["consumo"],
                "essencial": info_modulos_transporte[mod_id]["essencial"],
                "status": "ligado",
            }

    return {
        "clima_vento": vento_atual,
        "sistema_energetico": {
            "tipo_geracao": {
                "solar": {"capacidade_mw": 50.0, "status": "ativo"},
                "eolico": {
                    "velocidade_vento_kmh": vento_atual,
                    "previsao_geracao_mw": round(geracao_eolica, 2),
                    "status": "ativo",
                },
            },
            "bateria_kwh": 50.0,
        },
        "sistemas": sistemas_dinamicos,
    }


def analisar_uso_energia(geracao, consumo, reserva):
    saldo = geracao - consumo
    if consumo > geracao:
        deficit = consumo - geracao
        if reserva >= deficit:
            return {
                "status": "RISCO MODERADO",
                "mensagem": "Consumo maior que geração. Usar reserva.",
                "saldo": round(saldo, 2),
                "reserva_restante": round(reserva - deficit, 2),
            }
        else:
            return {
                "status": "ALERTA CRÍTICO",
                "mensagem": "Consumo maior que geração e reserva insuficiente.",
                "saldo": round(saldo, 2),
                "reserva_restante": round(reserva, 2),
            }
    elif geracao > consumo:
        excedente = geracao - consumo
        return {
            "status": "ENERGIA EXCEDENTE",
            "mensagem": "Geração maior que consumo. Armazenar excedente.",
            "saldo": round(saldo, 2),
            "energia_para_armazenar": round(excedente, 2),
        }
    else:
        return {
            "status": "EQUILÍBRIO",
            "mensagem": "Geração igual ao consumo.",
            "saldo": round(saldo, 2),
        }


def aplicar_logica_de_decisao(dados_colonia, diagnostico, balanco):
    acoes = []
    bateria = dados_colonia["sistema_energetico"]["bateria_kwh"]
    status = diagnostico["status"]

    if (status in ["ALERTA CRÍTICO", "RISCO MODERADO"]) and (
        bateria < 20.0 or balanco < -5.0
    ):
        acoes.append("MODO ECONOMIA ATIVADO: bateria crítica + déficit.")
        for nome, sys in dados_colonia["sistemas"].items():
            if not sys["essencial"]:
                sys["status"] = "desligado"
                acoes.append(f"  → Corte imediato: {nome} desligado.")
    elif status in ["ALERTA CRÍTICO", "RISCO MODERADO"]:
        for nome, sys in dados_colonia["sistemas"].items():
            if not sys["essencial"] and sys["status"] == "ligado":
                sys["status"] = "desligado"
                acoes.append(f"  → Corte preventivo: {nome} desligado.")
    elif status == "ENERGIA EXCEDENTE" and bateria < 100.0:
        acoes.append(
            f"  → Armazenando excedente de {diagnostico.get('energia_para_armazenar', 0):.2f} MW."
        )

    return acoes


def executar_fase3(res_f2: dict):
    print("\n" + "=" * 85)
    print("INICIANDO FASE 3: SISTEMA INTELIGENTE DA COLÓNIA".center(85))
    print("=" * 85)

    dados_colonia = obter_dados_colonia(36.0, res_f2)

    solar = dados_colonia["sistema_energetico"]["tipo_geracao"]["solar"][
        "capacidade_mw"
    ]
    eolico = dados_colonia["sistema_energetico"]["tipo_geracao"]["eolico"][
        "previsao_geracao_mw"
    ]
    geracao_total = solar + eolico

    consumo_total = sum(
        s["consumo"]
        for s in dados_colonia["sistemas"].values()
        if s["status"] == "ligado"
    )
    bateria = dados_colonia["sistema_energetico"]["bateria_kwh"]
    balanco = geracao_total - consumo_total

    diagnostico = analisar_uso_energia(geracao_total, consumo_total, bateria)
    acoes_tomadas = aplicar_logica_de_decisao(dados_colonia, diagnostico, balanco)

    print("\n" + "=" * 85)
    print("RESUMO TÉCNICO - FASE 3 (COLÔNIA)".center(85))
    print(
        f"  Geração Total  : {geracao_total:.2f} MW  (Solar {solar} + Eólico {eolico:.2f})"
    )
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
