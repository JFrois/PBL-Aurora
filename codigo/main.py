# ==============================================================================
# PROJETO AURORA SIGER - ORQUESTRADOR CENTRAL E INTEGRAÇÃO DE SESSÕES COM IA
# Versão atualizada com Fase 4: SIGIC (Sistema de Grafos da Colônia)
# ==============================================================================

import os
import json
from dotenv import load_dotenv

# Importação dos módulos independentes
from fase1 import executar_fase1
from fase2 import executar_fase2
from fase3 import executar_fase3
from fase4 import executar_fase4  

# Carrega as variáveis de ambiente
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Inicializa o cliente da Google GenAI apenas se a chave existir
try:
    from google import genai

    client = genai.Client(api_key=api_key) if api_key else None
except ImportError:
    client = None


def rodar_simulacao_integrada():
    """
    Pipeline completo da Missão Aurora Siger:
      F1 → F2 → F3 → F4 (SIGIC) → IA
    """
    print("=" * 85)
    print("INICIANDO SISTEMA INTEGRADO DA MISSÃO AURORA SIGER".center(85))
    print("=" * 85)

    # ------------------------------------------------------------------
    # FASES 1, 2 e 3 — inalteradas
    # ------------------------------------------------------------------
    res_f1 = executar_fase1()
    res_f2 = executar_fase2()
    res_f3 = executar_fase3()

    # ------------------------------------------------------------------
    # FASE 4 — SIGIC recebe os resultados anteriores como entrada
    # Os dados de res_f2 determinam quais módulos estão ativos no grafo.
    # Os dados de res_f3 determinam o status energético do armazenamento.
    # ------------------------------------------------------------------
    res_f4 = executar_fase4(res_f2, res_f3)

    # ------------------------------------------------------------------
    # Consolidação do Data Lake (todas as 4 fases)
    # ------------------------------------------------------------------
    contexto_operacional = {
        "Fase_1_Lancamento": res_f1,
        "Fase_2_Pouso": res_f2,
        "Fase_3_Colonia": res_f3,
        "Fase_4_SIGIC_Grafos": res_f4,  # ← NOVO BLOCO
    }

    dados_json = json.dumps(contexto_operacional, indent=2, ensure_ascii=False)

    if not client:
        print("\n[!] Chave 'GEMINI_API_KEY' ausente ou biblioteca indisponível.")
        print("[!] Pipeline concluído sem análise de IA.")
        return

    # ------------------------------------------------------------------
    # IA 1: Analista Técnico (correlação entre as 4 fases)
    # ------------------------------------------------------------------
    print("\n" + "=" * 85)
    print("PROCESSAMENTO DE DADOS E AUDITORIA (IA)".center(85))
    print("=" * 85)
    print(">> Extraindo correlações entre as 4 fases...")

    prompt_contexto = (
        f"Você é um Engenheiro de Sistemas Aeroespaciais sênior. "
        f"Analise os logs completos da missão (4 fases):\n{dados_json}\n\n"
        f"Gere um relatório técnico correlacionando os eventos. "
        f"Destaque especialmente como os resultados do pouso (Fase 2) impactaram "
        f"a topologia da rede de módulos (Fase 4 - SIGIC): quais módulos estão "
        f"operacionais, quais estão inativos e qual é o risco operacional resultante. "
        f"Seja técnico, detalhado e profissional."
    )

    resposta_contexto = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt_contexto
    )

    # ------------------------------------------------------------------
    # IA 2: Diretor de Voo (boletim executivo com as 4 fases)
    # ------------------------------------------------------------------
    print(">> Sintetizando Boletim Executivo (4 fases)...\n")

    prompt_executivo = (
        f"Com base na análise técnica:\n'{resposta_contexto.text}'\n\n"
        f"Atue como Diretor de Voo. Escreva um boletim operacional no layout:\n\n"
        f"FASE 1: TELEMETRIA E PRÉ-DECOLAGEM\n"
        f"-> [Análise]\n\n"
        f"FASE 2: APROXIMAÇÃO E POUSO (MGPEB)\n"
        f"-> [Análise]\n\n"
        f"FASE 3: SISTEMA INTELIGENTE DA COLÔNIA\n"
        f"-> [Análise]\n\n"
        f"FASE 4: SIGIC — REDE DE INFRAESTRUTURA\n"
        f"-> [Análise da topologia, módulos ativos/inativos e risco operacional]\n\n"
        f"Restrições: setas '->', tom formal/técnico, máximo 5 linhas por fase."
    )

    resposta_executiva = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt_executivo
    )

    print("--- BOLETIM DO DIRETOR DE VOO ---")
    print(resposta_executiva.text)
    print("=" * 85)


if __name__ == "__main__":
    rodar_simulacao_integrada()
