# ==============================================================================
# PROJETO AURORA SIGER - ORQUESTRADOR CENTRAL E MÁQUINA DE ESTADOS
# Interface Interativa CLI, Log Global e Sumarização via IA
# ==============================================================================

import os
import json
import time
from dotenv import load_dotenv

# Importação dos módulos das fases
from fase1 import executar_fase1
from fase2 import executar_fase2
from fase3 import executar_fase3
from fase4 import executar_fase4
import codigo_fonte as fase5  # Importa o módulo da Fase 5 (NCAS) e as funções de log

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
        "resumo_ia": "",
    },
    2: {
        "status": "Não iniciada",
        "nome": "Aproximação e Pouso (MGPEB)",
        "resultado": None,
        "resumo_ia": "",
    },
    3: {
        "status": "Não iniciada",
        "nome": "Sistema Inteligente da Colônia",
        "resultado": None,
        "resumo_ia": "",
    },
    4: {
        "status": "Não iniciada",
        "nome": "SIGIC — Rede de Infraestrutura",
        "resultado": None,
        "resumo_ia": "",
    },
    5: {
        "status": "Não iniciada",
        "nome": "NCAS — Núcleo Cognitivo",
        "resultado": None,
        "resumo_ia": "",
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


# ==============================================================================
# INTEGRAÇÃO COM IA (SUMARIZAÇÃO) E LOGS
# ==============================================================================
def gerar_resumo_fase_ia(fase_num, dados):
    """Gera um resumo dinâmico da fase executada utilizando o Gemini."""
    if not client:
        return f"[Mock local] Fase {fase_num} concluída com sucesso. Dados gravados."

    print("\n[IA] Sincronizando dados com o servidor para resumo...")
    time.sleep(1)  # Efeito visual de carregamento

    prompt = (
        f"Você é a IA da Aurora Siger. A Fase {fase_num} ({estado_projeto[fase_num]['nome']}) "
        f"acabou de ser executada e gerou os seguintes dados brutos: {json.dumps(dados, ensure_ascii=False)}.\n"
        "Faça um resumo executivo muito curto e direto (máximo de 3 bullet points) sobre o que aconteceu "
        "e qual foi o resultado final desta fase. Não use formatação exagerada."
    )
    try:
        resposta = client.models.generate_content(
            model=gemini_model, contents=prompt
        )
        return resposta.text.strip()
    except Exception as e:
        return f"[Erro IA] Não foi possível gerar resumo: {e}"


def gerar_resumo_final_ia():
    """Consolida os resumos de todas as fases em um relatório executivo final."""
    exibir_cabecalho("RESUMO FINAL DO PROJETO COM IA")

    # Verifica se pelo menos alguma fase foi feita
    fases_concluidas = [
        f for f in range(1, 6) if estado_projeto[f]["status"] == "Concluída"
    ]
    if not fases_concluidas:
        print("\n[!] Nenhuma fase foi concluída ainda.")
        print(
            "    Execute pelo menos uma fase no Menu Principal para gerar o relatório."
        )
        pausar()
        return

    contexto = {
        f"Resumo_Fase_{i}": estado_projeto[i]["resumo_ia"] for i in fases_concluidas
    }

    # Se a IA estiver desativada, exibe uma tela clara de fallback
    if not client:
        print("\n" + "-" * 70)
        print(" ⚠️  IA DESATIVADA OU BIBLIOTECA NÃO ENCONTRADA".center(70))
        print("-" * 70)
        print(" Não foi possível conectar à API do Gemini. O sistema gerou um")
        print(" relatório local (Mock) com base nas fases concluídas:\n")
        for fase in fases_concluidas:
            print(f"   -> Fase {fase} ({estado_projeto[fase]['nome']}): Concluída.")

        fase5.gravar_registro("Resumo final (Mock local) exibido.", "SISTEMA")
        pausar()
        return

    # Interface de carregamento para a IA
    print("\n>> Conectando aos servidores da Google (Gemini)...")
    time.sleep(1)
    print(">> Sintetizando o Boletim Executivo. Por favor, aguarde...\n")

    prompt = (
        f"Com base nos resumos individuais de cada fase concluída da Missão Aurora Siger: {json.dumps(contexto, ensure_ascii=False)}\n"
        "Atue como Diretor de Voo e escreva o Boletim Operacional Final. "
        "Use o seguinte layout:\n"
        "STATUS GERAL: [Resumo de 1 linha]\n\n"
        "PRINCIPAIS RESULTADOS:\n[Bullet points com as conclusões técnicas, focando na topologia da rede, energia e alertas].\n\n"
        "Seja extremamente profissional, técnico e conciso."
    )

    try:
        resposta = client.models.generate_content(
            model=gemini_model, contents=prompt
        )
        print("-" * 70)
        print(" BOLETIM DO DIRETOR DE VOO ".center(70))
        print("-" * 70)
        print(resposta.text)
        print("-" * 70)

        # Loga a geração bem-sucedida do relatório final
        fase5.gravar_registro(
            "Boletim Executivo Final gerado pela IA com sucesso.", "IA_RELATORIO"
        )
    except Exception as e:
        print(f"\n[❌ Erro na IA] Falha ao comunicar com a API: {e}")
        fase5.gravar_registro(f"Falha ao gerar Boletim IA: {e}", "ERRO_IA")

    pausar()


# ==============================================================================
# MENUS ESPECÍFICOS DE CADA FASE
# ==============================================================================
def menu_fase1():
    while True:
        exibir_cabecalho("FASE 1 — TELEMETRIA E PRÉ-DECOLAGEM")
        print(f"Status atual: {estado_projeto[1]['status']}\n")
        print("[1] Executar Testes de Telemetria")
        print("[2] Ver Resumo da Fase (se concluída)")
        print("[0] Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            limpar_tela()
            resultado = executar_fase1()
            resumo = gerar_resumo_fase_ia(1, resultado)

            estado_projeto[1]["resultado"] = resultado
            estado_projeto[1]["resumo_ia"] = resumo
            estado_projeto[1]["status"] = "Concluída"

            fase5.gravar_registro(
                "Fase 1 (Telemetria) executada com sucesso.", "FASE_1"
            )

            print(f"\n--- RESUMO GERADO PELA IA ---\n{resumo}")
            pausar()
        elif op == "2":
            print(
                f"\nResumo da Fase 1:\n{estado_projeto[1]['resumo_ia'] or 'Nenhum resumo disponível.'}"
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
        print("[2] Ver Resumo da Fase (se concluída)")
        print("[0] Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            limpar_tela()
            # Passa o resultado da Fase 1 para a Fase 2 (Pipeline de dados)
            resultado = executar_fase2(estado_projeto[1]["resultado"])
            resumo = gerar_resumo_fase_ia(2, resultado)

            estado_projeto[2]["resultado"] = resultado
            estado_projeto[2]["resumo_ia"] = resumo
            estado_projeto[2]["status"] = "Concluída"

            fase5.gravar_registro(
                "Fase 2 (Pouso Orbital) executada com sucesso.", "FASE_2"
            )

            print(f"\n--- RESUMO GERADO PELA IA ---\n{resumo}")
            pausar()
        elif op == "2":
            print(
                f"\nResumo da Fase 2:\n{estado_projeto[2]['resumo_ia'] or 'Nenhum resumo disponível.'}"
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
        print("[2] Ver Resumo da Fase (se concluída)")
        print("[0] Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            limpar_tela()
            # Passa o resultado da Fase 2 para a Fase 3 calcular o consumo apenas de quem pousou
            resultado = executar_fase3(estado_projeto[2]["resultado"])
            resumo = gerar_resumo_fase_ia(3, resultado)

            estado_projeto[3]["resultado"] = resultado
            estado_projeto[3]["resumo_ia"] = resumo
            estado_projeto[3]["status"] = "Concluída"

            fase5.gravar_registro(
                "Fase 3 (Diagnóstico Energético) executada com sucesso.", "FASE_3"
            )

            print(f"\n--- RESUMO GERADO PELA IA ---\n{resumo}")
            pausar()
        elif op == "2":
            print(
                f"\nResumo da Fase 3:\n{estado_projeto[3]['resumo_ia'] or 'Nenhum resumo disponível.'}"
            )
            pausar()
        elif op == "0":
            break


def menu_fase4():
    # Fase 4 DEPENDE dos resultados reais das fases 2 e 3 para montar a Rede
    if not verificar_dependencias([2, 3]):
        return

    exibir_cabecalho("FASE 4 — SIGIC (REDE DE INFRAESTRUTURA)")
    print("Iniciando interface própria da Fase 4...\n")
    time.sleep(1)

    # Executa a Fase 4 passando os contextos necessários (o loop de menu ocorre lá dentro)
    res_f2 = estado_projeto[2]["resultado"]
    res_f3 = estado_projeto[3]["resultado"]
    resultado = executar_fase4(res_f2, res_f3)

    # Ao sair do menu da Fase 4 (usuário digita 0 lá), cai aqui
    resumo = gerar_resumo_fase_ia(4, resultado)
    estado_projeto[4]["resultado"] = resultado
    estado_projeto[4]["resumo_ia"] = resumo
    estado_projeto[4]["status"] = "Concluída"

    fase5.gravar_registro("Fase 4 (SIGIC - Grafos) inspecionada e concluída.", "FASE_4")

    print(f"\n--- RESUMO DA FASE 4 (GERADO PELA IA) ---\n{resumo}")
    pausar()


def menu_fase5():
    if not verificar_dependencias([4]):
        return

    while True:
        exibir_cabecalho("FASE 5 — NÚCLEO COGNITIVO (NCAS)")
        print(f"Status atual: {estado_projeto[5]['status']}\n")
        print("[1] Executar Processamento em Lote (Pipeline Automático)")
        print("[2] Acessar Terminal Interativo do NCAS (Livre)")
        print("[3] Ver Resumo da Fase (se concluída)")
        print("[0] Voltar ao Menu Principal")

        op = input("\nEscolha uma opção: ").strip()
        if op == "1":
            limpar_tela()
            # Chama a função não-interativa do codigo_fonte.py, passando F2 e F4 para o JSON
            res_f2 = estado_projeto[2]["resultado"]
            res_f4 = estado_projeto[4]["resultado"]
            resultado = fase5.executar_fase5(client, res_f2, res_f4)

            resumo = gerar_resumo_fase_ia(5, resultado)

            estado_projeto[5]["resultado"] = resultado
            estado_projeto[5]["resumo_ia"] = resumo
            estado_projeto[5]["status"] = "Concluída"

            fase5.gravar_registro(
                "Fase 5 (Pipeline Automático do NCAS) executada com sucesso.", "FASE_5"
            )

            print(f"\n--- RESUMO GERADO PELA IA ---\n{resumo}")
            pausar()
        elif op == "2":
            limpar_tela()
            # O próprio menu da Fase 5 já faz o log de entrada e saída
            fase5.main()
        elif op == "3":
            print(
                f"\nResumo da Fase 5:\n{estado_projeto[5]['resumo_ia'] or 'Nenhum resumo disponível.'}"
            )
            pausar()
        elif op == "0":
            break


# ==============================================================================
# MENU PRINCIPAL (ORQUESTRADOR)
# ==============================================================================
def menu_principal():
    # Loga o início da execução global
    fase5.gravar_registro(
        "Project Validation System (PVS) - Orquestrador Iniciado", "SISTEMA"
    )

    while True:
        limpar_tela()
        print("============================================================")
        print("          PROJECT VALIDATION SYSTEM - AURORA SIGER          ")
        print("============================================================")

        # Desenha os status de forma visual
        for i in range(1, 6):
            status = estado_projeto[i]["status"]
            if status == "Concluída":
                simbolo = "✓"
            elif status == "Em andamento":
                simbolo = "→"
            else:
                simbolo = "○"

            print(f" [{i}] Fase {i} — {estado_projeto[i]['nome']}")
            print(f"     Status: {simbolo} {status}\n")

        print("------------------------------------------------------------")
        print(" [S] Gerar Resumo Executivo Final (IA)")
        print(" [X] Sair do Sistema")
        print("============================================================")

        op = input(" Selecione uma opção: ").strip().upper()

        if op == "1":
            estado_projeto[1]["status"] = (
                "Em andamento"
                if estado_projeto[1]["status"] != "Concluída"
                else "Concluída"
            )
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
        elif op == "S":
            gerar_resumo_final_ia()
        elif op == "X":
            limpar_tela()
            # Loga o fim da execução global
            fase5.gravar_registro(
                "Project Validation System (PVS) - Orquestrador Encerrado", "SISTEMA"
            )
            print(">> Encerrando o Project Validation System. Até logo!")
            break
        else:
            print("\n[!] Opção inválida!")
            time.sleep(1)


if __name__ == "__main__":
    menu_principal()
