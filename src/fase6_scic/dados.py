"""
Módulo de Gestão de Dados e Telemetria — Analista 1
Fase 6: SCIC (Missão Aurora Siger)

Responsabilidades:
- Geração da base simulada da colônia (dados_aurora_siger.csv)
- Limpa e valida os dados (nulos, duplicados, faixas físicas).
- Calcula indicadores operacionais.
- Exportação e carregamento em data/processed/dados_aurora_siger.csv.

Colunas geradas (20):
  timestamp_id, ciclo, data_registro,                       -> registro / ciclo
  modulo_id, nome_modulo, tipo_modulo, essencial,           -> identificação do módulo
  codigo_sensor_hex,                                        -> código do dispositivo/sensor
  temperatura_c, pressao_kpa, radiacao_msv,                 -> ambiente
  tensao_v, corrente_a, potencia_w, limite_potencia_w,      -> eletricidade
  latencia_observada_ms, latencia_prevista_ms,              -> comunicação
  status_operacional, prioridade, mensagem_alerta           -> alertas
"""

import numpy as np
import pandas as pd
from pathlib import Path

# A potência (P = V * I) é calculada no hardware.py
try:
    from .hardware import calcular_potencia
except ImportError:
    from hardware import calcular_potencia

# =====================================================================
# CONFIGURAÇÃO DE CAMINHOS COM PATHLIB (MODERNO E SEGURO)
# =====================================================================
# Resolve o caminho absoluto do arquivo atual e volta duas pastas
BASE_DIR = Path(__file__).resolve().parent
RAIZ_PROJETO = BASE_DIR.parent.parent

# Usa a barra (/) para unir caminhos de forma segura em qualquer SO
CSV_FILE_PATH = RAIZ_PROJETO / "data" / "processed" / "dados_aurora_siger.csv"

MODULOS = [
    ("MOD-01", "Habitação Alfa", "habitacao", 1, 28.0, 6800.0, ("0x1A", "0x1B")),
    ("MOD-02", "Comunicação Central", "comunicacao", 1, 12.0, 6500.0, ("0x2A", "0x2B")),
    ("MOD-03", "Controle de Missão", "controle", 1, 15.0, 6600.0, ("0x3A", "0x3B")),
    (
        "MOD-04",
        "Laboratório Científico",
        "laboratorio",
        0,
        35.0,
        6200.0,
        ("0x4A", "0x4B"),
    ),
    ("MOD-05", "Suporte Médico", "suporte_medico", 1, 22.0, 7000.0, ("0x5A", "0x5B")),
    ("MOD-06", "Estufa Agrícola", "agricultura", 0, 45.0, 6400.0, ("0x6A", "0x6B")),
    (
        "MOD-07",
        "Armazenamento de Dados",
        "armazenamento_dados",
        0,
        18.0,
        6300.0,
        ("0x7A", "0x7B"),
    ),
    (
        "MOD-08",
        "Produção de Oxigênio",
        "producao_oxigenio",
        1,
        25.0,
        6900.0,
        ("0x8A", "0x8B"),
    ),
]

COLUNAS = [
    "timestamp_id",
    "ciclo",
    "data_registro",
    "modulo_id",
    "nome_modulo",
    "tipo_modulo",
    "essencial",
    "codigo_sensor_hex",
    "temperatura_c",
    "pressao_kpa",
    "radiacao_msv",
    "tensao_v",
    "corrente_a",
    "potencia_w",
    "limite_potencia_w",
    "latencia_observada_ms",
    "latencia_prevista_ms",
    "status_operacional",
    "prioridade",
    "mensagem_alerta",
]

STATUS_VALIDOS = ["ativo", "manutencao", "alerta"]


# =====================================================================
# 1. GERAÇÃO DA BASE SIMULADA
# =====================================================================


