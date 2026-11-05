"""5.5 Modelo linear aplicada à tomada de decisão  |  INTEGRANTE 2  |

Entradas: temperatura em °C e umidade em %
Saída: consumo estimado em W"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ATRIBUTOS = [
    "temperatura_c",
    "umidade_pct",
]

PASTA_GRAFICOS = (
    Path(__file__).resolve().parents[2]
    / "docs/fase7/graficos_ou_imagens"
)

def preparar_dados(leituras: list[dict]):
    """Converte a consulta do banco em uma tabela adequada ao modelo."""
    df = pd.DataFrame(leituras)
    campos = ATRIBUTOS + ["consumo_w", "data_registro"]

    for campo in campos:
        if campo not in df.columns:
            raise ValueError(f"Campo obrigatório ausente: {campo}.")

    for campo in ATRIBUTOS + ["consumo_w"]:
        df[campo] = pd.to_numeric(df[campo], errors="coerce")

    df["data_registro"] = pd.to_datetime(df["data_registro"], errors="coerce")
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=campos)

    if "status_operacional" in df.columns:
        df = df[df["status_operacional"] != "falha"]

    # Faixas plausíveis; alertas de consumo não são removidos.
    df = df[df["consumo_w"] >= 0]
    df = df[df["temperatura_c"].between(-100, 100)]
    df = df[df["umidade_pct"].between(0, 100)]

    if df.empty:
        raise ValueError("Não há leituras válidas para a modelagem.")

    return df.sort_values("data_registro").reset_index(drop=True)


def analise_exploratoria(df) -> dict:
    """Resume a distribuição e as associações entre as variáveis."""
    numericos = df[ATRIBUTOS + ["consumo_w"]]
    estatisticas = numericos.describe()
    correlacao = numericos.corr()

    print("\nANÁLISE EXPLORATÓRIA")
    print(f"Registros válidos: {len(df)}")
    print("\nEstatísticas descritivas:")
    print(estatisticas.round(2))
    print("\nMatriz de correlação:")
    print(correlacao.round(3))

    if "modulo_id" in df.columns:
        print("\nConsumo médio por módulo (W):")
        print(df.groupby("modulo_id")["consumo_w"].mean().round(2))

    print("\nObserve picos e diferenças entre módulos nos gráficos.")
    print("Correlação não demonstra que uma variável causa a outra.")

    return {
        "registros": len(df),
        "estatisticas": estatisticas.to_dict(),
        "correlacao": correlacao.to_dict(),
    }


def treinar_regressao(df, alvo="consumo_w", atributos=None) -> dict:
    """Ajusta o modelo e avalia em instantes posteriores ao treinamento."""
    if atributos is None:
        atributos = ATRIBUTOS.copy()

    if not atributos or alvo in atributos:
        raise ValueError("Informe atributos diferentes da variável alvo.")

    for campo in [alvo, *atributos, "data_registro"]:
        if campo not in df.columns:
            raise ValueError(f"Campo ausente: {campo}.")

    datas = sorted(df["data_registro"].unique())

    if len(df) < 10 or len(datas) < 3:
        raise ValueError("Use pelo menos 10 registros e três instantes distintos.")

    # Separação temporal: o mesmo instante não aparece nos dois conjuntos.
    indice_corte = int(len(datas) * 0.8)
    indice_corte = max(1, min(indice_corte, len(datas) - 1))
    data_corte = datas[indice_corte]

    treino = df[df["data_registro"] < data_corte]
    teste = df[df["data_registro"] >= data_corte]

    if len(treino) <= len(atributos) or len(teste) < 2:
        raise ValueError("Há poucos registros para treinar e avaliar.")

    X_treino = treino[atributos]
    y_treino = treino[alvo]
    X_teste = teste[atributos]
    y_teste = teste[alvo]

    modelo = LinearRegression()
    modelo.fit(X_treino, y_treino)
    previsoes = modelo.predict(X_teste)

    # Referência simples: prever sempre a média do treinamento.
    referencia = [float(y_treino.mean())] * len(y_teste)
    mse = float(mean_squared_error(y_teste, previsoes))

    coeficientes = {}
    faixas = {}
    for i, atributo in enumerate(atributos):
        coeficientes[atributo] = float(modelo.coef_[i])
        faixas[atributo] = (
            float(X_treino[atributo].min()),
            float(X_treino[atributo].max()),
        )

    return {
        "modelo": modelo,
        "atributos": atributos,
        "coeficientes": coeficientes,
        "intercepto": float(modelo.intercept_),
        "mae": float(mean_absolute_error(y_teste, previsoes)),
        "mse": mse,
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_teste, previsoes)),
        "mae_baseline": float(mean_absolute_error(y_teste, referencia)),
        "n_treino": len(treino),
        "n_teste": len(teste),
        "data_corte": str(data_corte),
        "observado": y_teste.to_numpy(),
        "previsto": previsoes,
        "residuos": y_teste.to_numpy() - previsoes,
        "faixas": faixas,
        "entrada_exemplo": X_treino.median().to_dict(),
        "correlacao_treino": X_treino.corr().to_dict(),
    }

def interpretar_coeficientes(resultado: dict) -> str:
    """Apresenta a equação, as unidades e os limites da interpretação."""
    equacao = f"Consumo estimado (W) = {resultado['intercepto']:.2f}"
    linhas = []
    unidades = {
        "temperatura_c": "1 °C",
        "umidade_pct": "1 ponto percentual de umidade",
    }

    for atributo, coeficiente in resultado["coeficientes"].items():
        equacao += f" {coeficiente:+.2f} × {atributo}"
        unidade = unidades.get(atributo, f"1 unidade de {atributo}")
        linhas.append(
            f"{unidade}: associação de {coeficiente:+.2f} W, "
            "mantendo as demais entradas constantes."
        )

    linhas.insert(0, equacao)
    linhas.append("O intercepto é uma referência matemática; zero pode estar fora dos dados.")
    linhas.append(f"MAE: {resultado['mae']:.2f} W")
    linhas.append(f"MSE: {resultado['mse']:.2f} W²")
    linhas.append(f"RMSE: {resultado['rmse']:.2f} W")
    linhas.append(f"R² no teste: {resultado['r2']:.3f}; não é porcentagem de acertos.")
    linhas.append(f"MAE da média do treino: {resultado['mae_baseline']:.2f} W")

    if resultado["mae"] >= resultado["mae_baseline"]:
        linhas.append("O modelo não superou a média em MAE: não usar para controle operacional.")
    else:
        linhas.append("O modelo superou a média neste teste, mas ainda exige validação externa.")

    linhas.append("Dados sintéticos, picos e diferenças entre módulos limitam a generalização.")
    linhas.append("Coeficientes indicam associação, não causalidade.")
    return "\n".join(linhas)


def prever(resultado: dict, entrada: dict) -> float:
    """Estima consumo sem permitir extrapolação fora das faixas de treino."""
    valores = {}
    for atributo in resultado["atributos"]:
        if atributo not in entrada:
            raise ValueError(f"Informe o atributo {atributo}.")

        valor = float(entrada[atributo])
        minimo, maximo = resultado["faixas"][atributo]
        if not np.isfinite(valor) or not minimo <= valor <= maximo:
            raise ValueError(f"{atributo} está fora da faixa válida do treino.")
        valores[atributo] = valor

    tabela = pd.DataFrame([valores], columns=resultado["atributos"])
    previsao = float(resultado["modelo"].predict(tabela)[0])
    if not np.isfinite(previsao) or previsao < 0:
        raise ValueError("Previsão sem interpretação física; revisar o modelo.")
    return previsao


def gerar_graficos(df, resultado: dict, pasta_saida=None) -> list[str]:
    pasta = Path(pasta_saida) if pasta_saida else PASTA_GRAFICOS
    pasta.mkdir(parents=True, exist_ok=True)
    caminhos = []

    plt.figure(figsize=(10, 4))
    for i, atributo in enumerate(ATRIBUTOS):
        plt.subplot(1, 2, i + 1)
        plt.scatter(df[atributo], df["consumo_w"], alpha=0.7)
        rotulo = "Temperatura (°C)" if atributo == "temperatura_c" else "Umidade (%)"
        plt.xlabel(rotulo)
        plt.ylabel("Consumo (W)")
        plt.grid(True)
    plt.tight_layout()
    caminho = pasta / "analise_exploratoria.png"
    plt.savefig(caminho)
    plt.close()
    caminhos.append(str(caminho))

    plt.figure(figsize=(6, 5))
    plt.scatter(resultado["observado"], resultado["previsto"])
    minimo = min(min(resultado["observado"]), min(resultado["previsto"]))
    maximo = max(max(resultado["observado"]), max(resultado["previsto"]))
    plt.plot([minimo, maximo], [minimo, maximo], "--", color="gray")
    plt.xlabel("Consumo observado (W)")
    plt.ylabel("Consumo previsto (W)")
    plt.title("Avaliação em dados de teste")
    plt.grid(True)
    plt.tight_layout()
    caminho = pasta / "regressao.png"
    plt.savefig(caminho)
    plt.close()
    caminhos.append(str(caminho))

    plt.figure(figsize=(7, 4))
    plt.scatter(resultado["previsto"], resultado["residuos"])
    plt.axhline(0, color="gray", linestyle="--")
    plt.xlabel("Consumo previsto (W)")
    plt.ylabel("Resíduo: observado - previsto (W)")
    plt.title("Resíduos no conjunto de teste")
    plt.grid(True)
    plt.tight_layout()
    caminho = pasta / "residuos.png"
    plt.savefig(caminho)
    plt.close()
    caminhos.append(str(caminho))

    return caminhos    

def executar_modelo_linear() -> dict:
    from . import banco

    leituras = banco.listar_leituras(limite=None, ordem="asc")
    df = preparar_dados(leituras)
    print(f"Registros recebidos: {len(leituras)}; removidos: {len(leituras) - len(df)}")
    exploratoria = analise_exploratoria(df)
    resultado = treinar_regressao(df)
    resultado["exploratoria"] = exploratoria

    print(f"\nTreino: {resultado['n_treino']}; teste: {resultado['n_teste']}")
    print("Primeiro instante de teste:", resultado["data_corte"])
    print(interpretar_coeficientes(resultado))
    print("\nCorrelação das entradas no treino:")
    print(pd.DataFrame(resultado["correlacao_treino"]).round(3))
    print("Correlação alta entre entradas pode dificultar interpretar os coeficientes.")
    print("Não foi calculado VIF; a correlação é uma verificação inicial.")

    resultado["graficos"] = gerar_graficos(df, resultado)
    print("Resíduos devem ser inspecionados: padrões e erros grandes sugerem limitações.")

    # Exemplo hipotético com as medianas das entradas do treinamento.
    entrada = resultado["entrada_exemplo"]
    estimativa = prever(resultado, entrada)
    resultado["previsao_exemplo_w"] = estimativa
    print("\nCondições ilustrativas:", entrada)
    print(f"Consumo estimado: {estimativa:.1f} W; MAE no teste: {resultado['mae']:.1f} W.")
    print("O MAE não é um intervalo de confiança nem um limite garantido de erro.")
    print("Uso proposto: apoiar o planejamento e revisar cargas não essenciais.")
    print("Não é previsão de um ciclo futuro nem classificação de risco de falha.")
    print("Qualquer decisão exige validação humana e confirmação com dados reais.")
    for caminho in resultado["graficos"]:
        print("Gráfico salvo:", caminho)

    return resultado