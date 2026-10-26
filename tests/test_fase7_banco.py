"""Testes do banco/CRUD da Fase 7 (usam um banco temporário, nunca o real)."""

import pytest

from src.fase7_sifsm import banco, dados_simulados


@pytest.fixture()
def db(tmp_path):
    caminho = tmp_path / "teste.db"
    banco.inicializar_banco(caminho)
    csv = dados_simulados.salvar_csv(dados_simulados.gerar_leituras(), tmp_path / "dados.csv")
    banco.carregar_csv_para_banco(csv, caminho)
    return caminho


def _leitura(**extra):
    base = {"modulo_id": "MOD-01", "consumo_w": 1500, "temperatura_c": 22, "status_operacional": "ativo"}
    base.update(extra)
    return base


def test_carga_do_csv_tem_dados_suficientes(db):
    assert banco.contar_leituras(db) == 120
    assert len(banco.listar_modulos(db)) == 8
    assert len(banco.listar_sensores(db)) == 16


def test_cadastrar_e_buscar(db):
    novo = banco.cadastrar_leitura(_leitura(consumo_w="1234,5"), db)
    leitura = banco.buscar_leitura(novo, db)
    assert leitura["modulo_id"] == "MOD-01" and leitura["consumo_w"] == pytest.approx(1234.5)
    assert leitura["nome_modulo"] == "Habitação Alfa"


def test_listar_com_filtros_e_limite(db):
    todas = banco.listar_leituras(limite=None, caminho_banco=db)
    assert len(todas) == 120
    so_mod = banco.listar_leituras("mod-02", limite=None, caminho_banco=db)
    assert len(so_mod) == 15 and all(l["modulo_id"] == "MOD-02" for l in so_mod)
    assert len(banco.listar_leituras(limite=5, caminho_banco=db)) == 5
    falhas = banco.listar_leituras(status="falha", limite=None, caminho_banco=db)
    assert len(falhas) == 1


def test_alterar_revalida_e_persiste(db):
    novo = banco.cadastrar_leitura(_leitura(), db)
    assert banco.alterar_leitura(novo, {"consumo_w": 2000, "status_operacional": "alerta"}, db)
    leitura = banco.buscar_leitura(novo, db)
    assert leitura["consumo_w"] == 2000 and leitura["status_operacional"] == "alerta"
    with pytest.raises(banco.ErroBanco):
        banco.alterar_leitura(novo, {"umidade_pct": 150}, db)
    assert banco.alterar_leitura(99999, {"consumo_w": 1}, db) is False


def test_excluir_e_restaurar(db):
    novo = banco.cadastrar_leitura(_leitura(), db)
    registro = banco.buscar_leitura(novo, db)
    assert banco.excluir_leitura(novo, db) is True
    assert banco.buscar_leitura(novo, db) is None
    assert banco.excluir_leitura(novo, db) is False
    banco.restaurar_leitura(registro, db)
    assert banco.buscar_leitura(novo, db)["consumo_w"] == 1500


@pytest.mark.parametrize("dados", [
    _leitura(modulo_id=""),
    _leitura(consumo_w="abc"),
    _leitura(consumo_w=-5),
    _leitura(consumo_w=None),
    _leitura(umidade_pct=101),
    _leitura(status_operacional="quebrado"),
    _leitura(codigo_sensor="XYZ"),
    _leitura(data_registro="ontem"),
    _leitura(consumo_w=float("nan")),
])
def test_entradas_invalidas_sao_rejeitadas(db, dados):
    with pytest.raises(banco.ErroBanco):
        banco.cadastrar_leitura(dados, db)


def test_modulo_inexistente_vira_erro_claro(db):
    with pytest.raises(banco.ErroBanco, match="não cadastrado"):
        banco.cadastrar_leitura(_leitura(modulo_id="MOD-99"), db)


def test_sql_injection_nao_funciona(db):
    antes = banco.contar_leituras(db)
    assert banco.listar_leituras("MOD-01'; DROP TABLE leituras; --", limite=None, caminho_banco=db) == []
    assert banco.contar_leituras(db) == antes


def test_csv_ausente_gera_erro_claro(tmp_path):
    caminho = tmp_path / "x.db"
    banco.inicializar_banco(caminho)
    with pytest.raises(banco.ErroBanco, match="não encontrado"):
        banco.carregar_csv_para_banco(tmp_path / "nao_existe.csv", caminho)


def test_alertas_e_chamados(db):
    nid = banco.registrar_alerta("MOD-01", "regra_booleana", "critica", "teste", caminho_banco=db)
    assert len(banco.listar_alertas(caminho_banco=db)) == 1 and nid == 1
    assert banco.semear_chamados_exemplo(db) == 5
    assert banco.semear_chamados_exemplo(db) == 0
    ids = [c["id"] for c in banco.listar_chamados(caminho_banco=db)]
    assert ids == sorted(ids)
    with pytest.raises(banco.ErroBanco):
        banco.cadastrar_chamado("MOD-01", "  ", 3, db)
