"""
Orquestrador da Fase 6 — SCIC (Missão Aurora Siger)
Integração final (Analista 3)

Fluxo completo em um menu interativo de terminal:
    carregar/gerar dados (Analista 1) -> treinar modelo e métricas (Analista 2)
    -> fila de alertas críticos com Heap -> consultas por prefixo com Trie (Analista 3)

Execução (na raiz do projeto):
    python -m src.fase6_scic.fase6_scic            # menu interativo
    python -m src.fase6_scic.fase6_scic --auto     # roda o pipeline completo sem menu

O menu da Fase 6 do main.py também reaproveita as telas deste arquivo.
"""

import os
import sys

from .dados import (
    calcular_indicadores,
    gerar_dataset_telemetria,
    imprimir_resumo_terminal,
    salvar_telemetria_csv,
)
from .hardware import decodificar_registrador_telemetria, diagnosticar_circuito
from .modelagem import executar_fase6_analista2
from .estruturas import (
    Alerta,
    HeapAlertas,
    comparar_heap_vs_lista,
    construir_trie,
    executar_fase6_analista3,
    imprimir_alerta_detalhado,
    imprimir_busca,
)

# Estado compartilhado entre as telas (evita recalcular tudo a cada opção)
estado = {"df": None, "ml": None, "heap": None, "trie": None, "atendidos": []}


# =====================================================================
# UTILITÁRIOS DE TELA
# =====================================================================
def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\n[Pressione Enter para continuar...]")


def cabecalho(titulo):
    limpar_tela()
    print("=" * 80)
    print(titulo.center(80))
    print("=" * 80)


# =====================================================================
# ETAPAS DO PIPELINE
# =====================================================================
def etapa_dados(exibir=True):
    """Analista 1: gera, valida e salva a base de telemetria."""
    df = gerar_dataset_telemetria()
    caminho = salvar_telemetria_csv(df)
    estado["df"] = df
    if exibir:
        imprimir_resumo_terminal(df, caminho)
    return df


def etapa_modelo(exibir=True):
    """Analista 2: regressão, métricas, gráficos e CSV com previsões."""
    if estado["df"] is None:
        etapa_dados(exibir=False)
    estado["ml"] = executar_fase6_analista2(estado["df"], exibir=exibir)
    # Base mudou -> estruturas precisam ser reconstruídas
    estado["heap"] = estado["trie"] = None
    return estado["ml"]


def etapa_estruturas():
    """Analista 3: monta o Heap de alertas e a Trie de módulos."""
    if estado["ml"] is None:
        etapa_modelo(exibir=False)
    df_prev = estado["ml"]["df_previsoes"]
    estado["heap"] = HeapAlertas()
    estado["heap"].carregar_de_dataframe(df_prev)
    estado["trie"] = construir_trie(df_prev)
    estado["atendidos"] = []


def garantir_estruturas():
    if estado["heap"] is None or estado["trie"] is None:
        print(">> Preparando base, modelo e estruturas (primeira execução)...")
        etapa_estruturas()


def pipeline_completo():
    """Executa todas as etapas em sequência, exibindo cada resultado."""
    cabecalho("PIPELINE COMPLETO DO SCIC")
    print("\n>>> ETAPA 1/3 — DADOS E TELEMETRIA (Analista 1)")
    etapa_dados(exibir=True)
    print("\n>>> ETAPA 2/3 — MODELAGEM E MÉTRICAS (Analista 2)")
    etapa_modelo(exibir=True)
    print("\n>>> ETAPA 3/3 — HEAP DE ALERTAS E TRIE (Analista 3)")
    resultado = executar_fase6_analista3(estado["ml"]["df_previsoes"], exibir=True)
    estado["heap"], estado["trie"], estado["atendidos"] = resultado["heap"], resultado["trie"], []
    return resultado


