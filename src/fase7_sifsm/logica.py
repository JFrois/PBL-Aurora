"""Regra booleana de decisão e tabela-verdade  |  INTEGRANTE 1  |  Cap. 2 (lógica e circuitos)

A MESMA regra existe em três formas, todas coerentes entre si:
  1. funções Python (este módulo);
  2. expressão booleana + tabela-verdade (imprimir_tabela_verdade);
  3. circuito lógico (circuito_logico.png gerado por circuito_png.py; montagem no
     Tinkercad descrita em docs/fase7/tinkercad/README.md).

Variáveis (entradas):
    A = CONSUMO_ELEVADO : consumo acima de 90% do limite do módulo
    B = MODULO_CRITICO  : módulo essencial para a vida/missão (modulos.essencial = 1)
    C = SENSOR_VALIDO   : leitura confiável (sensor sem falha e valores plausíveis)

Regras (saídas):
    ALERTA   = A AND B AND C
    BLOQUEIO = NOT C        (nunca decidir com base em sensor inválido)
Pela lei de De Morgan, a negação do alerta é:  NOT ALERTA = (NOT A) OR (NOT B) OR (NOT C).
"""

from __future__ import annotations

from itertools import product
from typing import Callable, Optional

FATOR_CONSUMO_ELEVADO = 0.90  # consumo > 90% do limite do módulo
NOME_REGRA = "ALERTA = CONSUMO_ELEVADO AND MODULO_CRITICO AND SENSOR_VALIDO"
NOME_BLOQUEIO = "BLOQUEIO = NOT SENSOR_VALIDO"
VARIAVEIS = ("CONSUMO_ELEVADO", "MODULO_CRITICO", "SENSOR_VALIDO")


def consumo_alto(consumo_w: float, limite_w: float) -> bool:
    """True se o consumo ultrapassa FATOR_CONSUMO_ELEVADO do limite do módulo."""
    try:
        consumo, limite = float(consumo_w), float(limite_w)
    except (TypeError, ValueError):
        raise ValueError("consumo_w e limite_w devem ser numéricos.") from None
    if limite <= 0:
        raise ValueError("O limite de consumo deve ser maior que zero.")
    return consumo > FATOR_CONSUMO_ELEVADO * limite


def sensor_valido(leitura: dict) -> bool:
    """True se a leitura é confiável: status diferente de 'falha', consumo numérico >= 0
    e temperatura (se houver) dentro de uma faixa plausível (-100 a 100 °C)."""
    if str(leitura.get("status_operacional", "")).strip().lower() == "falha":
        return False
    try:
        if float(leitura.get("consumo_w")) < 0:
            return False
        temperatura = leitura.get("temperatura_c")
        if temperatura is not None and not -100 <= float(temperatura) <= 100:
            return False
    except (TypeError, ValueError):
        return False
    return True


def acionar_alerta(consumo_elevado: bool, modulo_critico: bool, sensor_valido: bool = True) -> bool:
    """Regra principal: ALERTA = A AND B AND C."""
    return bool(consumo_elevado and modulo_critico and sensor_valido)


def bloquear_operacao(sensor_valido: bool) -> bool:
    """Regra de segurança: BLOQUEIO = NOT C."""
    return not sensor_valido


def classificar_risco(leitura: dict, limite_w: float, modulo_critico: bool) -> str:
    """Traduz uma leitura em 'bloqueado' | 'alto' | 'medio' | 'baixo'.

        bloqueado : sensor inválido (a decisão é suspensa)
        alto      : ALERTA (consumo elevado em módulo crítico com sensor válido)
        medio     : consumo elevado em módulo NÃO crítico
        baixo     : demais casos
    """
    valido = sensor_valido(leitura)
    if bloquear_operacao(valido):
        return "bloqueado"
    elevado = consumo_alto(leitura["consumo_w"], limite_w)
    if acionar_alerta(elevado, modulo_critico, valido):
        return "alto"
    return "medio" if elevado else "baixo"


def tabela_verdade(
    regra: Optional[Callable[..., bool]] = None,
    variaveis: tuple[str, ...] = VARIAVEIS,
) -> list[tuple]:
    """Todas as combinações (2^n) e o resultado da regra: [(a, b, c, saida), ...]."""
    regra = regra or acionar_alerta
    linhas = []
    for combinacao in product((False, True), repeat=len(variaveis)):
        linhas.append(combinacao + (bool(regra(*combinacao)),))
    return linhas


def imprimir_tabela_verdade() -> None:
    """Mostra as regras e a tabela-verdade (0/1) no terminal."""
    print(f"\n  {NOME_REGRA}")
    print(f"  {NOME_BLOQUEIO}")
    print("  Pela lei de De Morgan: NOT ALERTA = (NOT A) OR (NOT B) OR (NOT C)\n")
    print("   A = CONSUMO_ELEVADO   B = MODULO_CRITICO   C = SENSOR_VALIDO\n")
    print("   A  B  C | ALERTA | BLOQUEIO")
    print("  ---------+--------+----------")
    for a, b, c, saida in tabela_verdade():
        print(f"   {int(a)}  {int(b)}  {int(c)} |   {int(saida)}    |    {int(bloquear_operacao(c))}")
    print("\n  Leitura: o alerta só dispara com as três condições juntas; com sensor "
          "inválido (C = 0) o sistema bloqueia a decisão.")
