"""Banco de dados e CRUD do SIFSM  |  INTEGRANTE 1  |  Cap. 3 (erros, banco e CRUD)

Banco: SQLite (biblioteca padrão `sqlite3`), arquivo gerado em data/fase7/.
O Oracle do Cap. 3 exige servidor e credenciais; o SQLite roda em qualquer
máquina sem instalar nada (justificativa também no README).

Regras de segurança/qualidade deste módulo:
  * Consultas SEMPRE parametrizadas (`?`): dados do usuário nunca entram no texto do SQL
    (evita SQL injection). Nomes de colunas só vêm de listas fixas (whitelist).
  * Toda entrada é validada ANTES de gravar (validar_leitura) e erros previsíveis viram
    ErroBanco com mensagem clara; o restante usa try/except/else/finally.
  * A conexão é sempre fechada no `finally`.

Contrato consumido por simulacao.py, modelo_linear.py e agentes.py:
    listar_leituras(...) -> list[dict] com as colunas de `leituras` + nome_modulo,
    tipo_modulo, essencial e limite_consumo_w (vindos de `modulos`).
"""

from __future__ import annotations

import csv
import math
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
PASTA_DADOS = RAIZ_PROJETO / "data" / "fase7"
CAMINHO_BANCO = PASTA_DADOS / "aurora_siger.db"       # gerado em tempo de execução
CAMINHO_SQL = PASTA_DADOS / "script_banco.sql"
CAMINHO_CSV = PASTA_DADOS / "dados_aurora_siger.csv"

STATUS_VALIDOS = ("ativo", "alerta", "falha", "manutencao")
COLUNAS_LEITURA = (
    "modulo_id", "codigo_sensor", "data_registro", "consumo_w",
    "temperatura_c", "umidade_pct", "carga_bateria_pct", "status_operacional",
)
_PADRAO_SENSOR = re.compile(r"^0X[0-9A-F]{2}$")
_FORMATOS_DATA = ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")

_SELECT_LEITURA = (
    "SELECT l.*, m.nome AS nome_modulo, m.tipo AS tipo_modulo, "
    "m.essencial AS essencial, m.limite_consumo_w AS limite_consumo_w "
    "FROM leituras l JOIN modulos m ON m.id = l.modulo_id"
)


class ErroBanco(Exception):
    """Erro de negócio/validação do banco, com mensagem clara para o usuário."""


# ---------------------------------------------------------------------
# Conexão e criação
# ---------------------------------------------------------------------
def conectar(caminho: Optional[Path] = None) -> sqlite3.Connection:
    """Abre a conexão com linhas acessíveis por nome e chaves estrangeiras ligadas."""
    conexao = sqlite3.connect(str(caminho or CAMINHO_BANCO))
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco(caminho: Optional[Path] = None, recriar: bool = False) -> Path:
    """Cria as tabelas a partir de script_banco.sql. `recriar=True` apaga o arquivo antes."""
    destino = Path(caminho or CAMINHO_BANCO)
    destino.parent.mkdir(parents=True, exist_ok=True)
    if recriar and destino.exists():
        destino.unlink()
    conexao = conectar(destino)
    try:
        conexao.executescript(CAMINHO_SQL.read_text(encoding="utf-8"))
        conexao.commit()
    finally:
        conexao.close()
    return destino


# ---------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------
def _numero(dados: dict, campo: str, minimo=None, maximo=None, obrigatorio=False) -> Optional[float]:
    valor = dados.get(campo)
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        if obrigatorio:
            raise ErroBanco(f"O campo '{campo}' é obrigatório.")
        return None
    try:
        numero = float(str(valor).strip().replace(",", "."))
    except (TypeError, ValueError):
        raise ErroBanco(f"O campo '{campo}' deve ser numérico (recebido: {valor!r}).") from None
    if not math.isfinite(numero):
        raise ErroBanco(f"O campo '{campo}' deve ser um número finito.")
    if minimo is not None and numero < minimo:
        raise ErroBanco(f"O campo '{campo}' deve ser >= {minimo} (recebido: {numero}).")
    if maximo is not None and numero > maximo:
        raise ErroBanco(f"O campo '{campo}' deve ser <= {maximo} (recebido: {numero}).")
    return numero


