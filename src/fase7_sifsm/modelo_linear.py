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

def formatar_numero(valor, casas=2):
    """Formata números apenas para apresentação no terminal."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


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
    """Apresenta um resumo dos dados e suas correlações."""
    numericos = df[ATRIBUTOS + ["consumo_w"]]
    estatisticas = numericos.describe()
    correlacao = numericos.corr()

    nomes = {
        "temperatura_c": "Temperatura (°C)",
        "umidade_pct": "Umidade (%)",
        "consumo_w": "Potência (W)",
    }

    print("\n1. ANÁLISE DOS DADOS")
    print("-" * 70)
    print(f" Registros válidos: {len(df)}")

    print(
        f"\n {'Variável':<20}"
        f"{'Média':>12}"
        f"{'Mínimo':>12}"
        f"{'Mediana':>12}"
        f"{'Máximo':>12}"
    )
    print(" " + "-" * 68)

    for campo in numericos.columns:
        resumo = estatisticas[campo]

        print(
            f" {nomes[campo]:<20}"
            f"{formatar_numero(resumo['mean']):>12}"
            f"{formatar_numero(resumo['min']):>12}"
            f"{formatar_numero(resumo['50%']):>12}"
            f"{formatar_numero(resumo['max']):>12}"
        )

    print("\n CORRELAÇÕES")
    print(
        " Temperatura × potência : "
        f"{formatar_numero(correlacao.loc['temperatura_c', 'consumo_w'], 3)}"
    )
    print(
        " Umidade × potência     : "
        f"{formatar_numero(correlacao.loc['umidade_pct', 'consumo_w'], 3)}"
    )
    print(
        " Temperatura × umidade  : "
        f"{formatar_numero(correlacao.loc['temperatura_c', 'umidade_pct'], 3)}"
    )
    print(" Correlação indica associação, não causalidade.")

    if "modulo_id" in df.columns:
        medias = df.groupby("modulo_id")["consumo_w"].mean()

        print("\n POTÊNCIA MÉDIA POR MÓDULO")
        print(f" {'Módulo':<15}{'Potência média (W)':>22}")
        print(" " + "-" * 37)

        for modulo, media in medias.items():
            print(
                f" {modulo:<15}"
                f"{formatar_numero(media):>22}"
            )

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
    """Explica a equação e apresenta a avaliação do modelo."""
    linhas = [
        "\n3. EQUAÇÃO E INTERPRETAÇÃO",
        "-" * 70,
        (
            " Potência estimada (W) = "
            f"{formatar_numero(resultado['intercepto'])}"
        ),
    ]

    unidades = {
        "temperatura_c": ("temperatura", "1 °C"),
        "umidade_pct": ("umidade", "1 ponto percentual de umidade"),
    }

    for atributo, coeficiente in resultado["coeficientes"].items():
        nome, unidade = unidades.get(
            atributo,
            (atributo, f"1 unidade de {atributo}"),
        )

        sinal = "+" if coeficiente >= 0 else "-"

        linhas.append(
            f"   {sinal} {formatar_numero(abs(coeficiente))} × {nome}"
        )

    linhas.append("\n Interpretação dos coeficientes:")

    for atributo, coeficiente in resultado["coeficientes"].items():
        nome, unidade = unidades.get(
            atributo,
            (atributo, f"1 unidade de {atributo}"),
        )

        sentido = "aumento" if coeficiente >= 0 else "redução"

        linhas.append(
            f" - {unidade}: associação com {sentido} de "
            f"{formatar_numero(abs(coeficiente))} W,"
        )
        linhas.append("   mantendo as demais entradas constantes.")

    linhas.extend([
        " O intercepto é uma referência matemática.",
        " Entradas iguais a zero podem estar fora dos dados observados.",
        " Os coeficientes não demonstram relações de causa e efeito.",
        "\n4. AVALIAÇÃO NO CONJUNTO DE TESTE",
        "-" * 70,
        f" MAE  — erro absoluto médio : {formatar_numero(resultado['mae'])} W",
        f" MSE  — erro quadrático médio: {formatar_numero(resultado['mse'])} W²",
        f" RMSE — raiz do MSE         : {formatar_numero(resultado['rmse'])} W",
        f" R²                        : {formatar_numero(resultado['r2'], 3)}",
        " R² não é porcentagem de acertos.",
        "\n COMPARAÇÃO COM UMA REFERÊNCIA SIMPLES",
        f" MAE da regressão : {formatar_numero(resultado['mae'])} W",
        f" MAE da média     : {formatar_numero(resultado['mae_baseline'])} W",
        " Para o MAE, quanto menor, melhor.",
    ])

    if resultado["mae"] >= resultado["mae_baseline"]:
        linhas.extend([
            "\n RESULTADO: a regressão não superou a média em MAE.",
            " Não utilizar o modelo para controle operacional.",
        ])
    else:
        linhas.extend([
            "\n RESULTADO: a regressão superou a média neste teste.",
            " Ainda é necessária validação com outros dados.",
        ])

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
            nomes = {
                "temperatura_c": ("Temperatura", "°C"),
                "umidade_pct": ("Umidade", "%"),
            }
            nome, unidade = nomes.get(atributo, (atributo, ""))
            raise ValueError(
                f"{nome} informada: {formatar_numero(valor)} {unidade}. "
                f"Faixa de treinamento: {formatar_numero(minimo)} a "
                f"{formatar_numero(maximo)} {unidade}. "
                "A estimativa foi bloqueada para evitar extrapolação."
            )
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

    print("\nPREPARAÇÃO DA BASE")
    print("-" * 70)
    print(f" Registros recebidos : {len(leituras)}")
    print(f" Registros removidos : {len(leituras) - len(df)}")
    print(f" Registros utilizados: {len(df)}")

    exploratoria = analise_exploratoria(df)
    resultado = treinar_regressao(df)
    resultado["exploratoria"] = exploratoria

    print("\n2. SEPARAÇÃO ENTRE TREINO E TESTE")
    print("-" * 70)
    print(f" Leituras de treinamento: {resultado['n_treino']}")
    print(f" Leituras de teste      : {resultado['n_teste']}")
    print(f" Início do teste       : {resultado['data_corte']}")
    print(" A separação considera os instantes em ordem cronológica.")
    print(" O mesmo instante não aparece nos dois conjuntos.")

    print(interpretar_coeficientes(resultado))

    print("\n5. CUIDADOS NA INTERPRETAÇÃO")
    print("-" * 70)

    correlacao_treino = resultado["correlacao_treino"]
    correlacao_entradas = correlacao_treino[
        "temperatura_c"
    ]["umidade_pct"]

    print(
        " Correlação temperatura × umidade no treino: "
        f"{formatar_numero(correlacao_entradas, 3)}"
    )
    print(" A correlação entre entradas pode afetar os coeficientes.")
    print(" Essa verificação inicial não substitui uma análise de VIF.")
    print(" Inspecione os gráficos para identificar picos e resíduos.")
    print(" Dados sintéticos e diferenças entre módulos limitam o modelo.")

    entrada = resultado["entrada_exemplo"]
    estimativa = prever(resultado, entrada)
    resultado["previsao_exemplo_w"] = estimativa

    print("\n6. EXEMPLO ILUSTRATIVO")
    print("-" * 70)
    print(
        " Temperatura utilizada: "
        f"{formatar_numero(entrada['temperatura_c'])} °C"
    )
    print(
        " Umidade utilizada    : "
        f"{formatar_numero(entrada['umidade_pct'])}%"
    )
    print(
        " Potência estimada    : "
        f"{formatar_numero(estimativa)} W"
    )
    print(
        " MAE no teste         : "
        f"{formatar_numero(resultado['mae'])} W"
    )
    print(" As entradas do exemplo são as medianas do treinamento.")
    print(" O MAE não é intervalo de confiança nem erro máximo garantido.")

    print("\n7. USO E RESPONSABILIDADE")
    print("-" * 70)
    print(" Uso proposto: discutir planejamento energético.")
    print(" A estimativa não prevê um ciclo futuro nem risco de falha.")
    print(" Nenhuma alteração operacional é realizada.")
    print(" Qualquer decisão exige validação humana e dados confiáveis.")

    resultado["graficos"] = gerar_graficos(df, resultado)

    print("\n8. GRÁFICOS GERADOS")
    print("-" * 70)

    for caminho in resultado["graficos"]:
        print(f" - {Path(caminho).name}")

    print(f"\n Pasta: {Path(resultado['graficos'][0]).parent}")

    return resultado