# =====================================================================
# TELAS INTERATIVAS
# =====================================================================
def menu_heap():
    """Central de alertas: consulta, atendimento e inserção manual (Heap)."""
    garantir_estruturas()
    heap = estado["heap"]
    while True:
        cabecalho("CENTRAL DE ALERTAS CRÍTICOS — HEAP (FILA DE PRIORIDADE)")
        print(f"Alertas pendentes: {len(heap)} | atendidos nesta sessão: {len(estado['atendidos'])}")
        topo = heap.espiar()
        if topo:
            print(f"Próximo a atender (O(1)): {topo.nome_modulo} — {topo.mensagem} "
                  f"[criticidade {topo.criticidade}]")
        print("\n[1] Ver os N alertas mais críticos (sem remover)")
        print("[2] Atender o alerta mais crítico (extrair — O(log n))")
        print("[3] Registrar novo alerta manual (inserir — O(log n))")
        print("[4] Histórico de alertas atendidos")
        print("[0] Voltar")
        op = input("\nEscolha uma opção: ").strip()

        if op == "1":
            try:
                n = int(input("Quantos alertas exibir? [5]: ") or 5)
            except ValueError:
                n = 5
            print()
            for i, alerta in enumerate(heap.top_n(n), 1):
                imprimir_alerta_detalhado(alerta, i)
            pausar()
        elif op == "2":
            if heap.esta_vazio():
                print("\nNenhum alerta pendente. Colônia estável.")
            else:
                alerta = heap.extrair_mais_critico()
                estado["atendidos"].append(alerta)
                print("\n>> ALERTA ENCAMINHADO À EQUIPE DE OPERAÇÃO:")
                imprimir_alerta_detalhado(alerta)
                print("\n   Decisão final: operador humano (o sistema apenas prioriza).")
            pausar()
        elif op == "3":
            registrar_alerta_manual(heap)
            pausar()
        elif op == "4":
            print()
            if not estado["atendidos"]:
                print("Nenhum alerta atendido ainda.")
            for i, alerta in enumerate(estado["atendidos"], 1):
                print(f"{i:>2}. {alerta.resumo()}")
            pausar()
        elif op == "0":
            break


def registrar_alerta_manual(heap):
    """Permite ao operador inserir um alerta reportado manualmente."""
    trie = estado["trie"]
    prefixo = input("\nMódulo (digite um prefixo, ex.: 'sup', 'mod-05', '0x5'): ").strip()
    candidatos = [
        (r, d) for r, d in trie.buscar_prefixo(prefixo).items()
        if d.get("categoria") in ("módulo", "sensor")
    ]
    if not candidatos:
        print("Nenhum módulo encontrado para esse prefixo.")
        return
    for i, (rotulo, _) in enumerate(candidatos, 1):
        print(f"  [{i}] {rotulo}")
    try:
        escolha = int(input("Escolha: ") or 1) - 1
        _, dados = candidatos[escolha]
        mensagens = [
            "Sobrecarga de potência no barramento",
            "Radiação elevada no módulo",
            "Latência acima do previsto",
        ]
        for i, m in enumerate(mensagens, 1):
            print(f"  [{i}] {m}")
        mensagem = mensagens[int(input("Tipo de alerta: ") or 1) - 1]
        prioridade = int(input("Prioridade (1 a 4) [4]: ") or 4)
    except (ValueError, IndexError):
        print("Entrada inválida. Alerta não registrado.")
        return

    registro = {
        "timestamp_id": 0,
        "ciclo": 0,
        "modulo_id": dados["modulo_id"],
        "nome_modulo": dados["nome_modulo"],
        "codigo_sensor_hex": dados.get("codigo", dados["sensores"][0]),
        "essencial": int(dados["essencial"]),
        "status_operacional": "alerta",
        "prioridade": max(1, min(prioridade, 4)),
        "mensagem_alerta": mensagem,
    }
    heap.inserir(registro)
    print(f"\n>> Alerta inserido. Fila agora com {len(heap)} alertas.")
    print(f"   Topo atual: {heap.espiar().resumo()}")


def menu_trie():
    """Busca interativa por prefixo (módulos, sensores hex e comandos)."""
    garantir_estruturas()
    trie = estado["trie"]
    cabecalho("BUSCA POR PREFIXO — TRIE")
    print(f"Chaves indexadas: {len(trie)} (nomes, palavras, IDs, tipos, códigos hex, comandos)")
    print("Exemplos: 'com', 'central', 'mod-0', '0x2', 'oxi', 'al'. Enter vazio para voltar.")
    while True:
        prefixo = input("\nPrefixo> ").strip()
        if not prefixo:
            break
        if not imprimir_busca(trie, prefixo):
            print("  Nenhum resultado. Dica: a busca ignora acentos e maiúsculas.")


