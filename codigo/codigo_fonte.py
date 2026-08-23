# ==============================================================================
# NÚCLEO COGNITIVO DA AURORA SIGER (NCAS) — FASE 5
# Arquivo principal do sistema
#
# Integrante 1 — Desenvolvimento Core e Estrutura de Dados
#   - Esqueleto do menu de navegação no terminal
#   - Funções de leitura/gravação em registros_colonia.txt (open, read, write, append)
#   - Funções de carregar/salvar dados_colonia.json
#
# Integrante 2 — Regra Lógica e Engenharia de Prompts
#   - validar_alerta_critico()      -> regra booleana simplificada (De Morgan/Simplificação)
#   - montar_prompt_*()             -> prompts zero-shot / few-shot / saída estruturada
#   - simular_resposta_assistente() -> resposta real (Gemini, se disponível) ou mock local
#
# A integração com IA é OPCIONAL (item 2.3 do enunciado): se a biblioteca
# google-genai/dotenv não estiver instalada, ou a GEMINI_API_KEY não existir,
# o sistema cai automaticamente para uma resposta simulada localmente —
# o programa nunca quebra por causa disso.
# ==============================================================================

import json
import os
from datetime import datetime

# ------------------------------------------------------------------------
# CAMINHOS DE ARQUIVO — resolvidos a partir da localização deste script
# (e não do diretório de onde o programa é executado), para que
# "python codigo/codigo_fonte.py" e "python main.py" encontrem os mesmos
# arquivos em ../dados/, independentemente da pasta atual do terminal.
# ------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "dados"))
ARQUIVO_REGISTROS = os.path.join(DADOS_DIR, "registros_colonia.txt")
ARQUIVO_DADOS = os.path.join(DADOS_DIR, "dados_colonia.json")

os.makedirs(DADOS_DIR, exist_ok=True)  # garante que a pasta dados/ exista

# ------------------------------------------------------------------------
# INTEGRAÇÃO OPCIONAL COM IA (mesmo padrão usado em main.py)
# ------------------------------------------------------------------------
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    from google import genai

    _client = genai.Client(api_key=_API_KEY) if _API_KEY else None
except ImportError:
    _client = None


def imprimir_quadro(titulo: str, linhas: list) -> None:
    """Exibe um bloco de texto formatado no terminal (padrão usado nas outras fases)."""
    largura = 70
    print("-" * largura)
    print(f"| {titulo.center(largura - 4)} |")
    print("|" + " " * (largura - 2) + "|")
    for linha in linhas:
        print(f"| {linha.ljust(largura - 4)} |")
    print("-" * largura)


# ==============================================================================
# BLOCO 1 — MANIPULAÇÃO DE ARQUIVO TEXTO (registros_colonia.txt)
#
# Por que TXT? Registros de log, acessos e ocorrências são eventos sequenciais,
# de formato livre, gerados continuamente durante a execução. Não precisam ser
# consultados por campo específico — apenas lidos em ordem ou anexados um a um.
# O modo "append" (a) é ideal para isso: cada evento novo é gravado ao final do
# arquivo sem necessidade de reescrever o conteúdo já existente.
# ==============================================================================