def validar_leitura(dados: dict) -> dict:
    """Valida e normaliza um dicionário de leitura. Levanta ErroBanco se inválido.

    Devolve um dict com exatamente as chaves de COLUNAS_LEITURA (opcionais ausentes = None).
    """
    if not isinstance(dados, dict):
        raise ErroBanco("Os dados da leitura devem ser informados em um dicionário.")

    modulo_id = str(dados.get("modulo_id") or "").strip().upper()
    if not modulo_id:
        raise ErroBanco("O campo 'modulo_id' é obrigatório (ex.: MOD-01).")

    sensor = str(dados.get("codigo_sensor") or "").strip().upper()
    if sensor and not _PADRAO_SENSOR.match(sensor):
        raise ErroBanco(f"Código de sensor inválido: {sensor!r}. Use o formato 0x1A.")
    sensor = ("0x" + sensor[2:]) if sensor else None

    texto_data = str(dados.get("data_registro") or "").strip()
    if not texto_data:
        data_registro = datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        data_registro = None
        for formato in _FORMATOS_DATA:
            try:
                data_registro = datetime.strptime(texto_data, formato).strftime("%Y-%m-%d %H:%M")
                break
            except ValueError:
                continue
        if data_registro is None:
            raise ErroBanco(f"Data inválida: {texto_data!r}. Use AAAA-MM-DD HH:MM.")

    status = str(dados.get("status_operacional") or "ativo").strip().lower()
    if status not in STATUS_VALIDOS:
        raise ErroBanco(f"Status inválido: {status!r}. Use um de: {', '.join(STATUS_VALIDOS)}.")

    return {
        "modulo_id": modulo_id,
        "codigo_sensor": sensor,
        "data_registro": data_registro,
        "consumo_w": _numero(dados, "consumo_w", minimo=0, maximo=1_000_000, obrigatorio=True),
        "temperatura_c": _numero(dados, "temperatura_c", minimo=-150, maximo=150),
        "umidade_pct": _numero(dados, "umidade_pct", minimo=0, maximo=100),
        "carga_bateria_pct": _numero(dados, "carga_bateria_pct", minimo=0, maximo=100),
        "status_operacional": status,
    }


def _traduzir_integridade(erro: sqlite3.IntegrityError) -> str:
    texto = str(erro)
    if "FOREIGN KEY" in texto:
        return "Módulo ou sensor não cadastrado. Confira o 'modulo_id' e o código do sensor."
    if "CHECK" in texto or "NOT NULL" in texto:
        return f"Valor fora das regras do banco: {texto}"
    return f"Violação de integridade: {texto}"


# ---------------------------------------------------------------------
# CRUD de leituras
# ---------------------------------------------------------------------
def cadastrar_leitura(dados: dict, caminho_banco: Optional[Path] = None) -> int:
    """CREATE: valida, insere e devolve o id da nova leitura."""
    leitura = validar_leitura(dados)
    colunas = ", ".join(COLUNAS_LEITURA)
    marcadores = ", ".join("?" for _ in COLUNAS_LEITURA)
    conexao = conectar(caminho_banco)
    try:
        cursor = conexao.execute(
            f"INSERT INTO leituras ({colunas}) VALUES ({marcadores})",  # colunas fixas, valores por parâmetro
            tuple(leitura[c] for c in COLUNAS_LEITURA),
        )
        conexao.commit()
    except sqlite3.IntegrityError as erro:
        conexao.rollback()
        raise ErroBanco(_traduzir_integridade(erro)) from erro
    except sqlite3.Error as erro:
        conexao.rollback()
        raise ErroBanco(f"Falha ao gravar no banco: {erro}") from erro
    else:
        return int(cursor.lastrowid)
    finally:
        conexao.close()


