"""Desenha o circuito lógico da regra de alerta (docs/fase7/circuito_logico.png)  |  INTEGRANTE 1

    ALERTA   = A AND B AND C   (duas portas AND de 2 entradas em cascata)
    BLOQUEIO = NOT C           (inversor)

Executar (raiz do projeto):  python -m src.fase7_sifsm.circuito_png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, Polygon  # noqa: E402

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_PNG = RAIZ_PROJETO / "docs" / "fase7" / "circuito_logico.png"
COR = "#1f2a44"


def _porta_and(ax, x, y, w=1.2, h=1.0):
    """Desenha uma porta AND com a borda esquerda em x e o centro em y.
    Devolve (pino_superior, pino_inferior, saida)."""
    raio = h / 2
    meio = x + w - raio
    angulos = np.linspace(np.pi / 2, -np.pi / 2, 24)
    arco = [(meio + raio * np.cos(a), y + raio * np.sin(a)) for a in angulos]
    pontos = [(x, y + raio), (meio, y + raio)] + arco + [(meio, y - raio), (x, y - raio)]
    ax.add_patch(Polygon(pontos, closed=True, fill=True, facecolor="#eef3ff", edgecolor=COR, lw=2))
    ax.text(x + w * 0.38, y, "AND", ha="center", va="center", fontsize=10, color=COR, weight="bold")
    return (x, y + h / 4), (x, y - h / 4), (x + w, y)


def _porta_not(ax, x, y, w=0.9, h=0.8):
    ax.add_patch(Polygon([(x, y + h / 2), (x, y - h / 2), (x + w, y)], closed=True,
                         facecolor="#eef3ff", edgecolor=COR, lw=2))
    ax.add_patch(Circle((x + w + 0.08, y), 0.08, facecolor="white", edgecolor=COR, lw=2))
    ax.text(x + w * 0.3, y, "NOT", ha="center", va="center", fontsize=8, color=COR, weight="bold")
    return (x, y), (x + w + 0.16, y)


def _fio(ax, *pontos, **kw):
    xs, ys = zip(*pontos)
    ax.plot(xs, ys, color=kw.get("cor", COR), lw=2, solid_capstyle="round")


def gerar_circuito_png(caminho: Path | None = None) -> Path:
    destino = Path(caminho or CAMINHO_PNG)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    and1_a, and1_b, and1_s = _porta_and(ax, 2.9, 3.0)
    and2_a, and2_b, and2_s = _porta_and(ax, 5.5, 2.75)
    not_e, not_s = _porta_not(ax, 5.5, 1.2)

    # Entradas A, B, C
    y_a, y_b, y_c = and1_a[1], and1_b[1], 1.2
    for nome, rotulo, y in (("A", "CONSUMO_ELEVADO\n(consumo > 90% do limite)", y_a),
                            ("B", "MODULO_CRITICO\n(módulo essencial)", y_b),
                            ("C", "SENSOR_VALIDO\n(leitura confiável)", y_c)):
        ax.text(0.05, y, f"{nome}", fontsize=14, weight="bold", va="center", color=COR)
        ax.text(0.45, y, rotulo, fontsize=8.5, va="center", color="#444")
        ax.add_patch(Circle((2.4, y), 0.06, color=COR))
    _fio(ax, (2.4, y_a), and1_a)
    _fio(ax, (2.4, y_b), and1_b)
    # Saída da AND1 -> entrada superior da AND2
    _fio(ax, and1_s, (and1_s[0] + 0.5, and1_s[1]), (and1_s[0] + 0.5, and2_a[1]), and2_a)
    # C: segue até a AND2 (inferior) e até o inversor
    _fio(ax, (2.4, y_c), (4.8, y_c), (4.8, and2_b[1]), and2_b)
    _fio(ax, (4.8, y_c), not_e)
    ax.add_patch(Circle((4.8, y_c), 0.06, color=COR))

    # Saídas
    _fio(ax, and2_s, (8.0, and2_s[1]))
    ax.add_patch(Circle((8.3, and2_s[1]), 0.3, facecolor="#e53935", edgecolor=COR, lw=2))
    ax.text(8.8, and2_s[1], "ALERTA\nA·B·C", va="center", fontsize=10, weight="bold", color="#b71c1c")
    _fio(ax, not_s, (8.0, not_s[1]))
    ax.add_patch(Circle((8.3, not_s[1]), 0.3, facecolor="#fbc02d", edgecolor=COR, lw=2))
    ax.text(8.8, not_s[1], "BLOQUEIO\nNOT C", va="center", fontsize=10, weight="bold", color="#8d6e00")

    ax.text(5.3, 4.35, "SIFSM - Circuito lógico da regra de decisão da colônia", ha="center",
            fontsize=13, weight="bold", color=COR)
    ax.text(5.3, 0.25, "ALERTA = A AND B AND C        BLOQUEIO = NOT C        "
            "NOT ALERTA = (NOT A) OR (NOT B) OR (NOT C)  (De Morgan)",
            ha="center", fontsize=9, color="#444")
    fig.savefig(destino, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return destino


if __name__ == "__main__":
    print(f"Circuito gravado em {gerar_circuito_png()}")
