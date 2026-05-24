# ==============================================================================
# PROJETO AURORA SIGER - ORQUESTRADOR CENTRAL E INTEGRAÇÃO DE SESSÕES COM IA
# ==============================================================================

import os
import json
from dotenv import load_dotenv
from google import genai

# Importação dos módulos independentes
from fase1 import executar_fase1
from fase2 import executar_fase2
from fase3 import executar_fase3

# Carrega as variáveis de ambiente
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Inicializa o cliente oficial da Google GenAI
client = genai.Client(api_key=api_key) if api_key else None


def rodar_simulacao_integrada():
    """
    Coordena o pipeline: Executa fases -> Consolida dados -> IA Analista -> IA Executiva.
    """
    print("=" * 85)
    print("INICIANDO SISTEMA INTEGRADO DA MISSÃO AURORA".center(85))
    print("=" * 85)

    # 1. Execução linear das fases (Cada fase cuida dos seus próprios logs no terminal)
    res_f1 = executar_fase1()
    res_f2 = executar_fase2()
    res_f3 = executar_fase3()

    # 2. Consolidando o pacote de dados único (Data Lake)
    contexto_operacional = {
        "Fase_1_Lancamento": res_f1,
        "Fase_2_Pouso": res_f2,
        "Fase_3_Colonia": res_f3,
    }

    # Conversão para JSON para o prompt da IA
    dados_json = json.dumps(contexto_operacional, indent=2, ensure_ascii=False)

    if not client:
        print("\n[!] Chave 'GEMINI_API_KEY' ausente. Encerrando sem IA.")
        return

    print("\n" + "=" * 85)
    print("PROCESSAMENTO DE DADOS E AUDITORIA (IA)".center(85))
    print("=" * 85)

    # --------------------------------------------------------------------------
    # REQUISIÇÃO IA 1: O "Analista de Dados" (Correlação Técnica)
    # --------------------------------------------------------------------------
    print(">> Extraindo correlações e gerando contexto analítico profundo...")
    prompt_contexto = (
        f"Você é um Engenheiro de Sistemas Aeroespaciais sênior. Analise os logs da missão:\n{dados_json}\n\n"
        f"Gere um relatório técnico correlacionando os eventos. Como as falhas de uma fase (se houver) "
        f"impactam o ecossistema das fases seguintes? Seja técnico, detalhista e profissional."
    )

    resposta_contexto = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt_contexto
    )

    # --------------------------------------------------------------------------
    # REQUISIÇÃO IA 2: O "Diretor de Voo" (Boletim Executivo Formal)
    # --------------------------------------------------------------------------
    print(">> Sintetizando Boletim Executivo Estruturado...\n")
    prompt_executivo = (
        f"Com base na análise técnica:\n'{resposta_contexto.text}'\n\n"
        f"Atue como Diretor de Voo. Escreva um boletim operacional estritamente no layout abaixo:\n\n"
        f"INICIANDO FASE 1: TELEMETRIA E PRÉ-DESCOLAGEM\n"
        f"-> [Análise detalhada fase 1]\n\n"
        f"INICIANDO FASE 2: APROXIMAÇÃO E POUSO (MGPEB)\n"
        f"-> [Análise detalhada fase 2]\n\n"
        f"INICIANDO FASE 3: SISTEMA INTELIGENTE DA COLÓNIA\n"
        f"-> [Análise detalhada fase 3]\n\n"
        f"Restrições: Use as setas '->', tom formal, técnico e no máximo 5 linhas por fase."
    )

    resposta_executiva = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt_executivo
    )

    print("--- BOLETIM DO DIRETOR DE VOO ---")
    print(resposta_executiva.text)
    print("=" * 85)


if __name__ == "__main__":
    rodar_simulacao_integrada()
