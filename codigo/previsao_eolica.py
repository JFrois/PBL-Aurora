# ==================================================
#  --- Previsão de Geração Eólica — Colônia Aurora ---
#  Regressão Linear Simples (Mínimos Quadrados Manual)
# ==================================================

# Dados históricos coletados pelas turbinas da colônia
# Formato: (velocidade_vento_km_h, geracao_mw)
HISTORICO_EOLICO = [
    (5.0,  3.0),
    (10.0, 8.0),
    (15.0, 14.0),
    (20.0, 19.0),
    (25.0, 24.0),
    (30.0, 29.0),
    (36.0, 30.0),   # ponto atual da colônia
    (40.0, 38.0),
    (45.0, 44.0),
    (50.0, 51.0),
    (55.0, 57.0),
    (60.0, 63.0),
    (65.0, 67.0),
    (70.0, 71.0),
    (75.0, 74.0),
    (80.0, 76.0),
]


def calcular_coeficientes(dados_historicos):
    """
    Calcula coeficiente angular (m) e linear (b) via mínimos quadrados.
    Retorna (m, b) para y = m*x + b
    """
    n = len(dados_historicos)
    soma_x = sum(par[0] for par in dados_historicos)
    soma_y = sum(par[1] for par in dados_historicos)
    soma_xy = sum(par[0] * par[1] for par in dados_historicos)
    soma_x2 = sum(par[0] ** 2 for par in dados_historicos)

    denominador = n * soma_x2 - soma_x ** 2
    if denominador == 0:
        return 0.0, soma_y / n

    m = (n * soma_xy - soma_x * soma_y) / denominador
    b = (soma_y - m * soma_x) / n
    return m, b


def prever_geracao_eolica(velocidade_km_h, m, b, capacidade_max_mw=80.0):
    """
    Prevê geração eólica (MW) para uma dada velocidade de vento.
    Limita o resultado entre 0 e capacidade máxima das turbinas.
    """
    previsao = m * velocidade_km_h + b
    return max(0.0, min(previsao, capacidade_max_mw))


def calcular_r2(dados_historicos, m, b):
    """Calcula o coeficiente de determinação R² do modelo."""
    n = len(dados_historicos)
    media_y = sum(par[1] for par in dados_historicos) / n

    ss_res = sum((par[1] - (m * par[0] + b)) ** 2 for par in dados_historicos)
    ss_tot = sum((par[1] - media_y) ** 2 for par in dados_historicos)

    if ss_tot == 0:
        return 1.0
    return 1.0 - (ss_res / ss_tot)


def previsao_completa(dados_colonia):
    """
    Ponto de integração principal: recebe o dicionário da colônia
    (retornado por memoria_colonia_aurora) e devolve a geração eólica
    prevista com base no vento atual registrado no clima.
    """
    velocidade_atual = dados_colonia["clima"]["vento_km_h"]
    m, b = calcular_coeficientes(HISTORICO_EOLICO)
    geracao_prevista = prever_geracao_eolica(velocidade_atual, m, b)
    r2 = calcular_r2(HISTORICO_EOLICO, m, b)

    resultado = {
        "velocidade_vento_km_h": velocidade_atual,
        "geracao_prevista_mw": round(geracao_prevista, 2),
        "coeficiente_angular": round(m, 4),
        "coeficiente_linear": round(b, 4),
        "r2": round(r2, 4),
    }
    return resultado


def exibir_previsao(resultado):
    print("=" * 50)
    print("  PREVISÃO DE GERAÇÃO EÓLICA — COLÔNIA AURORA")
    print("=" * 50)
    print(f"  Velocidade do vento   : {resultado['velocidade_vento_km_h']} km/h")
    print(f"  Geração prevista      : {resultado['geracao_prevista_mw']} MW")
    print(f"  Modelo: y = {resultado['coeficiente_angular']}x + {resultado['coeficiente_linear']}")
    print(f"  Precisão do modelo R² : {resultado['r2']}")
    print("=" * 50)


# --- Execução standalone (teste do módulo isolado) ---
if __name__ == "__main__":
    from Lógica_de_decisão import memoria_colonia_aurora

    dados = memoria_colonia_aurora()
    resultado = previsao_completa(dados)
    exibir_previsao(resultado)