def listar_leituras(
    modulo_id: Optional[str] = None,
    status: Optional[str] = None,
    limite: Optional[int] = 50,
    caminho_banco: Optional[Path] = None,
    ordem: str = "desc",
) -> list[dict]:
    """READ: lista de dicionários (uma por leitura), com filtros opcionais.

    `limite=None` devolve tudo. `ordem` = 'desc' (mais recentes primeiro) ou 'asc'
    (cronológica, útil para séries temporais e simulação).
    """
    condicoes: list[str] = []
    parametros: list = []
    if modulo_id:
        condicoes.append("l.modulo_id = ?")
        parametros.append(str(modulo_id).strip().upper())
    if status:
        status = str(status).strip().lower()
        if status not in STATUS_VALIDOS:
            raise ErroBanco(f"Status inválido: {status!r}. Use um de: {', '.join(STATUS_VALIDOS)}.")
        condicoes.append("l.status_operacional = ?")
        parametros.append(status)
    if ordem not in ("asc", "desc"):
        raise ErroBanco("A ordem deve ser 'asc' ou 'desc'.")

    sql = _SELECT_LEITURA
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
    sql += f" ORDER BY l.data_registro {ordem.upper()}, l.id {ordem.upper()}"  # `ordem` validada acima
    if limite is not None:
        try:
            limite = int(limite)
        except (TypeError, ValueError):
            raise ErroBanco("O limite deve ser um número inteiro.") from None
        if limite < 1:
            raise ErroBanco("O limite deve ser >= 1.")
        sql += " LIMIT ?"
        parametros.append(limite)

    conexao = conectar(caminho_banco)
    try:
        return [dict(linha) for linha in conexao.execute(sql, parametros)]
    except sqlite3.Error as erro:
        raise ErroBanco(f"Falha ao consultar o banco: {erro}") from erro
    finally:
        conexao.close()


def buscar_leitura(id_leitura: int, caminho_banco: Optional[Path] = None) -> Optional[dict]:
    """READ de um registro; devolve None se não existir."""
    conexao = conectar(caminho_banco)
    try:
        linha = conexao.execute(_SELECT_LEITURA + " WHERE l.id = ?", (int(id_leitura),)).fetchone()
    except (TypeError, ValueError):
        raise ErroBanco("O id da leitura deve ser um número inteiro.") from None
    except sqlite3.Error as erro:
        raise ErroBanco(f"Falha ao consultar o banco: {erro}") from erro
    else:
        return dict(linha) if linha else None
    finally:
        conexao.close()


def alterar_leitura(id_leitura: int, campos: dict, caminho_banco: Optional[Path] = None) -> bool:
    """UPDATE: altera só os campos informados (todos revalidados). True se alterou algo."""
    atual = buscar_leitura(id_leitura, caminho_banco)
    if atual is None:
        return False
    permitidos = {c: v for c, v in (campos or {}).items() if c in COLUNAS_LEITURA}
    if not permitidos:
        raise ErroBanco("Nenhum campo válido para alterar. Campos: " + ", ".join(COLUNAS_LEITURA))

    mesclado = {c: atual[c] for c in COLUNAS_LEITURA}
    mesclado.update(permitidos)
    validado = validar_leitura(mesclado)

    colunas = list(permitidos)  # nomes vêm da whitelist COLUNAS_LEITURA, nunca do usuário
    atribuicoes = ", ".join(f"{c} = ?" for c in colunas)
    conexao = conectar(caminho_banco)
    try:
        cursor = conexao.execute(
            f"UPDATE leituras SET {atribuicoes} WHERE id = ?",
            [validado[c] for c in colunas] + [int(id_leitura)],
        )
        conexao.commit()
    except sqlite3.IntegrityError as erro:
        conexao.rollback()
        raise ErroBanco(_traduzir_integridade(erro)) from erro
    except sqlite3.Error as erro:
        conexao.rollback()
        raise ErroBanco(f"Falha ao alterar no banco: {erro}") from erro
    else:
        return cursor.rowcount > 0
    finally:
        conexao.close()


def excluir_leitura(id_leitura: int, caminho_banco: Optional[Path] = None) -> bool:
    """DELETE: remove a leitura. True se existia. (A confirmação é feita no menu.)"""
    conexao = conectar(caminho_banco)
    try:
        cursor = conexao.execute("DELETE FROM leituras WHERE id = ?", (int(id_leitura),))
        conexao.commit()
    except (TypeError, ValueError):
        raise ErroBanco("O id da leitura deve ser um número inteiro.") from None
    except sqlite3.Error as erro:
        conexao.rollback()
        raise ErroBanco(f"Falha ao excluir no banco: {erro}") from erro
    else:
        return cursor.rowcount > 0
    finally:
        conexao.close()


