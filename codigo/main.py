# ==============================================================================
# PROJETO AURORA SIGER - ORQUESTRADOR CENTRAL E INTEGRAÇÃO DE SESSÕES COM IA
# ==============================================================================

import os
import json
from dotenv import load_dotenv
from google import genai

# Importação dos módulos independentes de cada fase
from fase1 import executar_fase1
from fase2 import executar_fase2
from fase3 import executar_fase3

# Carrega as variáveis de ambiente a partir do arquivo .env (onde está a chave de API)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Inicializa o cliente oficial da Google GenAI caso a chave exista
client = genai.Client(api_key=api_key) if api_key else None


def rodar_simulacao_integrada():
    """
    Função principal encarregada de coordenar o fluxo linear do Projeto Aurora.
    Coleta as saídas em bruto das três fases, encapsula-as em um payload JSON
    e executa o pipeline de requisição dupla com a IA para auditoria técnica.
    """
    print("=" * 85)
    print("INICIANDO SISTEMA INTEGRADO DA MISSÃO AURORA".center(85))
    print("=" * 85)

    # --------------------------------------------------------------------------
    # EXECUÇÃO DO PIPELINE DE DADOS (Módulos Independentes)
    # --------------------------------------------------------------------------
    # Coleta de métricas e status de validação do lançamento
    resultados_f1 = executar_fase1()

    # Processamento da fila de pouso orbital (FIFO/Insertion Sort)
    resultados_f2 = executar_fase2()

    # Análise de eficiência operacional e previsão por regressão linear manual
    resultados_f3 = executar_fase3()

    # Consolidando o pacote de dados centralizado (Data Lake Temporário)
    contexto_operacional = {
        "Fase_1_Lancamento": resultados_f1,
        "Fase_2_Pouso": resultados_f2,
        "Fase_3_Colonia": resultados_f3,
    }

    # Converte o dicionário global para string JSON estruturada
    dados_json = json.dumps(contexto_operacional, indent=2, ensure_ascii=False)

    # Bloqueio de segurança caso a chave da API do Gemini não esteja configurada
    if not client:
        print(
            "\n[!] Chave 'GEMINI_API_KEY' ausente no arquivo .env. Encerrando sem IA."
        )
        return

    print("\n" + "=" * 85)
    print("PROCESSAMENTO DE DADOS E AUDITORIA (IA)".center(85))
    print("=" * 85)

    # --------------------------------------------------------------------------
    # REQUISIÇÃO IA 1: Otimização e Enriquecimento do Contexto Técnico
    # --------------------------------------------------------------------------
    print(">> Extraindo correlações e gerando contexto analítico profundo...")
    prompt_contexto = (
        f"Você é um Engenheiro de Sistemas Aeroespaciais sênior. Analise os seguintes logs em bruto "
        f"obtidos através das 3 fases integradas da missão Aurora:\n{dados_json}\n\n"
        f"Gere um relatório puramente técnico correlacionando os eventos de forma cruzada. Explique como "
        f"as falhas de uma fase impactam o ecossistema das fases subsequentes (ex: se houve perda ou retenção "
        f"de módulos vitais na Fase 2, correlacione com a severidade do corte de carga na colônia na Fase 3). "
        f"Adote um tom estritamente profissional, acadêmico e detalhista."
    )

    # Executa a primeira chamada para consolidação do conhecimento cruzado
    resposta_contexto = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt_contexto
    )

    # --------------------------------------------------------------------------
    # REQUISIÇÃO IA 2: Formatação Estrita e Boletim Direto por Fases
    # --------------------------------------------------------------------------
    print(">> Sintetizando Boletim Executivo Estruturado...\n")
    prompt_executivo = (
        f"Com base na análise técnica detalhada fornecida pela engenharia de sistemas:\n"
        f"'{resposta_contexto.text}'\n\n"
        f"Atue como o Diretor de Voo da Missão Aurora. Escreva um boletim operacional contextualizado "
        f"que deve seguir OBRIGATORIAMENTE o layout estrito abaixo, utilizando as setas '->' para inserir "
        f"sua resposta altamente detalhada, clara e objetiva para cada uma das fases:\n\n"
        f"INICIANDO FASE 1: TELEMETRIA E PRÉ-DESCOLAGEM\n"
        f"-> [Insira aqui o seu retorno contextual detalhado sobre a Fase 1: análise do status GO/NO-GO, sucessos e impacto dos erros de telemetria]\n\n"
        f"INICIANDO FASE 2: APROXIMAÇÃO E POUSO (MGPEB)\n"
        f"-> [Insira aqui o seu retorno contextual detalhado sobre a Fase 2: auditoria do gerenciamento de pouso, eficiência da ordenação da fila e riscos operacionais dos módulos retidos]\n\n"
        f"INICIANDO FASE 3: SISTEMA INTELIGENTE DA COLÓNIA\n"
        f"-> [Insira aqui o seu retorno contextual detalhado sobre a Fase 3: avaliação do algoritmo de balanceamento de carga, precisão da previsão eólica por regressão linear e o impacto real do corte seletivo de energia nos módulos não essenciais]\n\n"
        f"Restrições: Não altere os títulos das fases, preserve a estrutura exata solicitada e mantenha um tom de liderança sério e formal."
    )

    # Executa a segunda chamada injetando o contexto rico e o template visual
    resposta_executiva = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt_executivo
    )

    # exibição do output final idêntico ao modelo solicitado pelo grupo
    print(resposta_executiva.text)
    print("=" * 85)


if __name__ == "__main__":
    # Ponto de entrada padrão para execução isolada do script
    rodar_simulacao_integrada()
