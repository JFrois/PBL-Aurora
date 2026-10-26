"""Testes das estruturas de dados da Fase 7 (fila, pilha, hash e heap)."""

import pytest

from src.fase7_sifsm import banco, dados_simulados
from src.fase7_sifsm.estruturas import FilaChamados, PilhaHistorico, TabelaSensores, montar_heap_de_alertas


def test_fila_e_fifo():
    fila = FilaChamados()
    for i in range(3):
        fila.enfileirar({"id": i, "descricao": f"c{i}"})
    assert [fila.atender()["id"] for _ in range(3)] == [0, 1, 2]
    assert fila.atender() is None and len(fila) == 0
    with pytest.raises(ValueError):
        fila.enfileirar({"descricao": ""})


def test_pilha_e_lifo_e_limite():
    pilha = PilhaHistorico(limite=3)
    for i in range(5):
        pilha.empilhar({"acao": "x", "id": i})
    assert len(pilha) == 3 and pilha.topo()["id"] == 4
    assert [pilha.desempilhar()["id"] for _ in range(3)] == [4, 3, 2]
    assert pilha.desempilhar() is None


def test_hash_insere_busca_remove_e_redimensiona():
    tabela = TabelaSensores(capacidade=2)
    codigos = [f"0x{i:02X}" for i in range(40)]
    for c in codigos:
        tabela.inserir(c, {"codigo": c})
    assert len(tabela) == 40 and tabela.estatisticas()["capacidade"] > 2
    assert all(tabela.buscar(c)["codigo"] == c for c in codigos)
    assert tabela.buscar("0x1a")["codigo"] == "0x1A"  # busca sem diferenciar maiúsculas
    assert tabela.remover("0x05") and tabela.buscar("0x05") is None and not tabela.remover("0x05")
    tabela.inserir("0x01", "novo")  # atualiza, não duplica
    assert len(tabela) == 39 and tabela.buscar("0x01") == "novo"


def test_heap_prioriza_alertas_reais(tmp_path):
    pytest.importorskip("pandas")
    caminho = tmp_path / "t.db"
    banco.inicializar_banco(caminho)
    csv = dados_simulados.salvar_csv(dados_simulados.gerar_leituras(), tmp_path / "d.csv")
    banco.carregar_csv_para_banco(csv, caminho)
    heap = montar_heap_de_alertas(banco.listar_leituras(limite=None, caminho_banco=caminho))
    assert len(heap) > 0
    top = heap.top_n(len(heap))
    criticidades = [a.criticidade for a in top]
    assert criticidades == sorted(criticidades, reverse=True)
