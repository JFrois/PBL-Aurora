# ==============================================================================
# PROJETO AURORA SIGER - ORQUESTRADOR CENTRAL E MÁQUINA DE ESTADOS
# Interface Interativa CLI, Sistema de Logs Operacionais e Análise Integrada com IA
# ==============================================================================
import json
import os
import time
from dotenv import load_dotenv

# Importação dos utilitários globais
from src.core.utils import exibir_cabecalho, limpar_tela, pausar

# Importação dos módulos das fases
import src.fases_anteriores.fase5 as fase5
from src.fase6_scic.dados import gerar_dataset_telemetria, salvar_telemetria_csv
from src.fase6_scic.hardware import (
    decodificar_registrador_telemetria,
    diagnosticar_circuito,
    mapear_interfaces_io,
)
from src.fase6_scic.modelagem import executar_fase6_analista2
from src.fases_anteriores.fase1 import executar_fase1
from src.fases_anteriores.fase2 import executar_fase2
from src.fases_anteriores.fase3 import executar_fase3
from src.fases_anteriores.fase4 import executar_fase4

# Importação da Fase 6 (Analista 3 — Heap, Trie e orquestrador do SCIC)
import src.fase6_scic.fase6_scic as scic

# ==============================================================================
# CONFIGURAÇÃO DE IA
# ==============================================================================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

try:
    from google import genai

    client = genai.Client(api_key=api_key) if api_key else None
except ImportError:
    client = None

# ==============================================================================
# ESTADO GLOBAL DO PROJETO (STATE MACHINE)
# ==============================================================================
estado_projeto = {
    1: {
        "status": "Não iniciada",
        "nome": "Telemetria e Pré-Decolagem",
        "resultado": None,
        "log_registro": "",
    },
    2: {
        "status": "Não iniciada",
        "nome": "Aproximação e Pouso (MGPEB)",
        "resultado": None,
        "log_registro": "",
    },
    3: {
        "status": "Não iniciada",
        "nome": "Sistema Inteligente da Colônia",
        "resultado": None,
        "log_registro": "",
    },
    4: {
        "status": "Não iniciada",
        "nome": "SIGIC — Rede de Infraestrutura",
        "resultado": None,
        "log_registro": "",
    },
    5: {
        "status": "Não iniciada",
        "nome": "NCAS — Núcleo Cognitivo",
        "resultado": None,
        "log_registro": "",
    },
    6: {
        "status": "Não iniciada",
        "nome": "SCIC — Sistema Computacional e Hardware",
        "resultado": None,
        "log_registro": "",
    },
}


# ==============================================================================
# FUNÇÕES DE INTERFACE (CLI) E VALIDAÇÃO
# ==============================================================================
def limpar_tela():
    """Limpa o terminal para criar a sensação de navegação em telas."""
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    """Pausa a execução até o usuário pressionar Enter."""
    input("\n[Pressione Enter para continuar...]")


def exibir_cabecalho(titulo):
    """Exibe um cabeçalho padronizado para as telas."""
    limpar_tela()
    print("=" * 70)
    print(titulo.center(70))
    print("=" * 70)


def verificar_dependencias(fases_necessarias):
    """Garante que o usuário não pule fases, quebrando a cronologia e os dados do sistema."""
    pendentes = [
        f for f in fases_necessarias if estado_projeto[f]["status"] != "Concluída"
    ]

    if pendentes:
        print("\n⚠️  AÇÃO BLOQUEADA: Dependências não atendidas.")
        print("Para executar esta fase, você precisa concluir primeiro:")
        for f in fases_necessarias:
            marcador = "✓" if estado_projeto[f]["status"] == "Concluída" else "✗"
            print(f"  {marcador} Fase {f}: {estado_projeto[f]['nome']}")
        pausar()
        return False
    return True


def obter_logs_acumulados(max_linhas=100):
    """Lê os últimos N registros do arquivo oficial de logs da colônia (registros_colonia.txt)."""
    caminho_log = os.path.join("data", "processed", "registros_colonia.txt")
    if not os.path.exists(caminho_log):
        return "Nenhum log operacional gravado até o momento."
    try:
        with open(caminho_log, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f.readlines() if l.strip()]
        return "\n".join(linhas[-max_linhas:]) if linhas else "Arquivo de logs vazio."
    except Exception as e:
        return f"Erro ao ler arquivo de registros de log: {e}"


