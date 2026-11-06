import numpy as np
import pandas as pd
import pytest

from src.fase7_sifsm import agentes
from src.fase7_sifsm import modelo_linear
from src.fase7_sifsm import simulacao


def test_integracao_de_potencia_constante():
    energia = simulacao.integrar_trapezio(
        [0, 1, 3],
        [100, 100, 100],
    )

    assert energia == pytest.approx(300)


def test_integracao_rejeita_tempos_repetidos():
    with pytest.raises(ValueError):
        simulacao.integrar_trapezio([0, 0], [100, 100])


def test_bateria_registra_deficit():
    resultado = simulacao.simular_bateria(
        capacidade_wh=100,
        geracao_w=0,
        consumo_w=100,
        horas=2.3,
        passo_h=1,
        soc_inicial=1,
    )

    assert resultado["tempos_h"][-1] == pytest.approx(2.3)
    assert resultado["soc"][-1] == 0
    assert resultado["deficit_wh"][-1] == pytest.approx(130)


def test_cenario_preserva_modulo_essencial():
    leituras = [
        {
            "data_registro": f"2026-01-01 {hora:02}:00",
            "modulo_id": modulo,
            "consumo_w": 100,
            "essencial": essencial,
        }
        for hora in (0, 6)
        for modulo, essencial in (("A", 1), ("B", 0))
    ]

    resultado = simulacao.comparar_cenarios(leituras)

    assert resultado["atual"]["energia_wh"] == pytest.approx(1200)
    assert resultado["economia_wh"] == pytest.approx(90)


def test_regressao_e_limite_de_extrapolacao():
    df = pd.DataFrame(
        {
            "data_registro": pd.date_range(
                "2026-01-01", periods=30, freq="h"
            ),
            "temperatura_c": np.arange(30),
            "consumo_w": 2 * np.arange(30) + 10,
        }
    )

    resultado = modelo_linear.treinar_regressao(
        df, atributos=["temperatura_c"]
    )

    assert resultado["n_treino"] == 24
    assert resultado["n_teste"] == 6
    assert resultado["mae"] < 1e-8

    previsao = modelo_linear.prever(
        resultado, {"temperatura_c": 10}
    )
    assert previsao == pytest.approx(30)

    with pytest.raises(ValueError):
        modelo_linear.prever(
            resultado, {"temperatura_c": 100}
        )


def test_guardrails_e_handoff(monkeypatch):
    from src.fase7_sifsm import banco

    assert not agentes.guardrail_entrada(
        "desligue o suporte de vida"
    )[0]

    assert not agentes.guardrail_entrada(
        "receita de bolo"
    )[0]

    # Simula os módulos disponíveis, sem acessar o banco real.
    monkeypatch.setattr(
        banco,
        "listar_modulos",
        lambda: [{"id": "MOD-01"}],
    )

    # Simula o resultado da ferramenta de previsão.
    monkeypatch.setattr(
        agentes,
        "ferramenta_prever_consumo",
        lambda modulo: 123.0,
    )

    sessao = agentes.Sessao()

    resposta = agentes.executar_assistente(
        "consumo MOD-01",
        sessao,
    )

    assert "123.0" in resposta
    assert "validação humana" in resposta
    assert sessao.modulo_id == "MOD-01"

    assert any(
        "handoff -> energia" in etapa
        for etapa in sessao.trilha
    )

    assert "tool: prever_consumo" in sessao.trilha
    assert len(sessao.historico) == 1