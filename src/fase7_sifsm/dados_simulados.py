"""Gerador da base simulada do SIFSM  |  INTEGRANTE 1

Gera data/fase7/dados_aurora_siger.csv de forma DETERMINÍSTICA (semente fixa), com os
mesmos 8 módulos e sensores da Fase 6. O consumo depende linearmente da temperatura e
da umidade do módulo (+ ruído), o que dá ao Integrante 2 uma relação real para a
regressão linear. Alguns picos de consumo, uma falha de sensor e uma manutenção são
injetados de propósito para exercitar a regra booleana e os alertas.

Executar (na raiz do projeto):  python -m src.fase7_sifsm.dados_simulados
"""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_CSV = RAIZ_PROJETO / "data" / "fase7" / "dados_aurora_siger.csv"

# (id, nome, tipo, essencial, limite_consumo_w, temperatura_base_c, umidade_base_pct, sensores)
MODULOS = [
    ("MOD-01", "Habitação Alfa", "habitacao", 1, 6800.0, 22.0, 45.0, ("0x1A", "0x1B")),
    ("MOD-02", "Comunicação Central", "comunicacao", 1, 6500.0, 20.0, 35.0, ("0x2A", "0x2B")),
    ("MOD-03", "Controle de Missão", "controle", 1, 6600.0, 21.0, 40.0, ("0x3A", "0x3B")),
    ("MOD-04", "Laboratório Científico", "laboratorio", 0, 6200.0, 23.0, 38.0, ("0x4A", "0x4B")),
    ("MOD-05", "Suporte Médico", "suporte_medico", 1, 7000.0, 22.0, 42.0, ("0x5A", "0x5B")),
    ("MOD-06", "Estufa Agrícola", "agricultura", 0, 6400.0, 26.0, 75.0, ("0x6A", "0x6B")),
    ("MOD-07", "Armazenamento de Dados", "armazenamento_dados", 0, 6300.0, 19.0, 30.0, ("0x7A", "0x7B")),
    ("MOD-08", "Produção de Oxigênio", "producao_oxigenio", 1, 6900.0, 24.0, 50.0, ("0x8A", "0x8B")),
]

COLUNAS = [
    "modulo_id", "nome_modulo", "tipo_modulo", "essencial", "limite_consumo_w",
    "codigo_sensor", "tipo_sensor", "data_registro", "consumo_w", "temperatura_c",
    "umidade_pct", "carga_bateria_pct", "status_operacional",
]

# Coeficientes "verdadeiros" da simulação (a regressão deve recuperar algo próximo)
COEF_TEMPERATURA_W_POR_C = 85.0
COEF_UMIDADE_W_POR_PCT = 14.0

# (ciclo, módulo) com pico de consumo acima do limite; falha de sensor; manutenção
PICOS = {(3, "MOD-01"), (3, "MOD-08"), (6, "MOD-04"), (9, "MOD-06"), (9, "MOD-05"), (12, "MOD-03"), (13, "MOD-07")}
FALHAS = {(10, "MOD-06")}
MANUTENCOES = {(7, "MOD-04")}


def gerar_leituras(semente: int = 42, ciclos: int = 15, inicio: datetime | None = None) -> list[dict]:
    """Gera `ciclos` leituras por módulo (uma a cada 6 h). Total = 8 x ciclos."""
    sorteio = random.Random(semente)
    inicio = inicio or datetime(2026, 10, 1, 0, 0)
    leituras: list[dict] = []
    for ciclo in range(ciclos):
        momento = inicio + timedelta(hours=6 * ciclo)
        for (mid, nome, tipo, essencial, limite, t_base, u_base, sensores) in MODULOS:
            temperatura = round(t_base + sorteio.uniform(-3.0, 3.5) + (6.0 if (ciclo, mid) in PICOS else 0.0), 2)
            umidade = round(min(95.0, max(10.0, u_base + sorteio.uniform(-8.0, 8.0))), 2)
            base_w = 0.42 * limite
            consumo = (
                base_w
                + COEF_TEMPERATURA_W_POR_C * (temperatura - t_base)
                + COEF_UMIDADE_W_POR_PCT * (umidade - u_base)
                + sorteio.gauss(0.0, 120.0)
            )
            if (ciclo, mid) in PICOS:
                consumo = max(consumo, limite * sorteio.uniform(0.93, 1.12))
            consumo = round(max(consumo, 300.0), 2)
            bateria = round(60.0 + 30.0 * ((ciclo % 8) / 7.0) - 10.0 * sorteio.random(), 2)
            bateria = min(100.0, max(5.0, bateria))

            if (ciclo, mid) in FALHAS:
                status = "falha"
            elif (ciclo, mid) in MANUTENCOES:
                status = "manutencao"
            elif consumo > 0.9 * limite:
                status = "alerta"
            else:
                status = "ativo"

            indice_sensor = ciclo % 2
            leituras.append({
                "modulo_id": mid, "nome_modulo": nome, "tipo_modulo": tipo, "essencial": essencial,
                "limite_consumo_w": limite, "codigo_sensor": sensores[indice_sensor],
                "tipo_sensor": ("temperatura", "consumo")[indice_sensor],
                "data_registro": momento.strftime("%Y-%m-%d %H:%M"), "consumo_w": consumo,
                "temperatura_c": temperatura, "umidade_pct": umidade, "carga_bateria_pct": bateria,
                "status_operacional": status,
            })
    return leituras


def salvar_csv(leituras: list[dict], caminho: Path | None = None) -> Path:
    destino = Path(caminho or CAMINHO_CSV)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(leituras)
    return destino


if __name__ == "__main__":
    dados = gerar_leituras()
    caminho = salvar_csv(dados)
    print(f"{len(dados)} leituras gravadas em {caminho}")