def restaurar_leitura(registro: dict, caminho_banco: Optional[Path] = None) -> int:
    """Reinsere uma leitura excluída mantendo o MESMO id (usado em 'desfazer' - pilha)."""
    leitura = validar_leitura(registro)
    conexao = conectar(caminho_banco)
    try:
        conexao.execute(
            "INSERT INTO leituras (id, " + ", ".join(COLUNAS_LEITURA) + ") VALUES (?, "
            + ", ".join("?" for _ in COLUNAS_LEITURA) + ")",
            (int(registro["id"]),) + tuple(leitura[c] for c in COLUNAS_LEITURA),
        )
        conexao.commit()
    except (KeyError, TypeError, ValueError):
        raise ErroBanco("Registro sem 'id' válido para restaurar.") from None
    except sqlite3.IntegrityError as erro:
        conexao.rollback()
        raise ErroBanco(_traduzir_integridade(erro)) from erro
    else:
        return int(registro["id"])
    finally:
        conexao.close()


def contar_leituras(caminho_banco: Optional[Path] = None) -> int:
    conexao = conectar(caminho_banco)
    try:
        return int(conexao.execute("SELECT COUNT(*) FROM leituras").fetchone()[0])
    finally:
        conexao.close()


# ---------------------------------------------------------------------
# Módulos, sensores, alertas e chamados
# ---------------------------------------------------------------------
def listar_modulos(caminho_banco: Optional[Path] = None) -> list[dict]:
    """Lista os módulos cadastrados (id, nome, tipo, essencial, limite_consumo_w, status)."""
    conexao = conectar(caminho_banco)
    try:
        return [dict(l) for l in conexao.execute("SELECT * FROM modulos ORDER BY id")]
    finally:
        conexao.close()


def listar_sensores(caminho_banco: Optional[Path] = None) -> list[dict]:
    conexao = conectar(caminho_banco)
    try:
        return [dict(l) for l in conexao.execute("SELECT * FROM sensores ORDER BY codigo_hex")]
    finally:
        conexao.close()


def registrar_alerta(
    modulo_id: str, tipo: str, prioridade: str, mensagem: str,
    leitura_id: Optional[int] = None, caminho_banco: Optional[Path] = None,
) -> int:
    """Grava um alerta gerado pela regra booleana. prioridade: baixa|media|alta|critica."""
    conexao = conectar(caminho_banco)
    try:
        cursor = conexao.execute(
            "INSERT INTO alertas (modulo_id, leitura_id, tipo, prioridade, mensagem, criado_em) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (modulo_id, leitura_id, tipo, prioridade, mensagem, datetime.now().strftime("%Y-%m-%d %H:%M")),
        )
        conexao.commit()
    except sqlite3.IntegrityError as erro:
        conexao.rollback()
        raise ErroBanco(_traduzir_integridade(erro)) from erro
    else:
        return int(cursor.lastrowid)
    finally:
        conexao.close()


def listar_alertas(apenas_abertos: bool = True, caminho_banco: Optional[Path] = None) -> list[dict]:
    conexao = conectar(caminho_banco)
    try:
        sql = "SELECT * FROM alertas" + (" WHERE resolvido = 0" if apenas_abertos else "") + " ORDER BY id"
        return [dict(l) for l in conexao.execute(sql)]
    finally:
        conexao.close()


def cadastrar_chamado(modulo_id: Optional[str], descricao: str, prioridade: int = 3,
                      caminho_banco: Optional[Path] = None) -> int:
    """Registra um chamado da tripulação (alimenta a FilaChamados)."""
    descricao = (descricao or "").strip()
    if not descricao:
        raise ErroBanco("A descrição do chamado é obrigatória.")
    conexao = conectar(caminho_banco)
    try:
        cursor = conexao.execute(
            "INSERT INTO chamados (modulo_id, descricao, prioridade, criado_em) VALUES (?, ?, ?, ?)",
            (modulo_id, descricao, int(prioridade), datetime.now().strftime("%Y-%m-%d %H:%M")),
        )
        conexao.commit()
    except (sqlite3.IntegrityError, ValueError, TypeError) as erro:
        conexao.rollback()
        raise ErroBanco(f"Chamado inválido: {erro}") from erro
    else:
        return int(cursor.lastrowid)
    finally:
        conexao.close()


