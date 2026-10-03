"""Testes unitários das estruturas do Analista 3 (Heap e Trie)."""

import random

import pandas as pd

from src.fase6_scic.estruturas import (
    Alerta,
    HeapAlertas,
    TrieModulos,
    calcular_criticidade,
    construir_trie,
)


def _alerta(crit, i=0):
    return Alerta(crit, i, 0, "MOD", "teste", "0x00", "alerta", 1, "msg")


def test_heap_extrai_em_ordem_decrescente():
    heap = HeapAlertas()
    valores = [random.Random(1).uniform(0, 100) for _ in range(200)]
    for i, v in enumerate(valores):
        heap.inserir(_alerta(v, i))
        assert heap.validar_invariante()
    extraidos = [heap.extrair_mais_critico().criticidade for _ in range(len(valores))]
    assert extraidos == sorted(valores, reverse=True)
    assert heap.esta_vazio()


def test_heap_desempate_pelo_mais_antigo():
    heap = HeapAlertas()
    heap.inserir(_alerta(50, 1))
    heap.inserir(_alerta(50, 2))
    assert heap.extrair_mais_critico().timestamp_id == 1


def test_top_n_nao_altera_fila():
    heap = HeapAlertas()
    for i, v in enumerate([10, 90, 40, 70]):
        heap.inserir(_alerta(v, i))
    assert [a.criticidade for a in heap.top_n(2)] == [90, 70]
    assert len(heap) == 4 and heap.espiar().criticidade == 90


def test_criticidade_sobrecarga_maior_que_nominal():
    base = {"essencial": 1, "prioridade": 3, "potencia_w": 5000, "limite_potencia_w": 6500}
    nominal, _ = calcular_criticidade({**base, "status_operacional": "ativo",
                                       "mensagem_alerta": "Operação nominal"})
    critico, motivos = calcular_criticidade({**base, "status_operacional": "alerta",
                                             "mensagem_alerta": "Sobrecarga de potência no barramento",
                                             "potencia_w": 7000})
    assert critico > nominal and motivos


def test_trie_prefixo_ignora_acento_e_caixa():
    trie = TrieModulos()
    trie.inserir("Comunicação Central", "MOD-02")
    trie.inserir("Controle de Missão", "MOD-03")
    assert set(trie.autocompletar("CO")) == {"MOD-02", "MOD-03"}
    assert trie.autocompletar("comunicacao") == ["MOD-02"]
    assert trie.buscar_prefixo("xyz") == {}
    assert trie.buscar_exato("controle de missao") == {"MOD-03": {}}


def test_construir_trie_com_sensores_hex():
    df = pd.DataFrame([
        {"modulo_id": "MOD-02", "nome_modulo": "Comunicação Central", "tipo_modulo": "comunicacao",
         "essencial": 1, "limite_potencia_w": 6500.0, "codigo_sensor_hex": "0x2A"},
        {"modulo_id": "MOD-02", "nome_modulo": "Comunicação Central", "tipo_modulo": "comunicacao",
         "essencial": 1, "limite_potencia_w": 6500.0, "codigo_sensor_hex": "0x2B"},
    ])
    trie = construir_trie(df, incluir_comandos=False)
    res = trie.buscar_prefixo("0x2")
    assert len(res) == 2
    assert all(d["categoria"] == "sensor" for d in res.values())
    assert "MOD-02 - Comunicação Central" in trie.buscar_prefixo("central")
