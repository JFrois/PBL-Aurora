"""Modelo linear para apoio à decisão  |  INTEGRANTE 2  |  Cap. 7

Já existe regressão na Fase 6 (src/fases_anteriores/fase6_scic/modelagem.py:
treino/teste, MAE/MSE/RMSE/R², gráficos). ADAPTAR/REAPROVEITAR, mas trocando o alvo
(latência) por uma variável de sustentabilidade, por exemplo:
    consumo_w  ~  temperatura_c + umidade_pct + carga_bateria_pct
Entregar: análise exploratória, correlação, coeficientes interpretados, métricas
de avaliação, limitações (poucos dados, colinearidade/VIF) e uma decisão apoiada
pelo modelo (ex.: prever consumo e sugerir reduzir carga em módulos não essenciais).
"""

from __future__ import annotations


def preparar_dados(leituras: list[dict]):
    """Converte leituras (lista de dict) em DataFrame limpo, pronto para o modelo."""
    raise NotImplementedError("Integrante 2: implementar preparar_dados()")


def analise_exploratoria(df) -> dict:
    """Estatísticas descritivas e matriz de correlação."""
    raise NotImplementedError("Integrante 2: implementar analise_exploratoria()")


def treinar_regressao(df, alvo: str = "consumo_w", atributos: list[str] | None = None) -> dict:
    """Ajusta a regressão linear (simples ou múltipla) e devolve modelo, coeficientes e métricas."""
    raise NotImplementedError("Integrante 2: implementar treinar_regressao()")


def interpretar_coeficientes(resultado: dict) -> str:
    """Texto em linguagem simples: o que cada coeficiente e o R² significam para a colônia."""
    raise NotImplementedError("Integrante 2: implementar interpretar_coeficientes()")


def prever(resultado: dict, entrada: dict) -> float:
    """Previsão do alvo para uma nova entrada (usada pela análise integrada e pelos agentes)."""
    raise NotImplementedError("Integrante 2: implementar prever()")


def executar_modelo_linear() -> dict:
    """Ponto de entrada do menu: carrega dados do banco, treina, interpreta e imprime."""
    raise NotImplementedError("Integrante 2: implementar executar_modelo_linear()")