def gerar_dataset_telemetria(amostras=120, semente=42):
    """
    Gera a base simulada. Cada ciclo tem uma leitura de cada um dos 8 módulos
    (120 amostras = 15 ciclos x 8 módulos). A semente garante o mesmo
    resultado toda vez que o código é executado.
    """
    rng = np.random.default_rng(semente)
    linhas = []

    for i in range(amostras):
        # Escolhe o módulo da vez (repete a lista de módulos a cada ciclo)
        modulo_id, nome, tipo, essencial, lat_base, limite, sensores = MODULOS[
            i % len(MODULOS)
        ]
        ciclo = i // len(MODULOS) + 1

        # Ambiente
        temperatura = round(rng.uniform(-60, 25), 2)
        pressao = round(rng.uniform(0.5, 1.2), 3)
        radiacao = round(rng.uniform(0.1, 2.5), 2)

        # Eletricidade: potência = tensão x corrente (função do hardware.py)
        tensao = round(rng.uniform(220, 240), 2)
        corrente = round(rng.uniform(5, 30), 2)
        potencia = round(calcular_potencia(tensao, corrente), 2)

        # Latência PREVISTA: estimativa de planejamento (não enxerga cada leitura)
        lat_prevista = lat_base + 0.003 * potencia + 7.0 + rng.normal(0, 1.0)

        # Latência OBSERVADA: previsto + efeitos da temperatura, radiação, ruído e picos
        pico = 0
        if rng.random() < 0.06:  # 6% das leituras têm um pico de latência
            pico = rng.uniform(15, 35)
        lat_observada = (
            lat_base
            + 0.003 * potencia
            + 0.05 * abs(temperatura)
            + 2.5 * radiacao**2
            + rng.normal(0, 2.5)
            + pico
        )

        lat_prevista = round(max(lat_prevista, 1.0), 2)
        lat_observada = round(max(lat_observada, 1.0), 2)

        # Status e mensagem
        if rng.random() < 0.08:
            status, mensagem = "manutencao", "Manutenção preventiva agendada"
        elif potencia > limite:
            status, mensagem = "alerta", "Sobrecarga de potência no barramento"
        elif lat_observada > lat_prevista * 1.30:
            status, mensagem = "alerta", "Latência acima do previsto"
        elif radiacao > 2.30:
            status, mensagem = "alerta", "Radiação elevada no módulo"
        else:
            status, mensagem = "ativo", "Operação nominal"

        """ 
        Prioridade (1 a 4): módulos essenciais têm prioridade maior.
        Não depende da latência, para o modelo não "colar" a resposta.
        """
        prioridade = 1 + essencial * 2 + int(rng.integers(0, 2))

        sensor = sensores[int(rng.integers(0, 2))]
        data = (pd.Timestamp("2026-10-01") + pd.Timedelta(days=ciclo - 1)).strftime(
            "%Y-%m-%d"
        )

        linhas.append(
            {
                "timestamp_id": i + 1,
                "ciclo": ciclo,
                "data_registro": data,
                "modulo_id": modulo_id,
                "nome_modulo": nome,
                "tipo_modulo": tipo,
                "essencial": essencial,
                "codigo_sensor_hex": sensor,
                "temperatura_c": temperatura,
                "pressao_kpa": pressao,
                "radiacao_msv": radiacao,
                "tensao_v": tensao,
                "corrente_a": corrente,
                "potencia_w": potencia,
                "limite_potencia_w": limite,
                "latencia_observada_ms": lat_observada,
                "latencia_prevista_ms": lat_prevista,
                "status_operacional": status,
                "prioridade": prioridade,
                "mensagem_alerta": mensagem,
            }
        )

    return pd.DataFrame(linhas, columns=COLUNAS)


# =====================================================================
# 2. LIMPEZA E VALIDAÇÃO
# =====================================================================


def limpar_dataset(df):
    """Padroniza o texto do status, remove linhas duplicadas e linhas com valores vazios."""
    df = df.copy()
    df["status_operacional"] = df["status_operacional"].str.strip().str.lower()

    antes = len(df)
    df = df.drop_duplicates(subset="timestamp_id")
    df = df.dropna()
    removidos = antes - len(df)
    if removidos > 0:
        print(
            f"[Limpeza] {removidos} linha(s) removida(s) (duplicadas ou com valores vazios)."
        )
    return df.reset_index(drop=True)


def verificar_problemas(df):
    """Confere colunas e faixas físicas. Retorna a lista de problemas (vazia = tudo certo)."""
    faltando = [c for c in COLUNAS if c not in df.columns]
    if faltando:
        return [f"Colunas ausentes: {faltando}"]

    problemas = []

    if df[COLUNAS].isnull().any().any():
        problemas.append("Existem valores vazios na base.")

    # Faixas permitidas: coluna -> (mínimo, máximo)
    faixas = {
        "tensao_v": (200, 260),
        "corrente_a": (0, 50),
        "pressao_kpa": (0.1, 5),
        "temperatura_c": (-100, 60),
        "radiacao_msv": (0, 10),
        "prioridade": (1, 4),
    }
    for coluna, (minimo, maximo) in faixas.items():
        fora = (~df[coluna].between(minimo, maximo)).sum()
        if fora > 0:
            problemas.append(
                f"{fora} valor(es) de '{coluna}' fora da faixa [{minimo}, {maximo}]."
            )

    if (df["latencia_observada_ms"] <= 0).any() or (
        df["latencia_prevista_ms"] <= 0
    ).any():
        problemas.append("As latências devem ser maiores que zero.")

    if not df["status_operacional"].isin(STATUS_VALIDOS).all():
        problemas.append(f"Status inválido (válidos: {STATUS_VALIDOS}).")

    if not df["codigo_sensor_hex"].astype(str).str.startswith("0x").all():
        problemas.append("Código de sensor fora do padrão hexadecimal (ex.: 0x1A).")

    # Potência precisa ser igual a tensão x corrente (com pequena tolerância de arredondamento)
    diferenca = (df["potencia_w"] - df["tensao_v"] * df["corrente_a"]).abs()
    if (diferenca > 0.01).any():
        problemas.append("A potência não bate com tensão x corrente.")

    if df["timestamp_id"].duplicated().any():
        problemas.append("Existem timestamp_id repetidos.")

    return problemas


def validar_dataset(df):
    """Retorna True se a base não tem nenhum problema."""
    return len(verificar_problemas(df)) == 0


# =====================================================================
# 3. INDICADORES OPERACIONAIS
# =====================================================================


