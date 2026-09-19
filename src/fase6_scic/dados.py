"""
Módulo de Gestão de Dados e Telemetria — Analista 1
Fase 6: SCIC (Missão Aurora Siger)

Responsabilidades:
- Geração estruturada de dados com sementes reprodutíveis.
- Validação estrita de limites físicos das variáveis marcianas.
- Exportação e carregamento em data/processed/dados_aurora_siger.csv.
"""

import os
from typing import Optional
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "data", "processed"))
CSV_FILE_PATH = os.path.join(DADOS_DIR, "dados_aurora_siger.csv")


def gerar_dataset_telemetria(amostras: int = 100, seed: int = 42) -> pd.DataFrame:
    """
    Gera dataframe sintético com parâmetros físicos contínuos da base marciana:
    - temperatura_c (-60°C a +25°C)
    - pressao_kpa (0.5 kPa a 1.2 kPa)
    - radiacao_msv (0.1 mSv/h a 2.5 mSv/h)
    - tensao_v (220V a 240V)
    - corrente_a (5A a 30A)
    - potencia_w (calculada via hardware)
    """
    rng = np.random.default_rng(seed)

    temperatura = np.round(rng.uniform(-60.0, 25.0, amostras), 2)
    pressao = np.round(rng.uniform(0.50, 1.20, amostras), 3)
    radiacao = np.round(rng.uniform(0.10, 2.50, amostras), 2)
    tensao = np.round(rng.uniform(220.0, 240.0, amostras), 2)
    corrente = np.round(rng.uniform(5.0, 30.0, amostras), 2)
    potencia = np.round(tensao * corrente, 2)

    modulos_disponiveis = [
        "habitacao",
        "centro_controle",
        "armazenamento_energia",
        "producao_oxigenio",
        "laboratorio",
    ]
    modulos = rng.choice(modulos_disponiveis, size=amostras)

    df = pd.DataFrame(
        {
            "timestamp_id": np.arange(1, amostras + 1),
            "modulo": modulos,
            "temperatura_c": temperatura,
            "pressao_kpa": pressao,
            "radiacao_msv": radiacao,
            "tensao_v": tensao,
            "corrente_a": corrente,
            "potencia_w": potencia,
        }
    )
    return df


def validar_dataset(df: pd.DataFrame) -> bool:
    """Executa verificações de integridade de esquema e faixas físicas."""
    colunas_obrigatorias = {
        "timestamp_id",
        "modulo",
        "temperatura_c",
        "pressao_kpa",
        "radiacao_msv",
        "tensao_v",
        "corrente_a",
        "potencia_w",
    }
    if not colunas_obrigatorias.issubset(df.columns):
        return False

    # Validação de intervalos operacionais
    if not df["tensao_v"].between(200.0, 260.0).all():
        return False
    if not df["corrente_a"].between(0.0, 50.0).all():
        return False
    if not df["pressao_kpa"].between(0.1, 5.0).all():
        return False

    return True


def salvar_telemetria_csv(df: pd.DataFrame, caminho: Optional[str] = None) -> str:
    """Salva o DataFrame validado em formato CSV no diretório data/processed."""
    destino = caminho or CSV_FILE_PATH
    os.makedirs(os.path.dirname(destino), exist_ok=True)

    if not validar_dataset(df):
        raise ValueError(
            "O DataFrame fornecido contém anomalias ou formato inconsistente."
        )

    df.to_csv(destino, index=False, encoding="utf-8")
    return destino


def carregar_telemetria_csv(caminho: Optional[str] = None) -> pd.DataFrame:
    """Carrega e valida o arquivo CSV de telemetria da colónia."""
    origem = caminho or CSV_FILE_PATH
    if not os.path.exists(origem):
        raise FileNotFoundError(f"Ficheiro de telemetria não encontrado em: {origem}")

    df = pd.read_csv(origem, encoding="utf-8")
    if not validar_dataset(df):
        raise ValueError(
            f"Ficheiro {origem} corrompido ou fora das especificações operacionais."
        )
    return df
