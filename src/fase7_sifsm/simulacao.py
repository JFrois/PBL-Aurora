"""Simulação computacional e integração matemática  |  INTEGRANTE 2  |  Caps. 5, 6 e 10

Dados de entrada: listar_leituras() de banco.py (consumo_w, carga_bateria_pct...).
Ideias do enunciado: variação do consumo no tempo, estado de carga (SoC) da
bateria, comparação de cenários de uso de recursos.
Matemática: integral numérica (regra do trapézio) = energia acumulada (Wh) a
partir da potência (W) ao longo do tempo; média da função; área sob a curva.
Documentar: variáveis, fenômeno representado e LIMITAÇÕES da simulação.
Gráficos: salvar em docs/fase7/graficos_ou_imagens/ (matplotlib).
"""

from __future__ import annotations

from typing import Sequence


def integrar_trapezio(tempos_h: Sequence[float], potencias_w: Sequence[float]) -> float:
    """Energia acumulada em Wh pela regra do trapézio."""
    raise NotImplementedError("Integrante 2: implementar integrar_trapezio()")


def simular_consumo(leituras: list[dict], horas: int = 24) -> dict:
    """Série temporal de consumo (por módulo ou total) para `horas`; devolve dict com tempos e valores."""
    raise NotImplementedError("Integrante 2: implementar simular_consumo()")


def simular_bateria(
    capacidade_wh: float,
    geracao_w: float,
    consumo_w: float,
    horas: int = 48,
    passo_h: float = 0.5,
    soc_inicial: float = 0.8,
) -> dict:
    """Evolução do estado de carga (0-1) da bateria: dSoC/dt = (geração - consumo) / capacidade."""
    raise NotImplementedError("Integrante 2: implementar simular_bateria()")


def comparar_cenarios(leituras: list[dict]) -> dict:
    """Compara cenários (ex.: consumo atual x com redução de 15% nos módulos não essenciais)."""
    raise NotImplementedError("Integrante 2: implementar comparar_cenarios()")


def gerar_graficos(resultado: dict, pasta_saida: str | None = None) -> list[str]:
    """Salva os gráficos e devolve os caminhos dos arquivos."""
    raise NotImplementedError("Integrante 2: implementar gerar_graficos()")


def executar_simulacao() -> dict:
    """Ponto de entrada do menu: roda a simulação, imprime a interpretação e devolve o resultado."""
    raise NotImplementedError("Integrante 2: implementar executar_simulacao()")
