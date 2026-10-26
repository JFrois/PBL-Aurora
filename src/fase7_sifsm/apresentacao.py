"""Telas explicativas do menu (texto no terminal)  |  INTEGRANTES 1 e 3

O enunciado pede que o sistema "exiba ou explique" o circuito lógico e apresente
uma análise final com limitações. Estas funções são só texto: curtas, claras e
ligadas ao que o sistema realmente faz (nada de texto genérico).
"""

from __future__ import annotations


def exibir_circuito_logico() -> None:
    """INTEGRANTE 1: mostra a regra booleana, o caminho do circuito (PNG/Tinkercad) e como
    cada porta lógica corresponde à função em logica.py."""
    from pathlib import Path

    from src.fase7_sifsm import logica

    raiz = Path(__file__).resolve().parents[2]
    png = raiz / "docs" / "fase7" / "circuito_logico.png"
    link = raiz / "docs" / "fase7" / "link_tinkercad.txt"

    print(f"\n  {logica.NOME_REGRA}")
    print(f"  {logica.NOME_BLOQUEIO}\n")
    print("  Correspondência circuito <-> código:")
    print("    porta AND (A, B)        -> logica.acionar_alerta(A, B, ...)  (1º nível)")
    print("    porta AND (AB, C)       -> logica.acionar_alerta(A, B, C)    (2º nível)")
    print("    inversor NOT (C)        -> logica.bloquear_operacao(C)")
    print("    LED vermelho / amarelo  -> alerta registrado / operação bloqueada")
    print("    chaves A, B, C          -> consumo_alto(), essencial do módulo, sensor_valido()\n")
    print("  Circuito (diagrama)  :", png if png.exists() else "não gerado - rode: python -m src.fase7_sifsm.circuito_png")
    if link.exists():
        print("  Simulação Tinkercad  :", link.read_text(encoding="utf-8").strip() or "(arquivo vazio)")
    else:
        print("  Simulação Tinkercad  : montagem em docs/fase7/tinkercad/README.md "
              "(cole o link em docs/fase7/link_tinkercad.txt)")
    print("\n  Dica: a opção 5 do menu mostra a tabela-verdade que o circuito deve reproduzir.")


def exibir_arquitetura() -> None:
    """INTEGRANTE 3: arquitetura computacional ligada ao sistema (Cap. 14): o que exigiria
    mais processamento, o que roda local, paralelismo, CPU/GPU/NPU/TPU, memória e
    movimentação de dados, e a relação com consumo energético."""
    raise NotImplementedError("Integrante 3: implementar exibir_arquitetura()")


def exibir_sustentabilidade() -> None:
    """INTEGRANTE 3: sustentabilidade, cidadania digital e impacto socioambiental (Caps. 11 e 13),
    com pelo menos 4 pontos do item 5.8 do enunciado, ligados ao sistema."""
    raise NotImplementedError("Integrante 3: implementar exibir_sustentabilidade()")


def exibir_analise_final(resultados: dict | None = None) -> None:
    """INTEGRANTE 3: análise final dos resultados e das LIMITAÇÕES do sistema + melhorias futuras."""
    raise NotImplementedError("Integrante 3: implementar exibir_analise_final()")