# ==============================================================================
# ANÁLISE INTEGRADA COM IA (CONSULTA ÚNICA BASEADA NOS LOGS E DADOS)
# ==============================================================================
def gerar_resumo_final_ia():
    """
    Consolida os logs operacionais acumulados de todas as etapas executadas
    em uma ANÁLISE ÚNICA E COMPLETA via IA (Gemini ou Fallback Local).
    """
    exibir_cabecalho("ANÁLISE INTEGRADA DA MISSÃO COM IA (DIRETOR DE VOO)")

    fases_concluidas = [
        f for f in range(1, 7) if estado_projeto[f]["status"] == "Concluída"
    ]
    if not fases_concluidas:
        print("\n[!] Nenhuma fase foi concluída ainda.")
        print("    Execute pelo menos uma fase no Menu Principal para gerar a análise.")
        pausar()
        return

    logs = obter_logs_acumulados(max_linhas=80)

    # Coleta os resultados estruturados de cada fase concluída
    contexto_fases = {}
    for f in fases_concluidas:
        contexto_fases[f"Fase_{f}_{estado_projeto[f]['nome']}"] = (
            estado_projeto[f]["resultado"]
        )

    # Se a API da IA não estiver disponível, apresenta um relatório local baseado nos logs
    if not client:
        print("\n" + "-" * 70)
        print(" ⚠️  IA EM MODO OFFLINE / LOCAL (FALLBACK)".center(70))
        print("-" * 70)
        print(
            " Não foi possível conectar à API do Gemini. Exibindo diagnóstico"
        )
        print(" unificado local com base nos logs gerados pelas etapas:\n")

        print(
            f"📊 FASES EXECUTADAS COM SUCESSO: {len(fases_concluidas)} de 6"
        )
        for f in fases_concluidas:
            print(f"   ✓ Fase {f}: {estado_projeto[f]['nome']}")

        print("\n📋 ÚLTIMOS REGISTROS DO LOG DA COLÔNIA (registros_colonia.txt):")
        print("-" * 70)
        for linha_log in logs.split("\n")[-12:]:
            print(f"  {linha_log}")
        print("-" * 70)

        fase5.gravar_registro(
            "Análise integrada executiva exibida em modo local (Mock).",
            "SISTEMA",
        )
        pausar()
        return

    print("\n>> Conectando aos servidores da Google (Gemini)...")
    time.sleep(1)
    print(
        ">> Sintetizando o Boletim do Diretor de Voo com base nos logs gerados..."
    )

    prompt = (
        "Você é a IA Central (Diretor de Voo) da Missão Aurora Siger.\n"
        "O sistema operou gerando registros contínuos de log a cada etapa executada pelos engenheiros e analistas.\n\n"
        f"--- HISTÓRICO DE LOGS OFICIAIS (data/processed/registros_colonia.txt) ---\n{logs}\n\n"
        f"--- DADOS ESTRUTURADOS DAS FASES EXECUTADAS ---\n{json.dumps(contexto_fases, ensure_ascii=False, default=str)}\n\n"
        "Sua tarefa é realizar uma ANÁLISE ÚNICA, COMPLETA E UNIFICADA de toda a operação da colônia.\n"
        "Por favor, organize a resposta com a seguinte estrutura clara em Markdown:\n\n"
        "STATUS GERAL DA MISSÃO: [Diagnóstico direto de 1 a 2 linhas do estado da colônia]\n\n"
        "1. 📈 DIAGNÓSTICO CRONOLÓGICO INTEGRADO:\n"
        "   - Avalie a evolução da missão desde a pré-decolagem/telemetria, pouso orbital, balanço energético, topologia de rede SIGIC, regras cognitivas NCAS até o hardware e ML no SCIC.\n\n"
        "2. 🔗 CORRELAÇÕES E IMPACTOS ENTRE ETAPAS:\n"
        "   - Analise como as decisões e resultados de uma etapa impactaram as seguintes (ex: como os módulos que pousaram na F2 afetaram a demanda de energia na F3, as rotas da rede na F4, os alertas lógicos do NCAS na F5 e a latência/fila do Heap no SCIC F6).\n\n"
        "3. 🚨 TRIAGEM DE ALERTAS E RECOMENDAÇÕES OPERACIONAIS:\n"
        "   - Destaque gargalos ou riscos elétricos/latências e apresente recomendações práticas prioritárias para a tripulação.\n\n"
        "Seja profissional, técnico, conciso e bem estruturado."
    )

    try:
        resposta = client.models.generate_content(
            model=gemini_model, contents=prompt
        )
        print("\n" + "=" * 70)
        print(
            " BOLETIM DO DIRETOR DE VOO — ANÁLISE INTEGRADA VIA IA ".center(70)
        )
        print("=" * 70 + "\n")
        print(resposta.text)
        print("\n" + "=" * 70)

        fase5.gravar_registro(
            "Análise integrada unificada gerada pela IA com sucesso.",
            "IA_ANALISE",
        )
    except Exception as e:
        print(f"\n[❌ Erro na IA] Falha ao comunicar com a API: {e}")
        fase5.gravar_registro(f"Falha ao gerar Análise IA: {e}", "ERRO_IA")

    pausar()


