"""SIFSM - Sistema Integrado de Futuro Sustentável em Marte (Fase 7 - PBL Aurora Siger).

Arquivo principal da entrega: menu de navegação no terminal.

Como executar (na raiz do projeto):
    python codigo_fonte.py

Cada opção chama um módulo de src/fase7_sifsm/. Funcionalidades ainda não
implementadas avisam qual integrante é responsável, sem derrubar o menu.
A Fase 6 (SCIC) continua disponível em:
    python -m src.fases_anteriores.fase6_scic.fase6_scic
"""

from __future__ import annotations

import sqlite3

from src.core.utils import exibir_cabecalho, pausar
from src.fase7_sifsm.banco import ErroBanco
from src.fase7_sifsm.estruturas import PilhaHistorico

# Pilha com o histórico de ações do CRUD nesta sessão (usada por "Desfazer" e pela opção 7)
historico = PilhaHistorico()


# ---------------------------------------------------------------------
# Execução segura de cada opção do menu
# ---------------------------------------------------------------------
def executar_opcao(funcao) -> None:
    """Roda a opção tratando pendências e erros previsíveis, sem fechar o menu."""
    try:
        funcao()
    except NotImplementedError as pendencia:
        print(f"\n[Em implementação] {pendencia}")
    except (ErroBanco, ValueError, sqlite3.Error) as erro:
        print(f"\n[Erro] Não foi possível concluir a operação: {erro}")
    except KeyboardInterrupt:
        print("\n[Cancelado pelo usuário]")
    pausar()


# ---------------------------------------------------------------------
# Opções do menu (imports dentro das funções: o menu abre mesmo se um módulo falhar)
# ---------------------------------------------------------------------
def _pedir(rotulo: str, padrao: str = "") -> str:
    """Lê um texto do usuário; Enter mantém o valor padrão."""
    sufixo = f" [{padrao}]" if padrao != "" else ""
    return input(f"  {rotulo}{sufixo}: ").strip() or str(padrao)


def _mostrar_leituras(leituras: list[dict]) -> None:
    from src.fase7_sifsm import logica

    if not leituras:
        print("  (nenhum registro encontrado)")
        return
    print(f"  {'ID':>4} {'Data':<16} {'Módulo':<7} {'Consumo W':>10} {'Temp':>6} {'Umid':>6} "
          f"{'Bat%':>6} {'Status':<10} {'Risco':<9}")
    print("  " + "-" * 84)
    for l in leituras:
        risco = logica.classificar_risco(l, l["limite_consumo_w"], bool(l["essencial"]))
        temp = "-" if l["temperatura_c"] is None else f"{l['temperatura_c']:.1f}"
        umid = "-" if l["umidade_pct"] is None else f"{l['umidade_pct']:.1f}"
        bat = "-" if l["carga_bateria_pct"] is None else f"{l['carga_bateria_pct']:.1f}"
        print(f"  {l['id']:>4} {l['data_registro']:<16} {l['modulo_id']:<7} {l['consumo_w']:>10.1f} "
              f"{temp:>6} {umid:>6} {bat:>6} {l['status_operacional']:<10} {risco:<9}")
    print(f"\n  {len(leituras)} registro(s).")


def opcao_cadastrar() -> None:
    """CREATE: pede os campos, grava no banco, avalia o risco e registra alerta se necessário."""
    from src.fase7_sifsm import banco, logica

    print("  Módulos disponíveis: " + ", ".join(m["id"] for m in banco.listar_modulos()))
    dados = {
        "modulo_id": _pedir("Módulo (ex.: MOD-01)"),
        "codigo_sensor": _pedir("Código do sensor (opcional, ex.: 0x1A)"),
        "consumo_w": _pedir("Consumo em W"),
        "temperatura_c": _pedir("Temperatura em °C (opcional)"),
        "umidade_pct": _pedir("Umidade em % (opcional)"),
        "carga_bateria_pct": _pedir("Carga da bateria em % (opcional)"),
        "status_operacional": _pedir("Status (ativo/alerta/falha/manutencao)", "ativo"),
        "data_registro": _pedir("Data AAAA-MM-DD HH:MM (Enter = agora)"),
    }
    novo_id = banco.cadastrar_leitura(dados)
    historico.empilhar({"acao": "cadastrar", "id": novo_id})
    leitura = banco.buscar_leitura(novo_id)
    risco = logica.classificar_risco(leitura, leitura["limite_consumo_w"], bool(leitura["essencial"]))
    print(f"\n  [OK] Leitura #{novo_id} cadastrada. Risco avaliado pela regra booleana: {risco.upper()}")
    if risco in ("alto", "bloqueado"):
        banco.registrar_alerta(
            leitura["modulo_id"], "regra_booleana", "critica" if risco == "alto" else "media",
            f"Risco {risco}: consumo {leitura['consumo_w']:.0f} W (limite {leitura['limite_consumo_w']:.0f} W)",
            leitura_id=novo_id)
        print("  [!] Alerta registrado no banco.")


