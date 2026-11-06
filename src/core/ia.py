"""Acesso opcional a um LLM (Gemini), compartilhado pelos módulos da Fase 7.

A IA é OPCIONAL (item 2.3 do enunciado): sem biblioteca `google-genai`, sem
GEMINI_API_KEY ou sem rede, o sistema continua funcionando com a resposta de
contingência (`fallback`) que quem chama fornece. Assim a correção roda em
qualquer máquina, sem credenciais.
"""

from __future__ import annotations

import os
from typing import Callable, Optional, Union

try:  # python-dotenv é opcional
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

_MODELO = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
_cliente = None
_tentou_criar = False


def _obter_cliente():
    """Cria o cliente Gemini uma única vez; devolve None se indisponível."""
    global _cliente, _tentou_criar
    if _tentou_criar:
        return _cliente
    _tentou_criar = True
    chave = os.getenv("GEMINI_API_KEY")
    if not chave:
        return None
    try:
        from google import genai

        _cliente = genai.Client(api_key=chave)
    except ImportError:
        _cliente = None
    return _cliente


def ia_disponivel() -> bool:
    """True se há cliente Gemini configurado (biblioteca + chave)."""
    return _obter_cliente() is not None


def perguntar(prompt: str, fallback: Union[str, Callable[[str], str], None] = None) -> str:
    """Envia `prompt` ao LLM; em qualquer falha devolve o `fallback`.

    `fallback` pode ser um texto ou uma função que recebe o prompt e devolve
    a resposta simulada (ex.: a lógica por regras dos agentes).
    """

    def _contingencia() -> str:
        if callable(fallback):
            return fallback(prompt)
        return fallback or "[IA indisponível] Resposta não gerada."

    cliente = _obter_cliente()
    if cliente is None:
        return _contingencia()
    try:
        resposta = cliente.models.generate_content(model=_MODELO, contents=prompt)
        texto = (resposta.text or "").strip()
        return texto or _contingencia()
    except Exception:  # rede, cota, modelo inexistente etc.
        return _contingencia()