def gravar_registro(mensagem: str, tipo: str = "LOG") -> None:
    """Adiciona uma nova linha ao arquivo de registros (modo append)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] [{tipo}] {mensagem}\n"
    with open(ARQUIVO_REGISTROS, "a", encoding="utf-8") as arquivo:
        arquivo.write(linha)
    print(">> Registro salvo com sucesso.")


def ler_registros() -> None:
    """Lê e exibe todo o conteúdo do arquivo de registros (modo read)."""
    if not os.path.exists(ARQUIVO_REGISTROS):
        print(f">> Nenhum registro encontrado ainda em: {ARQUIVO_REGISTROS}")
        return

    with open(ARQUIVO_REGISTROS, "r", encoding="utf-8") as arquivo:
        linhas = [linha.strip() for linha in arquivo.readlines() if linha.strip()]

    if not linhas:
        print(">> O arquivo de registros existe, mas está vazio.")
        return

    print(f"\n--- REGISTROS DA COLÔNIA ({len(linhas)} entradas) ---")
    for i, linha in enumerate(linhas, start=1):
        print(f"  {i:>3}. {linha}")
    print("-" * 60)


# ==============================================================================
# BLOCO 2 — MANIPULAÇÃO DE ARQUIVO JSON (dados_colonia.json)
#
# Por que JSON? Módulos e alertas possuem uma estrutura fixa de campos
# (nome, status, consumo, prioridade...) que precisa ser consultada,
# validada e atualizada de forma organizada — inclusive pelas regras lógicas
# do Integrante 2. Um dicionário/lista de dicionários representa isso melhor
# do que texto livre, e o módulo json permite carregar e salvar essa estrutura
# de forma direta.
# ==============================================================================


def carregar_dados_json() -> dict:
    """Carrega os dados estruturados (módulos e alertas) do arquivo JSON."""
    if not os.path.exists(ARQUIVO_DADOS):
        print(f">> Arquivo de dados JSON não encontrado em: {ARQUIVO_DADOS}")
        print(">> Iniciando estrutura vazia.")
        return {"modulos": [], "alertas": []}

    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_dados_json(dados: dict) -> None:
    """Salva a estrutura completa de dados (módulos e alertas) no arquivo JSON."""
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)
    print(">> Dados JSON atualizados com sucesso.")


def exibir_modulos() -> None:
    """Exibe todos os módulos cadastrados no JSON."""
    dados = carregar_dados_json()
    modulos = dados.get("modulos", [])

    if not modulos:
        print(">> Nenhum módulo cadastrado.")
        return

    print(f"\n--- MÓDULOS DA COLÔNIA ({len(modulos)} cadastrados) ---")
    consumo_total = 0.0
    for i, m in enumerate(modulos, start=1):
        consumo_total += float(m.get("consumo_kw", 0))
        print(
            f"  {i:>2}. {m['nome']:<25} | tipo: {m['tipo']:<15} | "
            f"status: {m['status']:<12} | consumo: {m['consumo_kw']:>6.1f} kW"
        )
    print("-" * 70)
    print(f"  Consumo total estimado: {consumo_total:.1f} kW")
    print("-" * 70)


def exibir_alertas() -> None:
    """Exibe todos os alertas operacionais cadastrados no JSON."""
    dados = carregar_dados_json()
    alertas = dados.get("alertas", [])

    if not alertas:
        print(">> Nenhum alerta registrado.")
        return

    print(f"\n--- ALERTAS OPERACIONAIS ({len(alertas)} registrados) ---")
    for i, a in enumerate(alertas, start=1):
        marcador = "🔴" if validar_alerta_critico(a) else "🟡"
        print(
            f"  {i:>2}. {marcador} [{a['prioridade'].upper()}] {a['modulo']} — "
            f"{a['tipo_ocorrencia']}: {a['mensagem']} ({a['data']})"
        )
    print("-" * 70)


def cadastrar_modulo() -> None:
    """Cadastra um novo módulo interativamente e persiste no JSON."""
    dados = carregar_dados_json()

    nome = input("Nome do módulo: ").strip()
    tipo = input("Tipo (ex: habitacao, energia, laboratorio): ").strip()
    status = input("Status (operacional/inativo/manutencao): ").strip()
    try:
        consumo = float(input("Consumo em kW: ").strip())
    except ValueError:
        consumo = 0.0

    novo_modulo = {
        "nome": nome,
        "tipo": tipo,
        "status": status,
        "consumo_kw": consumo,
        "ultima_manutencao": datetime.now().strftime("%Y-%m-%d"),
    }

    dados.setdefault("modulos", []).append(novo_modulo)
    salvar_dados_json(dados)
    gravar_registro(f"Novo módulo cadastrado: {nome} ({status})", tipo="CADASTRO")


# ==============================================================================
# BLOCO 3 — REGRA LÓGICA E SIMULAÇÃO DE IA (Integrante 2)
# ==============================================================================


def validar_alerta_critico(alerta: dict) -> bool:
    """
    Regra de negócio original (item 1.4 do enunciado):
        ALERTA_CRITICO = (FALHA AND CRITICO) OR (FALHA AND NOT CRITICO)

    Aplicando o Teorema da Simplificação (X.Y + X.~Y = X), com X = FALHA
    e Y = CRITICO, a variável CRITICO se cancela e a regra se reduz a:
        ALERTA_CRITICO = FALHA

    Ou seja: para o disparo do alerta importa apenas se houve falha —
    a criticidade adicional não muda o resultado da expressão.
    """
    falha = alerta.get("tipo_ocorrencia") == "falha_critica"
    return falha


def montar_prompt_zero_shot(alerta: dict) -> str:
    """Prompt zero-shot: pede um resumo do alerta sem exemplos prévios."""
    return (
        "Resuma em uma frase, em tom técnico e objetivo, o seguinte alerta "
        f"operacional da colônia: módulo '{alerta['modulo']}', "
        f"ocorrência '{alerta['tipo_ocorrencia']}', "
        f"prioridade '{alerta['prioridade']}', "
        f"descrição: '{alerta['mensagem']}'."
    )


def montar_prompt_few_shot(solicitacao: str) -> str:
    """Prompt few-shot: dá exemplos de classificação antes de pedir a nova."""
    return (
        "Classifique solicitações da tripulação em: URGENTE, ROTINA ou INFORMATIVA.\n\n"
        "Exemplo 1: 'Vazamento de ar na Habitação' -> URGENTE\n"
        "Exemplo 2: 'Solicito troca de filtro na próxima manutenção' -> ROTINA\n"
        "Exemplo 3: 'Qual o horário do próximo pouso de suprimentos?' -> INFORMATIVA\n\n"
        f"Solicitação: '{solicitacao}' -> "
    )


def montar_prompt_saida_estruturada(alerta: dict) -> str:
    """Prompt que exige explicitamente uma saída estruturada em JSON."""
    return (
        "Responda APENAS com um JSON válido, sem texto adicional, no formato "
        '{"modulo": str, "critico": bool, "acao_recomendada": str}, '
        f"considerando o alerta: {json.dumps(alerta, ensure_ascii=False)}"
    )


def simular_resposta_assistente(prompt: str) -> str:
    """
    Retorna a resposta do assistente inteligente.

    Se houver uma GEMINI_API_KEY configurada e a biblioteca google-genai
    instalada, faz a chamada real (mesmo cliente usado em main.py).
    Caso contrário, devolve uma resposta simulada localmente — o item 2.3
    do enunciado permite explicitamente essa simulação.
    """
    if _client:
        try:
            resposta = _client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return resposta.text.strip()
        except Exception as erro:  # falha de rede/quota etc. -> cai para o mock
            return (
                f"[IA indisponível ({erro}); resposta simulada] Alerta reconhecido "
                "e registrado para acompanhamento do Centro de Controle."
            )

    return (
        "[Resposta simulada] Alerta reconhecido. Recomenda-se isolar o módulo "
        "afetado e acionar a equipe de manutenção com prioridade compatível "
        "ao nível informado."
    )


def analisar_alerta_operacional() -> None:
    """Opção 6 do menu: aplica a regra lógica sobre os alertas e chama a IA para os críticos."""
    dados = carregar_dados_json()
    alertas = dados.get("alertas", [])

    if not alertas:
        print(">> Nenhum alerta cadastrado para analisar.")
        return

    print("\n--- ANÁLISE LÓGICA DE ALERTAS ---")
    for a in alertas:
        critico = validar_alerta_critico(a)
        status = "CRÍTICO" if critico else "não crítico"
        print(f"  {a['modulo']:<25} -> {status}")

        if critico:
            prompt = montar_prompt_zero_shot(a)
            resposta = simular_resposta_assistente(prompt)
            print(f"    Prompt (zero-shot): {prompt}")
            print(f"    Resposta da IA: {resposta}")
            gravar_registro(
                f"Alerta crítico analisado ({a['modulo']}): {resposta}",
                tipo="RESPOSTA_IA",
            )
    print("-" * 70)


def simular_interacao_assistente() -> None:
    """Opção 7 do menu: demonstra os três tipos de prompt exigidos no item 1.5."""
    dados = carregar_dados_json()
    alertas = dados.get("alertas", [])
    alerta_exemplo = (
        alertas[0]
        if alertas
        else {
            "modulo": "Produção de Oxigênio",
            "tipo_ocorrencia": "falha_critica",
            "prioridade": "alta",
            "mensagem": "Exemplo genérico de alerta.",
            "data": datetime.now().strftime("%Y-%m-%d"),
        }
    )

    print("\n--- SIMULAÇÃO DE INTERAÇÃO COM O ASSISTENTE INTELIGENTE ---")

    print("\n[1] Prompt ZERO-SHOT (resumo de alerta):")
    prompt_zs = montar_prompt_zero_shot(alerta_exemplo)
    print(f"  Prompt: {prompt_zs}")
    print(f"  Resposta: {simular_resposta_assistente(prompt_zs)}")

    print("\n[2] Prompt FEW-SHOT (classificação de solicitação):")
    solicitacao = (
        input("  Digite uma solicitação da tripulação para classificar: ").strip()
        or "Preciso de mais água na Habitação até amanhã"
    )
    prompt_fs = montar_prompt_few_shot(solicitacao)
    print(f"  Resposta: {simular_resposta_assistente(prompt_fs)}")

    print("\n[3] Prompt de SAÍDA ESTRUTURADA (JSON):")
    prompt_est = montar_prompt_saida_estruturada(alerta_exemplo)
    print(f"  Resposta: {simular_resposta_assistente(prompt_est)}")
    print("-" * 70)

    gravar_registro(
        "Simulação de interação com o assistente executada.", tipo="RESPOSTA_IA"
    )


# ==============================================================================
# BLOCO 4 — MENU DE NAVEGAÇÃO (execução interativa/standalone)
# ==============================================================================


def exibir_menu() -> None:
    print("\n" + "=" * 55)
    print("NÚCLEO COGNITIVO DA AURORA SIGER (NCAS)".center(55))
    print("=" * 55)
    print("1 - Cadastrar novo módulo")
    print("2 - Consultar registros salvos (TXT)")
    print("3 - Adicionar registro manual (TXT)")
    print("4 - Exibir módulos cadastrados (JSON)")
    print("5 - Exibir alertas operacionais (JSON)")
    print("6 - Analisar alerta operacional (validação lógica + IA)")
    print("7 - Simular resposta do assistente inteligente")
    print("0 - Sair")
    print("=" * 55)


def main() -> None:
    """Loop interativo — usado quando o arquivo é executado diretamente."""
    gravar_registro("Sistema NCAS iniciado.", tipo="SISTEMA")

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_modulo()
        elif opcao == "2":
            ler_registros()
        elif opcao == "3":
            mensagem = input("Digite o registro a ser salvo: ").strip()
            gravar_registro(mensagem, tipo="MANUAL")
        elif opcao == "4":
            exibir_modulos()
        elif opcao == "5":
            exibir_alertas()
        elif opcao == "6":
            analisar_alerta_operacional()
        elif opcao == "7":
            simular_interacao_assistente()
        elif opcao == "0":
            gravar_registro("Sistema NCAS encerrado.", tipo="SISTEMA")
            print(">> Encerrando o Núcleo Cognitivo. Até logo!")
            break
        else:
            print(">> Opção inválida. Tente novamente.")


# ==============================================================================
# BLOCO 5 — PONTO DE ENTRADA NÃO INTERATIVO PARA O main.py (PIPELINE INTEGRADO)
#
# Segue o mesmo padrão de executar_fase1()...executar_fase4(): sem input(),
# imprime um relatório e devolve um dicionário-resumo para o Data Lake
# consolidado em main.py.
# ==============================================================================

# ==============================================================================
# BLOCO 5 — PONTO DE ENTRADA NÃO INTERATIVO PARA O main.py (PIPELINE INTEGRADO)
# ==============================================================================


def executar_fase5(client=None, res_f2=None, res_f4=None) -> dict:
    """
    Executa a Fase 5 integrando as falhas de pouso (Fase 2) e a topologia (Fase 4)
    diretamente no arquivo JSON do NCAS para gerar análises da IA.
    """
    global _client
    if client is not None:
        _client = client

    print("\n" + "=" * 85)
    print("INICIANDO FASE 5: NÚCLEO COGNITIVO DA AURORA SIGER (NCAS)".center(85))
    print("=" * 85)

    # Limpa a base atual e reconstrói o JSON com o cenário real do pipeline
    dados = {"modulos": [], "alertas": []}

    # 1. Alimentando Módulos Operacionais a partir da Rede (Fase 4)
    if res_f4:
        for mod in res_f4.get("modulos_operacionais", []):
            dados["modulos"].append(
                {
                    "nome": mod,
                    "tipo": "infraestrutura",
                    "status": "operacional",
                    "consumo_kw": 0.0,
                    "ultima_manutencao": datetime.now().strftime("%Y-%m-%d"),
                }
            )

    # 2. Alimentando Alertas Críticos a partir das Falhas de Pouso (Fase 2)
    if res_f2:
        for mod_falho in res_f2.get("em_espera", []):
            dados["alertas"].append(
                {
                    "modulo": mod_falho,
                    "tipo_ocorrencia": "falha_critica",
                    "prioridade": "alta",
                    "mensagem": "Módulo retido em órbita ou destruído durante a descida (Fase 2).",
                    "data": datetime.now().strftime("%Y-%m-%d"),
                }
            )

    # Salva o arquivo JSON integrando o pipeline todo
    salvar_dados_json(dados)

    alertas_criticos = [a for a in dados["alertas"] if validar_alerta_critico(a)]
    respostas_ia = []

    for alerta in alertas_criticos:
        prompt = montar_prompt_zero_shot(alerta)
        resposta = simular_resposta_assistente(prompt)
        respostas_ia.append({"modulo": alerta["modulo"], "resposta": resposta})

    imprimir_quadro(
        "RESUMO NCAS",
        [
            f"Módulos em rede (Fase 4): {len(dados['modulos'])}",
            f"Alertas de Pouso (Fase 2): {len(dados['alertas'])}",
            f"Alertas críticos (Regra Lógica): {len(alertas_criticos)}",
            f"Análises de IA geradas: {len(respostas_ia)}",
        ],
    )

    gravar_registro(
        f"Fase 5 executada via pipeline integrado. {len(alertas_criticos)} alertas processados.",
        tipo="SISTEMA",
    )

    return {
        "modulos": dados["modulos"],
        "total_alertas": len(dados["alertas"]),
        "alertas_criticos": alertas_criticos,
        "respostas_ia": respostas_ia,
    }


if __name__ == "__main__":
    main()