def opcao_listar() -> None:
    """READ: lista leituras com filtro opcional por módulo e status."""
    from src.fase7_sifsm import banco

    modulo = _pedir("Filtrar por módulo (Enter = todos)")
    status = _pedir("Filtrar por status (Enter = todos)")
    limite = _pedir("Quantidade máxima de registros", "15")
    print()
    _mostrar_leituras(banco.listar_leituras(modulo or None, status or None, limite))


def opcao_alterar() -> None:
    """UPDATE: altera campos de uma leitura (Enter mantém o valor atual)."""
    from src.fase7_sifsm import banco

    id_leitura = _pedir("ID da leitura a alterar")
    atual = banco.buscar_leitura(id_leitura)
    if atual is None:
        print(f"\n  [!] Leitura #{id_leitura} não encontrada.")
        return
    print(f"  Atual: módulo {atual['modulo_id']}, consumo {atual['consumo_w']} W, "
          f"status {atual['status_operacional']}. (Enter mantém o valor atual)")
    campos = {}
    for campo, rotulo in (("consumo_w", "Novo consumo em W"), ("temperatura_c", "Nova temperatura"),
                          ("umidade_pct", "Nova umidade"), ("carga_bateria_pct", "Nova carga da bateria"),
                          ("status_operacional", "Novo status")):
        valor = _pedir(rotulo)
        if valor:
            campos[campo] = valor
    if not campos:
        print("\n  Nada a alterar.")
        return
    antes = {c: atual[c] for c in campos}
    if banco.alterar_leitura(atual["id"], campos):
        historico.empilhar({"acao": "alterar", "id": atual["id"], "antes": antes})
        print(f"\n  [OK] Leitura #{atual['id']} alterada.")


def opcao_excluir() -> None:
    """DELETE: pede confirmação e exclui."""
    from src.fase7_sifsm import banco

    id_leitura = _pedir("ID da leitura a excluir")
    registro = banco.buscar_leitura(id_leitura)
    if registro is None:
        print(f"\n  [!] Leitura #{id_leitura} não encontrada.")
        return
    print(f"  Leitura #{registro['id']}: {registro['modulo_id']} em {registro['data_registro']}, "
          f"{registro['consumo_w']} W.")
    if _pedir("Confirmar exclusão? (s/n)", "n").lower() != "s":
        print("\n  Exclusão cancelada.")
        return
    if banco.excluir_leitura(registro["id"]):
        historico.empilhar({"acao": "excluir", "id": registro["id"], "registro": registro})
        print(f"\n  [OK] Leitura #{registro['id']} excluída. (Use 'U' para desfazer.)")


def opcao_desfazer() -> None:
    """Desempilha a última ação do histórico e a reverte no banco."""
    from src.fase7_sifsm import banco

    acao = historico.desempilhar()
    if acao is None:
        print("  Nada para desfazer nesta sessão.")
        return
    if acao["acao"] == "cadastrar":
        banco.excluir_leitura(acao["id"])
        print(f"  [OK] Desfeito: cadastro da leitura #{acao['id']} removido.")
    elif acao["acao"] == "alterar":
        banco.alterar_leitura(acao["id"], acao["antes"])
        print(f"  [OK] Desfeito: leitura #{acao['id']} voltou aos valores anteriores.")
    elif acao["acao"] == "excluir":
        banco.restaurar_leitura(acao["registro"])
        print(f"  [OK] Desfeito: leitura #{acao['id']} restaurada.")


def opcao_regra_logica() -> None:
    from src.fase7_sifsm import logica

    logica.imprimir_tabela_verdade()