def calcular_indicadores(df):
    """Calcula indicadores simples da colônia (retorna um dicionário)."""
    total = len(df)
    status = df["status_operacional"]
    return {
        "total_registros": total,
        "disponibilidade_%": round((status == "ativo").sum() / total * 100, 2),
        "taxa_alertas_%": round((status == "alerta").sum() / total * 100, 2),
        "em_manutencao_%": round((status == "manutencao").sum() / total * 100, 2),
        "latencia_media_ms": round(df["latencia_observada_ms"].mean(), 2),
        "latencia_acima_do_previsto_%": round(
            (df["latencia_observada_ms"] > df["latencia_prevista_ms"]).sum()
            / total
            * 100,
            2,
        ),
        "potencia_media_w": round(df["potencia_w"].mean(), 2),
        "registros_em_sobrecarga": int(
            (df["potencia_w"] > df["limite_potencia_w"]).sum()
        ),
    }


# =====================================================================
# 4. SALVAR E CARREGAR O CSV
# =====================================================================
def salvar_telemetria_csv(df, caminho=None):
    """Valida a base e salva em CSV. Retorna o caminho do arquivo."""
    destino = Path(caminho) if caminho else CSV_FILE_PATH

    problemas = verificar_problemas(df)
    if problemas:
        raise ValueError(
            "Base inválida, nada foi salvo:\n - " + "\n - ".join(problemas)
        )

    # Cria as pastas pai automaticamente se não existirem (substitui o os.makedirs)
    destino.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(destino, index=False, encoding="utf-8")
    return destino


def carregar_telemetria_csv(caminho=None):
    """Lê o CSV, limpa e valida. Se o arquivo for de uma versão antiga, avisa o que falta."""
    origem = Path(caminho) if caminho else CSV_FILE_PATH

    # Verifica a existência com .exists()
    if not origem.exists():
        raise FileNotFoundError(f"Arquivo de telemetria não encontrado em: {origem}")

    df = pd.read_csv(origem, encoding="utf-8")
    if all(c in df.columns for c in COLUNAS):
        df = limpar_dataset(df)

    problemas = verificar_problemas(df)
    if problemas:
        raise ValueError(
            "Arquivo fora do padrão. Rode 'python -m src.fase6_scic.dados' "
            "para gerar a base de novo.\n - " + "\n - ".join(problemas)
        )
    return df


def exportar_para_entrega(df, pasta=None):
    """Salva 'dados_aurora_siger.csv' na raiz do projeto."""
    diretorio_base = Path(pasta) if pasta else RAIZ_PROJETO
    destino = diretorio_base / "dados_aurora_siger.csv"
    return salvar_telemetria_csv(df, destino)


# =====================================================================
# 5. RESUMO NO TERMINAL
# =====================================================================
def imprimir_resumo_terminal(df, caminho):
    """Mostra a base de forma organizada no terminal."""
    import os  # Usado apenas aqui para pegar o caminho relativo no print visual

    linha = "-" * 80
    print("\n" + "=" * 80)
    print("BASE DE DADOS DA COLÔNIA - SCIC / AURORA SIGER".center(80))
    print("=" * 80)
    print("\n[1] ARQUIVO GERADO\n" + linha)
    print(f"Arquivo : {os.path.relpath(str(caminho), str(RAIZ_PROJETO))}")
    print(
        f"Registros: {len(df)}  ({df['ciclo'].nunique()} ciclos x {df['modulo_id'].nunique()} módulos)"
    )
    print(f"Colunas  : {len(df.columns)}")

    print("\n[2] AMOSTRA (primeiro ciclo)\n" + linha)
    colunas_amostra = [
        "timestamp_id",
        "nome_modulo",
        "codigo_sensor_hex",
        "latencia_observada_ms",
        "latencia_prevista_ms",
        "status_operacional",
        "prioridade",
    ]
    print(df.head(df["modulo_id"].nunique())[colunas_amostra].to_string(index=False))

    print("\n[3] VALIDAÇÃO\n" + linha)
    problemas = verificar_problemas(df)
    if problemas:
        for p in problemas:
            print(f"[ERRO] {p}")
    else:
        print("OK - nenhum problema encontrado.")

    print("\n[4] INDICADORES\n" + linha)
    for nome, valor in calcular_indicadores(df).items():
        print(f"{nome:<32} {valor}")

    print("\n[5] SITUAÇÃO DOS REGISTROS\n" + linha)
    print(df["status_operacional"].value_counts().to_string())

    print("\n[6] LATÊNCIA MÉDIA POR MÓDULO (ms)\n" + linha)
    por_modulo = (
        df.groupby("nome_modulo")[["latencia_observada_ms", "latencia_prevista_ms"]]
        .mean()
        .round(2)
    )
    print(por_modulo.sort_values("latencia_observada_ms", ascending=False).to_string())
    print("\n" + "=" * 80)


# Executando este arquivo direto, ele gera e salva a base
if __name__ == "__main__":
    dados = gerar_dataset_telemetria()
    caminho = salvar_telemetria_csv(dados)
    imprimir_resumo_terminal(dados, caminho)
