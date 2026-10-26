"""Sistema multiagente simulado  |  INTEGRANTE 2  |  Caps. 8 e 9

Padrão do projeto: a regra DETERMINÍSTICA decide, a IA só explica.
Funciona sem chave de API: cada agente responde por regras; o LLM (src/core/ia.py,
Gemini) é opcional e entra apenas para redigir/explicar, sempre com fallback.

Arquitetura-alvo (descrever no relatório, inclusive o fluxo com LLM real):
    entrada -> guardrail de entrada -> Triador --handoff--> Especialista
            -> ferramentas determinísticas (banco, risco, previsão)
            -> guardrail de saída -> resposta (+ histórico da sessão + tracing)
Agentes: Triador, Energia, Manutenção, Dados.
Ferramentas: consultar leituras (banco.py), classificar risco (logica.py),
prever consumo (modelo_linear.py).
Guardrails: bloquear fora de escopo/ações perigosas (ex.: "desligue o suporte
de vida"), limitar tamanho da entrada, exigir validação humana para ações críticas.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Sessao:
    """Contexto da conversa: histórico e trilha de execução (tracing)."""

    historico: list[dict] = field(default_factory=list)
    trilha: list[str] = field(default_factory=list)


# ----- Guardrails ---------------------------------------------------------
def guardrail_entrada(texto: str) -> tuple[bool, str]:
    """(permitido, motivo). Bloqueia vazio, excesso de tamanho e pedidos fora do escopo/perigosos."""
    raise NotImplementedError("Integrante 2: implementar guardrail_entrada()")


def guardrail_saida(resposta: str) -> tuple[bool, str]:
    """(aprovada, motivo). Garante que a resposta não executa ação crítica sem validação humana."""
    raise NotImplementedError("Integrante 2: implementar guardrail_saida()")


# ----- Ferramentas determinísticas ---------------------------------------
def ferramenta_consultar_leituras(modulo_id: str | None = None) -> list[dict]:
    raise NotImplementedError("Integrante 2: implementar ferramenta_consultar_leituras()")


def ferramenta_classificar_risco(modulo_id: str) -> str:
    raise NotImplementedError("Integrante 2: implementar ferramenta_classificar_risco()")


def ferramenta_prever_consumo(modulo_id: str) -> float:
    raise NotImplementedError("Integrante 2: implementar ferramenta_prever_consumo()")


# ----- Agentes ------------------------------------------------------------
def agente_triador(texto: str, sessao: Sessao) -> str:
    """Interpreta o pedido e devolve o nome do especialista: 'energia' | 'manutencao' | 'dados'."""
    raise NotImplementedError("Integrante 2: implementar agente_triador()")


def agente_energia(texto: str, sessao: Sessao) -> str:
    raise NotImplementedError("Integrante 2: implementar agente_energia()")


def agente_manutencao(texto: str, sessao: Sessao) -> str:
    raise NotImplementedError("Integrante 2: implementar agente_manutencao()")


def agente_dados(texto: str, sessao: Sessao) -> str:
    raise NotImplementedError("Integrante 2: implementar agente_dados()")


def executar_assistente(texto: str, sessao: Sessao | None = None) -> str:
    """Fluxo completo com handoff, guardrails, histórico e tracing. Registra em sessao.trilha."""
    raise NotImplementedError("Integrante 2: implementar executar_assistente()")


def menu_assistente() -> None:
    """Laço interativo do menu (digite 'sair' para voltar)."""
    raise NotImplementedError("Integrante 2: implementar menu_assistente()")
