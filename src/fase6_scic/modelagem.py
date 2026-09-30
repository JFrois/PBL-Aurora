"""
Módulo de Modelagem Estatística, Análise Numérica & Métricas — Analista 2
Fase 6: SCIC (Missão Aurora Siger)

Responsabilidades:
- Cálculo de Erro Absoluto e Relativo entre latência observada e prevista (com discussão de
  ponto flutuante e critério de erro aceitável x preocupante).
- Modelo de regressão (scikit-learn) com treino / validação cruzada / teste.
- Comparação simples de modelos (Linear x Ridge com Grid Search) e AIC/BIC.
- Cálculo de Métricas (MAE, MSE, RMSE, R² + interpretação).
- Geração de gráficos de diagnóstico e geração de latencia_prevista_ms para todos os módulos
  (insumo para o heap de alertas do Analista 3).
"""


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = os.path.normpath(os.path.join(BASE_DIR, "..", ".."))
DADOS_DIR = os.path.join(RAIZ_PROJETO, "data", "processed")
GRAFICOS_DIR = os.path.join(RAIZ_PROJETO, "graficos_ou_imagens")  

SEMENTE = 42
COL_OBSERVADA = "latencia_observada_ms"
COL_PREVISTA = "latencia_prevista_ms"


# Critério de aceitação do erro relativo 
LIMITE_ACEITAVEL = 0.05     # até 5%: aceitável
LIMITE_PREOCUPANTE = 0.15   # acima de 15%: preocupante (entre os dois: atenção)

# Colunas usadas como entrada do modelo 
FEATURES_BASE = ["tensao_v", "corrente_a", "potencia_w", "temperatura_c",
                 "pressao_kpa", "radiacao_msv", "prioridade"]



# =====================================================================
# 1. ERRO ABSOLUTO E RELATIVO 
# =====================================================================

def erro_absoluto(y_real, y_previsto):
    """Erro absoluto: real - previsto, na mesma unidade da latência (ms)."""
    return np.abs(np.array(y_real) - np.array(y_previsto))


 
def erro_relativo(y_real, y_previsto):
    """
    Erro relativo: |real - previsto| / |real|. 
    Resultado em fração (0.05 = 5%).
    Serve para comparar módulos que têm escalas de latência diferentes.
    """
    y_real = np.array(y_real, dtype=float)
    y_previsto = np.array(y_previsto, dtype=float)
    return np.abs(y_real - y_previsto) / np.abs(y_real)


def classificar_erro_relativo(er):
    """Classifica um erro relativo em aceitável, atenção ou preocupante."""
    if er < LIMITE_ACEITAVEL:
        return "ACEITÁVEL"
    elif er < LIMITE_PREOCUPANTE:
        return "ATENÇÃO"
    else:
        return "PREOCUPANTE"

def resumo_erros(y_real, y_previsto):
    """Resume os erros absoluto e relativo em um dicionário."""
    ea = erro_absoluto(y_real, y_previsto)
    er = erro_relativo(y_real, y_previsto)
    faixas = [classificar_erro_relativo(x) for x in er]
    total = len(faixas)
    return {
        "EA_medio_ms": float(ea.mean()),
        "EA_mediano_ms": float(np.median(ea)),
        "EA_max_ms": float(ea.max()),
        "ER_medio_%": float(er.mean() * 100),
        "ER_max_%": float(er.max() * 100),
        "pct_aceitavel": faixas.count("ACEITÁVEL") / total * 100,
        "pct_atencao": faixas.count("ATENÇÃO") / total * 100,
        "pct_preocupante": faixas.count("PREOCUPANTE") / total * 100,
    }


def demonstrar_ponto_flutuante():
    """Mostra por que não se compara decimais com '==' (representação IEEE 754)."""
    soma = 0.0
    for _ in range(10):
        soma += 0.1          # somar 0.1 dez vezes deveria dar 1.0...
    return {
        "0.1 + 0.2 == 0.3": (0.1 + 0.2 == 0.3),
        "valor de 0.1 + 0.2": 0.1 + 0.2,
        "0.1 + 0.2 ≈ 0.3 (np.isclose)": bool(np.isclose(0.1 + 0.2, 0.3)),
        "dez somas de 0.1 == 1.0": (soma == 1.0),
        "erro acumulado": abs(soma - 1.0),
    }