# ==============================================================================
# MENUS ESPECÍFICOS DE CADA FASE
# ==============================================================================
def menu_fase1():
    while True:
        exibir_cabecalho("FASE 1 — TELEMETRIA E PRÉ-DECOLAGEM")
        print(f"Status atual: {estado_projeto[1]['status']}\n")
        print("[1] Executar Testes de Telemetria")
        print("[2] Ver Registros de Log da Fase (se concluída)")
        print("[0] Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            limpar_tela()
            resultado = executar_fase1()

            msg_log = (
                f"Fase 1 (Telemetria) executada. Telemetria nominal: {resultado.get('telemetria_ok', True)}. "
                f"Módulos pré-checados: {len(resultado.get('modulos', []))}."
            )
            fase5.gravar_registro(msg_log, "FASE_1")

            estado_projeto[1]["resultado"] = resultado
            estado_projeto[1]["log_registro"] = msg_log
            estado_projeto[1]["status"] = "Concluída"

            print("\n[✓] Fase 1 concluída com sucesso!")
            print(
                "    -> Registros de telemetria gravados em registros_colonia.txt."
            )
            print(
                "    -> Selecione [S] no Menu Principal para a Análise Integrada com IA."
            )
            pausar()
        elif op == "2":
            print(
                f"\nRegistros da Fase 1:\n{estado_projeto[1]['log_registro'] or 'Nenhum registro nesta sessão.'}"
            )
            pausar()
        elif op == "0":
            break


def menu_fase2():
    if not verificar_dependencias([1]):
        return

    while True:
        exibir_cabecalho("FASE 2 — APROXIMAÇÃO E POUSO")
        print(f"Status atual: {estado_projeto[2]['status']}\n")
        print("[1] Executar Protocolo de Pouso")
        print("[2] Ver Registros de Log da Fase (se concluída)")
        print("[0] Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            limpar_tela()
            resultado = executar_fase2(estado_projeto[1]["resultado"])

            pousados = (
                len(resultado.get("pousados", []))
                if isinstance(resultado, dict)
                else "N/A"
            )
            msg_log = (
                f"Fase 2 (Pouso Orbital - MGPEB) executada com sucesso. Módulos pousados: {pousados}. "
                f"Status: {resultado.get('status', 'OK') if isinstance(resultado, dict) else 'OK'}."
            )
            fase5.gravar_registro(msg_log, "FASE_2")

            estado_projeto[2]["resultado"] = resultado
            estado_projeto[2]["log_registro"] = msg_log
            estado_projeto[2]["status"] = "Concluída"

            print("\n[✓] Fase 2 concluída com sucesso!")
            print(
                "    -> Evento de pouso registrado em registros_colonia.txt."
            )
            print(
                "    -> Selecione [S] no Menu Principal para a Análise Integrada com IA."
            )
            pausar()
        elif op == "2":
            print(
                f"\nRegistros da Fase 2:\n{estado_projeto[2]['log_registro'] or 'Nenhum registro nesta sessão.'}"
            )
            pausar()
        elif op == "0":
            break


def menu_fase3():
    if not verificar_dependencias([1, 2]):
        return

    while True:
        exibir_cabecalho("FASE 3 — SISTEMA INTELIGENTE DA COLÔNIA")
        print(f"Status atual: {estado_projeto[3]['status']}\n")
        print("[1] Executar Diagnóstico Energético")
        print("[2] Ver Registros de Log da Fase (se concluída)")
        print("[0] Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            limpar_tela()
            resultado = executar_fase3(estado_projeto[2]["resultado"])

            consumo = (
                resultado.get("consumo_total_kw", "N/A")
                if isinstance(resultado, dict)
                else "N/A"
            )
            msg_log = f"Fase 3 (Diagnóstico Energético) executada. Consumo total calculado: {consumo} kW."
            fase5.gravar_registro(msg_log, "FASE_3")

            estado_projeto[3]["resultado"] = resultado
            estado_projeto[3]["log_registro"] = msg_log
            estado_projeto[3]["status"] = "Concluída"

            print("\n[✓] Fase 3 concluída com sucesso!")
            print(
                "    -> Balanço energético registrado em registros_colonia.txt."
            )
            print(
                "    -> Selecione [S] no Menu Principal para a Análise Integrada com IA."
            )
            pausar()
        elif op == "2":
            print(
                f"\nRegistros da Fase 3:\n{estado_projeto[3]['log_registro'] or 'Nenhum registro nesta sessão.'}"
            )
            pausar()
        elif op == "0":
            break


def menu_fase4():
    if not verificar_dependencias([2, 3]):
        return

    exibir_cabecalho("FASE 4 — SIGIC (REDE DE INFRAESTRUTURA)")
    print("Iniciando interface própria da Fase 4...\n")
    time.sleep(1)

    res_f2 = estado_projeto[2]["resultado"]
    res_f3 = estado_projeto[3]["resultado"]
    resultado = executar_fase4(res_f2, res_f3)

    msg_log = (
        "Fase 4 (SIGIC - Redes em Grafos) executada e inspecionada com sucesso."
    )
    fase5.gravar_registro(msg_log, "FASE_4")

    estado_projeto[4]["resultado"] = resultado
    estado_projeto[4]["log_registro"] = msg_log
    estado_projeto[4]["status"] = "Concluída"

    print("\n[✓] Fase 4 concluída com sucesso!")
    print(
        "    -> Mapeamento de infraestrutura em grafos registrado em registros_colonia.txt."
    )
    print(
        "    -> Selecione [S] no Menu Principal para a Análise Integrada com IA."
    )
    pausar()


def menu_fase5():
    if not verificar_dependencias([4]):
        return

    while True:
        exibir_cabecalho("FASE 5 — NÚCLEO COGNITIVO (NCAS)")
        print(f"Status atual: {estado_projeto[5]['status']}\n")
        print("[1] Executar Processamento em Lote (Pipeline Automático)")
        print("[2] Acessar Terminal Interativo do NCAS (Livre)")
        print("[3] Ver Registros de Log da Fase (se concluída)")
        print("[0] Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            limpar_tela()
            res_f2 = estado_projeto[2]["resultado"]
            res_f4 = estado_projeto[4]["resultado"]
            resultado = fase5.executar_fase5(client, res_f2, res_f4)

            msg_log = "Fase 5 (NCAS - Núcleo Cognitivo) executada. Regras lógicas de De Morgan aplicadas."
            fase5.gravar_registro(msg_log, "FASE_5")

            estado_projeto[5]["resultado"] = resultado
            estado_projeto[5]["log_registro"] = msg_log
            estado_projeto[5]["status"] = "Concluída"

            print("\n[✓] Fase 5 concluída com sucesso!")
            print(
                "    -> Regras lógicas e decisões cognitivas registradas em registros_colonia.txt."
            )
            print(
                "    -> Selecione [S] no Menu Principal para a Análise Integrada com IA."
            )
            pausar()
        elif op == "2":
            limpar_tela()
            fase5.main()
        elif op == "3":
            print(
                f"\nRegistros da Fase 5:\n{estado_projeto[5]['log_registro'] or 'Nenhum registro nesta sessão.'}"
            )
            pausar()
        elif op == "0":
            break


def menu_fase6():
    if not verificar_dependencias([1, 2, 3, 4, 5]):
        return
    while True:
        exibir_cabecalho("FASE 6 — SCIC (HARDWARE E DADOS)")
        print(f"Status atual: {estado_projeto[6]['status']}\n")
        print("[1] Gerar e Persistir Dataset de Telemetria (CSV)")
        print("[2] Executar Diagnóstico de Circuito Elétrico (Lei de Ohm)")
        print("[3] Mapear Interfaces de I/O e Transmissão da Colônia")
        print("[4] Decodificar Registrador Hexadecimal")
        print("[5] Central de Alertas Críticos (Heap / Fila de Prioridade)")
        print("[6] Busca por Prefixo de Módulos e Sensores (Trie)")
        print("[7] Benchmark Heap x Lista Comum")
        print(
            "[8] Executar Pipeline Completo do SCIC (dados -> modelo -> heap -> trie)"
        )
        print("[0] Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            limpar_tela()
            print(">> Gerando dataset sintético de telemetria marciana...")
            df = gerar_dataset_telemetria(amostras=120)
            caminho = salvar_telemetria_csv(df)
            print(f">> Dataset gerado e salvo com sucesso em:\n   {caminho}")

            print(
                "\n>> Treinando Modelo de Regressão Linear e Otimização..."
            )
            resultado_ml = executar_fase6_analista2(df, exibir=True)
            scic.estado.update(df=df, ml=resultado_ml, heap=None, trie=None)

            msg_log = (
                f"Fase 6 (SCIC - Telemetria e ML) executada. Dataset salvo em {caminho}. "
                f"Métricas ML: MAE={resultado_ml['metricas']['MAE']}, RMSE={resultado_ml['metricas']['RMSE']}, R2={resultado_ml['metricas']['R2']}."
            )
            fase5.gravar_registro(msg_log, "FASE_6")

            estado_projeto[6]["resultado"] = resultado_ml
            estado_projeto[6]["log_registro"] = msg_log
            estado_projeto[6]["status"] = "Concluída"

            print(
                "\n[✓] Fase 6 (Telemetria e Modelagem) concluída com sucesso!"
            )
            print(
                "    -> Métricas de ML e telemetria gravadas em registros_colonia.txt."
            )
            print(
                "    -> Selecione [S] no Menu Principal para a Análise Integrada com IA."
            )
            pausar()

        elif op == "2":
            limpar_tela()
            print("--- DIAGNÓSTICO DE HARDWARE ---")
            try:
                v = float(input("Tensão (V) [ex: 220]: ") or 220.0)
                i = float(input("Corrente (A) [ex: 12.5]: ") or 12.5)
                limite = float(
                    input("Limite Térmico de Potência (W) [ex: 3000]: ")
                    or 3000.0
                )
                res = diagnosticar_circuito(v, i, limite)
                print(f"\nResultado da Análise:")
                for k, val in res.items():
                    print(f"  > {k}: {val}")
                fase5.gravar_registro(
                    f"Diagnóstico elétrico executado: V={v}V, I={i}A, P={res['potencia_w']}W ({res['status']}).",
                    "HARDWARE",
                )
            except ValueError as e:
                print(f"[!] Erro nos valores informados: {e}")
            pausar()
        elif op == "3":
            limpar_tela()
            print("--- MAPEAMENTO DE INTERFACES DE I/O E PROTOCOLOS ---")
            mod_id = input(
                "Digite o ID do módulo (ex: MOD-02) ou Enter para listar todos: "
            ).strip()
            try:
                mapeamento = mapear_interfaces_io(mod_id if mod_id else None)
                for m_code, info in mapeamento.items():
                    print(f"\n> [{m_code}] {info['modulo']}")
                    print(
                        f"  - Comunicação        : {info['interface_comunicacao']}"
                    )
                    print(f"  - Interfaces I/O     : {info['sensores_io']}")
                    print(
                        f"  - Barramento Elétrico: {info['barramento_eletrico']}"
                    )
            except ValueError as e:
                print(f"[!] {e}")
            pausar()
        elif op == "4":
            limpar_tela()
            hex_input = input(
                "Digite o valor do registrador em Hex (ex: 0x2A ou FF): "
            ).strip()
            try:
                res = decodificar_registrador_telemetria(hex_input)
                print(f"\nDecodificação de Registrador:")
                print(f"  > Hexadecimal : {res['hex']}")
                print(f"  > Decimal     : {res['decimal']}")
                print(f"  > Binário     : {res['binario']}")
            except Exception as e:
                print(f"[!] Erro ao decodificar: {e}")
            pausar()
        elif op == "5":
            scic.menu_heap()
        elif op == "6":
            scic.menu_trie()
        elif op == "7":
            scic.menu_benchmark()
        elif op == "8":
            res_estruturas = scic.pipeline_completo()
            resultado_ml = scic.estado["ml"]

            msg_log = (
                f"Fase 6 (SCIC - Pipeline Completo) executada. Alertas no Heap: {res_estruturas.get('alertas_na_fila', 0)}, "
                f"Chaves na Trie: {res_estruturas.get('chaves_trie', 0)}. Métricas ML: MAE={resultado_ml['metricas']['MAE']}, RMSE={resultado_ml['metricas']['RMSE']}, R2={resultado_ml['metricas']['R2']}."
            )
            fase5.gravar_registro(msg_log, "FASE_6")

            estado_projeto[6]["resultado"] = resultado_ml
            estado_projeto[6]["log_registro"] = msg_log
            estado_projeto[6]["status"] = "Concluída"

            print("\n[✓] Pipeline Completo da Fase 6 concluído com sucesso!")
            print(
                "    -> Dados, regressão, Heap e Trie registrados em registros_colonia.txt."
            )
            print(
                "    -> Selecione [S] no Menu Principal para a Análise Integrada com IA."
            )
            pausar()
        elif op == "0":
            break


# ==============================================================================
# MENU PRINCIPAL (ORQUESTRADOR)
# ==============================================================================
def menu_principal():
    fase5.gravar_registro(
        "Project Validation System (PVS) - Orquestrador Iniciado", "SISTEMA"
    )

    while True:
        limpar_tela()
        print("============================================================")
        print("          PROJECT VALIDATION SYSTEM - AURORA SIGER          ")
        print("============================================================")

        for i in range(1, 7):
            status = estado_projeto[i]["status"]
            simbolo = (
                "✅"
                if status == "Concluída"
                else ("⏳" if status == "Em andamento" else "⭕")
            )
            print(f" [{i}] Fase {i} — {estado_projeto[i]['nome']}")
            print(f"     Status: {simbolo} {status}\n")

        print("------------------------------------------------------------")
        print(" [S] Análise Integrada da Missão com IA (Diretor de Voo)")
        print(" [X] Sair do Sistema")
        print("============================================================")

        op = input(" Selecione uma opção: ").strip().upper()

        if op == "1":
            if estado_projeto[1]["status"] != "Concluída":
                estado_projeto[1]["status"] = "Em andamento"
            menu_fase1()
        elif op == "2":
            if estado_projeto[2]["status"] != "Concluída":
                estado_projeto[2]["status"] = "Em andamento"
            menu_fase2()
        elif op == "3":
            if estado_projeto[3]["status"] != "Concluída":
                estado_projeto[3]["status"] = "Em andamento"
            menu_fase3()
        elif op == "4":
            if estado_projeto[4]["status"] != "Concluída":
                estado_projeto[4]["status"] = "Em andamento"
            menu_fase4()
        elif op == "5":
            if estado_projeto[5]["status"] != "Concluída":
                estado_projeto[5]["status"] = "Em andamento"
            menu_fase5()
        elif op == "6":
            if estado_projeto[6]["status"] != "Concluída":
                estado_projeto[6]["status"] = "Em andamento"
            menu_fase6()
        elif op == "S":
            gerar_resumo_final_ia()
        elif op == "X":
            limpar_tela()
            fase5.gravar_registro(
                "Project Validation System (PVS) - Orquestrador Encerrado",
                "SISTEMA",
            )
            print(">> Encerrando o Project Validation System. Até logo!")
            break
        else:
            print("\n[!] Opção inválida!")
            time.sleep(1)


if __name__ == "__main__":
    menu_principal()