def opcao_circuito() -> None:
    from src.fase7_sifsm import apresentacao

    apresentacao.exibir_circuito_logico()


def opcao_estruturas() -> None:
    from src.fase7_sifsm import estruturas

    estruturas.demonstrar_estruturas(historico)


def opcao_simulacao() -> None:
    from src.fase7_sifsm import simulacao

    simulacao.executar_simulacao()


def opcao_modelo_linear() -> None:
    from src.fase7_sifsm import modelo_linear

    modelo_linear.executar_modelo_linear()


def opcao_assistente() -> None:
    from src.fase7_sifsm import agentes

    agentes.menu_assistente()


def opcao_arquitetura() -> None:
    from src.fase7_sifsm import apresentacao

    apresentacao.exibir_arquitetura()


def opcao_sustentabilidade() -> None:
    from src.fase7_sifsm import apresentacao

    apresentacao.exibir_sustentabilidade()


def opcao_analisar_colonia() -> None:
    """Fluxo integrado (exemplo do enunciado): consulta os registros no banco, classifica o
    risco com a regra booleana, organiza os alertas em estrutura de dados, roda a simulação,
    estima com a regressão e exibe a recomendação técnica + análise final.

    TODO (Integrante 2 monta, depois que o Integrante 1 entregar banco/lógica/estruturas):
        1. leituras = banco.listar_leituras()
        2. risco por módulo   = logica.classificar_risco(...)
        3. alertas na estrutura (HeapAlertas/Fila) -> mostrar do mais crítico ao menos
        4. simulacao.executar_simulacao()
        5. modelo_linear.executar_modelo_linear() -> previsão
        6. apresentacao.exibir_analise_final(resultados)
    """
    raise NotImplementedError("Integrantes 1 e 2: implementar opcao_analisar_colonia()")


OPCOES = {
    "1": ("Cadastrar leitura", opcao_cadastrar),
    "2": ("Listar registros", opcao_listar),
    "3": ("Alterar registro", opcao_alterar),
    "4": ("Excluir registro", opcao_excluir),
    "5": ("Regra booleana e tabela-verdade", opcao_regra_logica),
    "6": ("Circuito lógico / Tinkercad", opcao_circuito),
    "7": ("Estruturas de dados (fila, pilha, hash)", opcao_estruturas),
    "8": ("Simulação computacional (consumo e bateria)", opcao_simulacao),
    "9": ("Modelo linear de apoio à decisão", opcao_modelo_linear),
    "10": ("Assistente multiagente (IA)", opcao_assistente),
    "11": ("Arquitetura computacional", opcao_arquitetura),
    "12": ("Sustentabilidade e cidadania digital", opcao_sustentabilidade),
    "U": ("Desfazer última ação do CRUD (pilha de histórico)", opcao_desfazer),
    "A": ("ANALISAR SUSTENTABILIDADE DA COLÔNIA (fluxo completo)", opcao_analisar_colonia),
}


def preparar_banco() -> None:
    """Cria o banco e, na primeira execução, carrega o CSV e os chamados de exemplo.
    Uma falha aqui não impede o menu de abrir."""
    try:
        from src.fase7_sifsm import banco

        banco.inicializar_banco()
        if banco.contar_leituras() == 0:
            total = banco.carregar_csv_para_banco()
            banco.semear_chamados_exemplo()
            print(f"[Banco] {total} leituras carregadas de dados_aurora_siger.csv")
    except (OSError, sqlite3.Error, ErroBanco) as erro:
        print(f"[Aviso] Banco não inicializado: {erro}")


def menu_principal() -> None:
    preparar_banco()
    while True:
        exibir_cabecalho("SIFSM - FUTURO SUSTENTÁVEL EM MARTE (AURORA SIGER)")
        for chave, (rotulo, _) in OPCOES.items():
            print(f" [{chave:>2}] {rotulo}")
        print(" [ 0] Sair")
        print("=" * 70)

        escolha = input(" Selecione uma opção: ").strip().upper()
        if escolha == "0":
            print("\n>> Encerrando o SIFSM. Até logo!")
            break
        if escolha in OPCOES:
            exibir_cabecalho(OPCOES[escolha][0].upper())
            executar_opcao(OPCOES[escolha][1])
        else:
            print("\n[!] Opção inválida. Escolha uma das opções listadas.")
            pausar()


if __name__ == "__main__":
    menu_principal()