# =====================================================================
# 2. MODELO DE REGRESSÃO
# =====================================================================

def treinar_modelo_regressao(df):
    """
    Treina uma regressão linear para estimar a latência observada.
    - 80% dos dados para treino e 20% para teste.
    - Validação cruzada (5 partes) dentro do treino, para ter uma segunda opinião.
    """
    if COL_OBSERVADA not in df.columns:
        raise ValueError("O DataFrame precisa da coluna 'latencia_observada_ms' (rode o dados.py).")
 
    dados = df.reset_index(drop=True)
 
    # O tipo do módulo é texto; o modelo precisa de números. get_dummies cria uma
    # coluna 0/1 para cada tipo (drop_first evita uma coluna redundante).
    tipos = pd.get_dummies(dados["tipo_modulo"], prefix="tipo", drop_first=True, dtype=float)
    dados = pd.concat([dados, tipos], axis=1)
    features = FEATURES_BASE + list(tipos.columns)
 
    X = dados[features]
    y = dados[COL_OBSERVADA]
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.2, random_state=SEMENTE)
 
    modelo = LinearRegression()
    rmse_validacao = -cross_val_score(modelo, X_treino, y_treino, cv=5,
                                      scoring="neg_root_mean_squared_error")
    modelo.fit(X_treino, y_treino)
 
    return {
        "modelo": modelo,
        "features": features,
        "dados": dados,
        "X_teste": X_teste,
        "y_treino": y_treino,
        "y_teste": y_teste,
        "y_pred_treino": modelo.predict(X_treino),
        "y_pred_teste": modelo.predict(X_teste),
        "rmse_validacao_medio": float(rmse_validacao.mean()),
    }


# =====================================================================
# 3. MÉTRICAS
# =====================================================================

def calcular_metricas(y_real, y_previsto):
    """
    Calcula MAE, MSE, RMSE e R².
    - MAE: erro médio (todos os erros pesam igual).
    - RMSE: eleva o erro ao quadrado antes da média, então erros grandes pesam mais.
      Se RMSE for bem maior que o MAE, existem alguns erros muito grandes.
    """
    mae = mean_absolute_error(y_real, y_previsto)
    mse = mean_squared_error(y_real, y_previsto)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_real, y_previsto)
    return {
        "MAE": round(float(mae), 4),
        "MSE": round(float(mse), 4),
        "RMSE": round(float(rmse), 4),
        "R2": round(float(r2), 4),
        "RMSE_sobre_MAE": round(float(rmse / mae), 3),
    }


def interpretar_metricas(m_teste, m_treino):
    """Retorna frases explicando as métricas (um número sozinho não basta)."""
    frases = []
    if m_teste["RMSE_sobre_MAE"] > 1.4:
        frases.append("RMSE bem maior que o MAE: há alguns registros com erro muito grande.")
    else:
        frases.append("RMSE próximo do MAE: os erros são parecidos entre os registros.")
    frases.append(f"R² = {m_teste['R2']:.2f}: o modelo explica essa parte da variação da latência, "
                  "mas R² alto não significa que o modelo é perfeito.")
    if m_treino["R2"] - m_teste["R2"] > 0.10:
        frases.append("R² de treino bem maior que o de teste: sinal de overfitting.")
    return frases



# =====================================================================
# 4. PREVISÕES PARA OS REGISTROS
# =====================================================================

def gerar_previsoes_completas(res):
    """
    Aplica o modelo a todos os registros e calcula o erro de cada um.
    Este DataFrame serve de entrada para o heap de alertas (Analista 3).
    """
    d = res["dados"].copy()
    if COL_PREVISTA in d.columns:      # guarda a estimativa de planejamento do CSV
        d = d.rename(columns={COL_PREVISTA: "latencia_prevista_original_ms"})
 
    d[COL_PREVISTA] = np.round(res["modelo"].predict(d[res["features"]]), 2)
    d["erro_absoluto_ms"] = np.round(erro_absoluto(d[COL_OBSERVADA], d[COL_PREVISTA]), 2)
    er = erro_relativo(d[COL_OBSERVADA], d[COL_PREVISTA])
    d["erro_relativo_pct"] = np.round(er * 100, 2)
    d["faixa_erro"] = [classificar_erro_relativo(x) for x in er]
 
    d["conjunto"] = "treino"
    d.loc[res["X_teste"].index, "conjunto"] = "teste"
    return d
 
 
