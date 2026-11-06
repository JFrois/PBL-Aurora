"""Testes da regra booleana e da tabela-verdade da Fase 7."""

import pytest

from src.fase7_sifsm import logica


def test_tabela_verdade_completa():
    tabela = logica.tabela_verdade()
    assert len(tabela) == 8
    verdadeiras = [linha[:3] for linha in tabela if linha[3]]
    assert verdadeiras == [(True, True, True)]  # alerta só com as três condições


def test_de_morgan():
    for a, b, c, saida in logica.tabela_verdade():
        assert (not saida) == ((not a) or (not b) or (not c))


def test_bloqueio_e_negacao_do_sensor():
    assert logica.bloquear_operacao(False) is True
    assert logica.bloquear_operacao(True) is False


def test_consumo_alto_usa_90_por_cento():
    assert logica.consumo_alto(5800, 6000) is True
    assert logica.consumo_alto(5400, 6000) is False
    with pytest.raises(ValueError):
        logica.consumo_alto(100, 0)
    with pytest.raises(ValueError):
        logica.consumo_alto("x", 100)


def test_sensor_valido():
    assert logica.sensor_valido({"consumo_w": 100, "temperatura_c": 20, "status_operacional": "ativo"})
    assert not logica.sensor_valido({"consumo_w": 100, "status_operacional": "falha"})
    assert not logica.sensor_valido({"consumo_w": 100, "temperatura_c": 500, "status_operacional": "ativo"})
    assert not logica.sensor_valido({"consumo_w": None, "status_operacional": "ativo"})


@pytest.mark.parametrize("consumo,status,critico,esperado", [
    (6000, "alerta", True, "alto"),
    (6000, "alerta", False, "medio"),
    (1000, "ativo", True, "baixo"),
    (6000, "falha", True, "bloqueado"),
])
def test_classificar_risco(consumo, status, critico, esperado):
    leitura = {"consumo_w": consumo, "temperatura_c": 22, "status_operacional": status}
    assert logica.classificar_risco(leitura, 6500, critico) == esperado