def listar_chamados(status: str = "aberto", caminho_banco: Optional[Path] = None) -> list[dict]:
    """Chamados na ordem de chegada (id crescente), prontos para entrar na fila FIFO."""
    conexao = conectar(caminho_banco)
    try:
        return [dict(l) for l in conexao.execute(
            "SELECT * FROM chamados WHERE status = ? ORDER BY id", (status,))]
    finally:
        conexao.close()


def semear_chamados_exemplo(caminho_banco: Optional[Path] = None) -> int:
    """Cria alguns chamados de exemplo se a tabela estiver vazia. Devolve quantos criou."""
    conexao = conectar(caminho_banco)
    try:
        existentes = conexao.execute("SELECT COUNT(*) FROM chamados").fetchone()[0]
    finally:
        conexao.close()
    if existentes:
        return 0
    exemplos = [
        ("MOD-05", "Verificar sensor de temperatura do Suporte Médico", 2),
        ("MOD-06", "Irrigação da Estufa abaixo do esperado", 3),
        ("MOD-01", "Troca de filtro de ar na Habitação", 4),
        ("MOD-08", "Consumo acima do normal na Produção de Oxigênio", 1),
        ("MOD-02", "Calibrar antena da Comunicação Central", 3),
    ]
    for modulo, texto, prioridade in exemplos:
        cadastrar_chamado(modulo, texto, prioridade, caminho_banco)
    return len(exemplos)


# ---------------------------------------------------------------------
# Carga inicial a partir do CSV
# ---------------------------------------------------------------------
def carregar_csv_para_banco(
    caminho_csv: Optional[Path] = None,
    caminho_banco: Optional[Path] = None,
    limpar: bool = False,
) -> int:
    """Importa dados_aurora_siger.csv (módulos, sensores e leituras) para o banco.

    Linhas inválidas são ignoradas (e contadas); se o arquivo não existir ou nenhuma linha
    for válida, levanta ErroBanco. `limpar=True` esvazia as tabelas antes. Devolve o número de
    leituras inseridas.
    """
    origem = Path(caminho_csv or CAMINHO_CSV)
    if not origem.exists():
        raise ErroBanco(f"Arquivo de dados não encontrado: {origem}. "
                        "Gere-o com: python -m src.fase7_sifsm.dados_simulados")

    conexao = conectar(caminho_banco)
    inseridas = invalidas = 0
    try:
        if limpar:
            for tabela in ("alertas", "chamados", "leituras", "sensores", "modulos"):
                conexao.execute(f"DELETE FROM {tabela}")  # nomes fixos acima, sem entrada do usuário
        with open(origem, encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo):
                try:
                    leitura = validar_leitura(linha)
                    conexao.execute(
                        "INSERT OR IGNORE INTO modulos (id, nome, tipo, essencial, limite_consumo_w) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (leitura["modulo_id"], linha.get("nome_modulo") or leitura["modulo_id"],
                         linha.get("tipo_modulo") or "desconhecido",
                         1 if str(linha.get("essencial", "0")).strip() == "1" else 0,
                         float(linha.get("limite_consumo_w") or 6500)),
                    )
                    if leitura["codigo_sensor"]:
                        conexao.execute(
                            "INSERT OR IGNORE INTO sensores (codigo_hex, modulo_id, tipo) VALUES (?, ?, ?)",
                            (leitura["codigo_sensor"], leitura["modulo_id"], linha.get("tipo_sensor") or "geral"),
                        )
                    conexao.execute(
                        "INSERT INTO leituras (" + ", ".join(COLUNAS_LEITURA) + ") VALUES ("
                        + ", ".join("?" for _ in COLUNAS_LEITURA) + ")",
                        tuple(leitura[c] for c in COLUNAS_LEITURA),
                    )
                    inseridas += 1
                except (ErroBanco, ValueError, sqlite3.IntegrityError):
                    invalidas += 1
        if inseridas == 0 and invalidas:
            raise ErroBanco(f"Nenhuma linha válida no CSV ({invalidas} inválidas).")
        conexao.commit()
    except sqlite3.Error as erro:
        conexao.rollback()
        raise ErroBanco(f"Falha ao importar o CSV: {erro}") from erro
    except ErroBanco:
        conexao.rollback()
        raise
    finally:
        conexao.close()
    return inseridas