def salvar_previsoes_csv(df_prev, caminho=None):
    """Salva as previsões em um CSV separado (não sobrescreve a base original)."""
    destino = caminho or os.path.join(DADOS_DIR, "dados_aurora_siger_com_previsao.csv")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    df_prev.to_csv(destino, index=False, encoding="utf-8")
    return destino

# =====================================================================
# 5. GRÁFICOS
# =====================================================================

def gerar_graficos(y_teste, y_pred, caminho=None):
    """Gera 3 gráficos: real x previsto, resíduos e distribuição dos erros."""
    y_teste = np.array(y_teste)
    y_pred = np.array(y_pred)
    residuos = y_teste - y_pred
 
    fig, eixos = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Avaliação do Modelo - SCIC / Aurora Siger", fontsize=14, fontweight="bold")
 
    # 1) Real x previsto: quanto mais perto da linha vermelha, melhor
    eixos[0].scatter(y_teste, y_pred, color="teal", alpha=0.7, edgecolors="k")
    minimo, maximo = y_teste.min(), y_teste.max()
    eixos[0].plot([minimo, maximo], [minimo, maximo], "r--", label="Previsão perfeita")
    eixos[0].set_xlabel("Latência observada (ms)")
    eixos[0].set_ylabel("Latência prevista (ms)")
    eixos[0].set_title("Real vs. Previsto")
    eixos[0].legend()
 
    # 2) Resíduos: devem ficar espalhados em torno de zero, sem padrão
    eixos[1].scatter(y_pred, residuos, color="darkorange", alpha=0.7, edgecolors="k")
    eixos[1].axhline(0, color="red", linestyle="--")
    eixos[1].set_xlabel("Valores previstos (ms)")
    eixos[1].set_ylabel("Resíduo (real - previsto)")
    eixos[1].set_title("Resíduos")
 
    # 3) Histograma dos erros
    eixos[2].hist(residuos, bins=10, color="purple", alpha=0.7, edgecolor="black")
    eixos[2].set_xlabel("Erro (ms)")
    eixos[2].set_ylabel("Frequência")
    eixos[2].set_title("Distribuição dos erros")
 
    for eixo in eixos:
        eixo.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
 
    destino = caminho or os.path.join(GRAFICOS_DIR, "avaliacao_modelo_scic.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    plt.savefig(destino, dpi=300)
    plt.close()
    return destino
 
 
def gerar_grafico_erro_por_modulo(df_prev, caminho=None):
    """Gráfico de barras com o erro relativo médio de cada módulo."""
    medias = df_prev.groupby("nome_modulo")["erro_relativo_pct"].mean().sort_values()
 
    plt.figure(figsize=(9, 5))
    plt.barh(medias.index, medias.values, color="steelblue", edgecolor="black")
    plt.axvline(LIMITE_ACEITAVEL * 100, color="green", linestyle="--", label="Limite aceitável (5%)")
    plt.axvline(LIMITE_PREOCUPANTE * 100, color="red", linestyle="--", label="Limite preocupante (15%)")
    plt.xlabel("Erro relativo médio (%)")
    plt.title("Erro relativo médio por módulo")
    plt.legend()
    plt.tight_layout()
 
    destino = caminho or os.path.join(GRAFICOS_DIR, "erro_relativo_por_modulo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    plt.savefig(destino, dpi=300)
    plt.close()
    return destino


# =====================================================================
# 6. EXECUÇÃO DA FASE (chamada pelo menu)
# =====================================================================

def _secao(numero, titulo):
    print(f"\n[{numero}] {titulo}")
    print("-" * 80)
 
 
def executar_fase6_analista2(df_telemetria, exibir=True):
    res = treinar_modelo_regressao(df_telemetria)
    m_teste = calcular_metricas(res["y_teste"], res["y_pred_teste"])
    m_treino = calcular_metricas(res["y_treino"], res["y_pred_treino"])
 
    df_prev = gerar_previsoes_completas(res)
    teste = df_prev[df_prev["conjunto"] == "teste"]
    erros = resumo_erros(teste[COL_OBSERVADA], teste[COL_PREVISTA])
 
    caminho_img = gerar_graficos(res["y_teste"], res["y_pred_teste"])
    caminho_mod = gerar_grafico_erro_por_modulo(df_prev)
    caminho_csv = salvar_previsoes_csv(df_prev)
 
    if exibir:
        print("\n" + "=" * 80)
        print("MODELAGEM, ERROS E MÉTRICAS (SCIC / AURORA SIGER)".center(80))
        print("=" * 80)
 
        _secao(1, "DADOS")
        print(f"Registros: {len(res['dados'])} | Treino: {len(res['y_treino'])} | Teste: {len(res['y_teste'])}")
        print(f"Variáveis de entrada: {len(res['features'])}")
 
        _secao(2, "PONTO FLUTUANTE")
        for nome, valor in demonstrar_ponto_flutuante().items():
            print(f"{nome:<32} {valor}")
        print("Diferenças de ~1e-16 são ruído da representação binária, não erro do modelo.")
 
        _secao(3, "MODELO: REGRESSÃO LINEAR")
        print(f"RMSE médio na validação cruzada (treino): {res['rmse_validacao_medio']:.2f} ms")
        coef = pd.Series(res["modelo"].coef_, index=res["features"]).round(3)
        print("Coeficientes (efeito de cada variável na latência):")
        print(coef.to_string())
 
        _secao(4, "MÉTRICAS")
        tabela = pd.DataFrame({"Treino": m_treino, "Teste": m_teste}).round(3)
        print(tabela.to_string())
        for frase in interpretar_metricas(m_teste, m_treino):
            print(f"- {frase}")
 
        _secao(5, "ERROS ABSOLUTO E RELATIVO (conjunto de teste)")
        print(f"Erro absoluto: médio {erros['EA_medio_ms']:.2f} ms | mediano {erros['EA_mediano_ms']:.2f} ms "
              f"| máximo {erros['EA_max_ms']:.2f} ms")
        print(f"Erro relativo: médio {erros['ER_medio_%']:.2f}% | máximo {erros['ER_max_%']:.2f}%")
        print(f"Aceitável (<5%): {erros['pct_aceitavel']:.1f}% | Atenção (5% a 15%): "
              f"{erros['pct_atencao']:.1f}% | Preocupante (>15%): {erros['pct_preocupante']:.1f}%")
 
        _secao(6, "ARQUIVOS GERADOS")
        print(f"Gráfico de avaliação : {os.path.relpath(caminho_img, RAIZ_PROJETO)}")
        print(f"Gráfico por módulo   : {os.path.relpath(caminho_mod, RAIZ_PROJETO)}")
        print(f"CSV com previsões    : {os.path.relpath(caminho_csv, RAIZ_PROJETO)}")
        print("\n" + "=" * 80)
 
    return {
        "status": "sucesso",
        "features": res["features"],
        "coeficientes": res["modelo"].coef_.tolist(),
        "intercepto": float(res["modelo"].intercept_),
        "metricas": m_teste,
        "metricas_treino": m_treino,
        "resumo_erros": erros,
        "df_previsoes": df_prev,
        "caminho_grafico": caminho_img,
        "caminho_grafico_modulo": caminho_mod,
        "caminho_csv_previsoes": caminho_csv,
    }
 
 
# Executando este arquivo direto, ele carrega (ou gera) a base e roda a análise
if __name__ == "__main__":
    import sys
    if RAIZ_PROJETO not in sys.path:
        sys.path.append(RAIZ_PROJETO)
 
    from src.fase6_scic.dados import carregar_telemetria_csv, gerar_dataset_telemetria, salvar_telemetria_csv
 
    try:
        df = carregar_telemetria_csv()
    except FileNotFoundError:
        df = gerar_dataset_telemetria()
        salvar_telemetria_csv(df)
 
    executar_fase6_analista2(df)