def menu_benchmark():
    cabecalho("BENCHMARK — HEAP x LISTA COMUM")
    print("Inserindo n alertas e extraindo todos em ordem de criticidade...\n")
    print(f"{'n':>8} | {'lista (ms)':>12} | {'heap (ms)':>10} | ganho")
    for r in comparar_heap_vs_lista():
        print(f"{r['n']:>8} | {r['lista_ms']:>12.2f} | {r['heap_ms']:>10.2f} | {r['ganho_x']}x")
    print("\nLista comum: cada extração varre a lista inteira -> O(n), total O(n²).")
    print("Heap binário: inserção e extração O(log n), total O(n log n).")
    print("Para n pequeno a lista pode até empatar (constantes), mas o heap escala muito melhor.")
    pausar()


def menu_mapeamento_io():
    cabecalho("MAPEAMENTO DE INTERFACES DE I/O E PROTOCOLOS")
    mod_id = input("Digite o ID do módulo (ex: MOD-02) ou Enter para listar todos: ").strip()
    try:
        mapeamento = mapear_interfaces_io(mod_id if mod_id else None)
        for m_code, info in mapeamento.items():
            print(f"\n> [{m_code}] {info['modulo']}")
            print(f"  - Comunicação        : {info['interface_comunicacao']}")
            print(f"  - Interfaces I/O     : {info['sensores_io']}")
            print(f"  - Barramento Elétrico: {info['barramento_eletrico']}")
    except ValueError as e:
        print(f"[!] {e}")
    pausar()


def menu_decodificar_hex():
    cabecalho("DECODIFICAÇÃO DE REGISTRADOR HEXADECIMAL")
    codigo = input("Código de sensor hex para decodificar [0x2A]: ").strip() or "0x2A"
    try:
        r = decodificar_registrador_telemetria(codigo)
        print(f"\n  > Hexadecimal : {r['hex']}")
        print(f"  > Decimal     : {r['decimal']}")
        print(f"  > Binário     : {r['binario']}")
    except ValueError as e:
        print(f"[!] {e}")
    pausar()


def menu_principal_scic():
    while True:
        cabecalho("SCIC — SISTEMA COMPUTACIONAL INTEGRADO DA COLÔNIA AURORA SIGER")
        if estado["df"] is not None:
            ind = calcular_indicadores(estado["df"])
            print(f"Base carregada: {ind['total_registros']} registros | "
                  f"disponibilidade {ind['disponibilidade_%']}% | alertas {ind['taxa_alertas_%']}%")
        if estado["ml"] is not None:
            m = estado["ml"]["metricas"]
            print(f"Modelo ML: MAE {m['MAE']} | RMSE {m['RMSE']} | R² {m['R2']}")

        print("\n[1] Gerar e Persistir Dataset de Telemetria (CSV)")
        print("[2] Executar Diagnóstico de Circuito Elétrico (Lei de Ohm)")
        print("[3] Mapear Interfaces de I/O e Transmissão da Colônia")
        print("[4] Decodificar Registrador Hexadecimal")
        print("[5] Central de Alertas Críticos (Heap / Fila de Prioridade)")
        print("[6] Busca por Prefixo de Módulos e Sensores (Trie)")
        print("[7] Benchmark Heap x Lista Comum")
        print("[8] Executar Pipeline Completo do SCIC (dados -> modelo -> heap -> trie)")
        print("[0] Sair / Voltar")

        op = input("\nEscolha uma opção: ").strip()

        if op == "1":
            limpar_tela()
            etapa_dados(exibir=True)
            etapa_modelo(exibir=True)
            pausar()
        elif op == "2":
            limpar_tela()
            try:
                v = float(input("Tensão (V) [230]: ") or 230.0)
                i = float(input("Corrente (A) [28]: ") or 28.0)
                limite = float(input("Limite de potência (W) [6500]: ") or 6500.0)
                for k, val in diagnosticar_circuito(v, i, limite).items():
                    print(f"  > {k}: {val}")
            except (ValueError, ZeroDivisionError) as e:
                print(f"[!] {e}")
            pausar()
        elif op == "3":
            menu_mapeamento_io()
        elif op == "4":
            menu_decodificar_hex()
        elif op == "5":
            menu_heap()
        elif op == "6":
            menu_trie()
        elif op == "7":
            menu_benchmark()
        elif op == "8":
            pipeline_completo()
            pausar()
        elif op == "0":
            print(">> Encerrando o SCIC.")
            break


if __name__ == "__main__":
    if "--auto" in sys.argv:
        pipeline_completo()
    else:
        menu_principal_scic()
