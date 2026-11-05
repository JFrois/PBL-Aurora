"""5.6 Sistema multiagente simulado  |  INTEGRANTE 2  |

Padrão do projeto:
    As regras determinísticas decidem; a IA somente explica.

Funcionamento padrão:
    Não exige chave de API. Triador e especialistas utilizam regras
    e respostas prontas, conectadas às ferramentas do projeto.

Fluxo:
    entrada -> guardrail de entrada -> Triador
    -> handoff -> Especialista -> ferramenta determinística
    -> guardrail de saída -> resposta
    -> histórico de sessão e tracing

Agentes:
    Triador, Energia, Manutenção e Dados.

Ferramentas:
    consultar leituras: banco.py
    classificar risco: logica.py
    estimar consumo: modelo_linear.py

Integração opcional:
    O Gemini, disponível em src/core/ia.py, poderá ser utilizado
    somente para redigir explicações dos resultados calculados.
    Na ausência de chave, falha do serviço ou resposta rejeitada,
    deverá ser utilizada a explicação determinística.

Esta versão implementa o fluxo simulado. A chamada opcional ao
Gemini é uma possibilidade de evolução, não está implementada aqui.

Segurança:
    As ferramentas dos agentes somente consultam e calculam.
    Não alteram registros nem operam equipamentos.
    Os guardrails são didáticos e não garantem segurança completa.
    Decisões críticas exigem validação humana.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import re
import sqlite3
import unicodedata

from .banco import ErroBanco


AVISO_HUMANO = (
    "Recomendações exigem validação humana. "
    "Nenhuma alteração foi executada."
)


@dataclass
class Sessao:
    """Memória temporária: módulo em contexto, histórico e rastreamento."""
    historico: list[dict] = field(default_factory=list)
    trilha: list[str] = field(default_factory=list)
    modulo_id: str | None = None


def normalizar(texto: str) -> str:
    """Facilita comparar palavras com ou sem acentos."""
    caracteres = unicodedata.normalize("NFD", texto.lower())
    resultado = ""
    for caractere in caracteres:
        if unicodedata.category(caractere) != "Mn":
            resultado += caractere
    return resultado


def registrar_evento(sessao: Sessao, evento: str) -> None:
    """Tracing local e limitado; não grava o texto do usuário."""
    sessao.trilha.append(evento)
    sessao.trilha[:] = sessao.trilha[-100:]

# ----- Guardrails ---------------------------------------------------------
def guardrail_entrada(texto: str) -> tuple[bool, str]:
    if not isinstance(texto, str) or not texto.strip():
        return False, "Informe uma solicitação."
    if len(texto) > 1000:
        return False, "Use no máximo 1000 caracteres."

    mensagem = normalizar(texto)
    bloqueados = (
        "deslig", "desativ", "exclu", "apagu", "apag", "remov",
        "alter", "cadastr", "ligue", "ativar", "ative", "execut",
        "ignore", "ignorar", "senha", "credencia", "chave de api",
    )
    for palavra in bloqueados:
        if palavra in mensagem:
            return False, "Pedido bloqueado: o assistente somente consulta e recomenda."

    assuntos = (
        "energi", "consumo", "bateria", "previs", "estim",
        "manutenc", "falha", "risco", "alerta", "sensor",
        "dados", "leitura", "registro", "mod-", "colonia", "sustent",
    )
    for assunto in assuntos:
        if assunto in mensagem:
            return True, "Entrada aceita."
    return False, "Fora do escopo. Consulte energia, manutenção ou dados da colônia."


def guardrail_saida(resposta: str) -> tuple[bool, str]:
    """Verificação didática: limita afirmações e exige supervisão humana."""
    if not isinstance(resposta, str) or not resposta.strip():
        return False, "Resposta vazia."

    mensagem = normalizar(resposta)
    proibidos = (
        "acao executada", "desligamento realizado", "registro excluido",
        "consumo garantido", "sem possibilidade de erro",
        "envie sua senha", "informe sua senha",
    )
    for termo in proibidos:
        if termo in mensagem:
            return False, "Resposta bloqueada pelo guardrail de saída."
    if "validacao humana" not in mensagem:
        return False, "A resposta precisa informar a necessidade de validação humana."
    return True, "Saída aprovada."


# ----- Ferramentas determinísticas ---------------------------------------
def ferramenta_consultar_leituras(modulo_id: str | None = None) -> list[dict]:
    from . import banco

    return banco.listar_leituras(
        modulo_id=modulo_id, limite=None, ordem="desc"
    )


def ferramenta_classificar_risco(modulo_id: str) -> str:
    from .logica import classificar_risco

    leituras = ferramenta_consultar_leituras(modulo_id)
    if not leituras:
        raise ValueError("Módulo sem leituras disponíveis.")

    leitura = leituras[0]
    return classificar_risco(
        leitura, leitura["limite_consumo_w"], bool(leitura["essencial"])
    )


def ferramenta_prever_consumo(modulo_id: str) -> float:
    from .modelo_linear import preparar_dados, treinar_regressao, prever

    df = preparar_dados(ferramenta_consultar_leituras())
    locais = df[df["modulo_id"] == modulo_id]
    if locais.empty:
        raise ValueError("O módulo não possui leituras válidas para a regressão.")

    modelo = treinar_regressao(df)
    # Estimativa para condições observadas, não previsão de um instante futuro.
    entrada = locais.iloc[-1].to_dict()
    return prever(modelo, entrada)


def identificar_modulo(texto: str, sessao: Sessao) -> str | None:
    """Atualiza o contexto apenas quando o módulo existe no banco."""
    from . import banco

    mensagem = normalizar(texto)
    if "todos os modulos" in mensagem or "toda a colonia" in mensagem:
        sessao.modulo_id = None
        return None

    codigos = re.findall(r"\bMOD-\d+\b", texto.upper())
    if len(set(codigos)) > 1:
        raise ValueError("Consulte apenas um módulo por mensagem.")
    if "mod-" in mensagem and not codigos:
        raise ValueError("Use o formato MOD-01 para informar o módulo.")
    if not codigos:
        return sessao.modulo_id

    codigo = codigos[0]
    existentes = [modulo["id"] for modulo in banco.listar_modulos()]
    if codigo not in existentes:
        raise ValueError(f"Módulo {codigo} inexistente; contexto anterior preservado.")

    sessao.modulo_id = codigo
    return codigo


# ----- Agentes ------------------------------------------------------------
def agente_triador(texto: str, sessao: Sessao) -> str:
    """Escolhe o especialista por palavras-chave; não simula compreensão livre."""
    mensagem = normalizar(texto)
    if any(p in mensagem for p in ("manutenc", "falha", "risco", "alerta")):
        especialista = "manutencao"
    elif any(p in mensagem for p in ("energi", "consumo", "bateria", "previs", "estim", "sustent")):
        especialista = "energia"
    else:
        especialista = "dados"

    registrar_evento(sessao, f"Triador -> handoff -> {especialista}")
    return especialista


def agente_energia(texto: str, sessao: Sessao) -> str:
    if "bateria" in normalizar(texto):
        return (
            "O cenário de bateria está disponível na opção 8 do menu. "
            "Ele usa capacidade e geração hipotéticas, não telemetria real."
        )
    modulo = sessao.modulo_id
    if modulo is None:
        return "Informe um módulo para estimar consumo: consumo MOD-01."

    registrar_evento(sessao, "tool: prever_consumo")
    estimativa = ferramenta_prever_consumo(modulo)
    return (
        f"{modulo}: consumo estimado de {estimativa:.1f} W, nas condições "
        "da última leitura válida. Não é previsão de um ciclo futuro. "
        "Consulte as métricas na opção 9: a regressão da base original "
        "não superou a média em MAE e não deve controlar equipamentos."
    )


def agente_manutencao(texto: str, sessao: Sessao) -> str:
    modulo = sessao.modulo_id
    if modulo is None:
        return "Informe um módulo: risco MOD-01."

    registrar_evento(sessao, "tool: classificar_risco")
    risco = ferramenta_classificar_risco(modulo)
    orientacoes = {
        "bloqueado": "Inspecione o sensor; a leitura não deve fundamentar uma decisão operacional.",
        "alto": "Solicite revisão técnica do consumo no módulo essencial.",
        "medio": "Avalie o consumo elevado e possíveis cargas não essenciais.",
        "baixo": "Mantenha o monitoramento; esta classificação não garante ausência de falhas.",
    }
    return f"{modulo}: risco da última leitura = {risco}. {orientacoes[risco]}"


def agente_dados(texto: str, sessao: Sessao) -> str:
    registrar_evento(sessao, "tool: consultar_leituras")
    leituras = ferramenta_consultar_leituras(sessao.modulo_id)
    escopo = sessao.modulo_id or "todos os módulos"
    resposta = f"Escopo: {escopo}. Registros disponíveis: {len(leituras)}."
    if leituras:
        resposta += f" Último registro: {leituras[0]['data_registro']}."
    return resposta


def executar_assistente(texto: str, sessao: Sessao | None = None) -> str:
    if sessao is None:
        sessao = Sessao()

    permitido, motivo = guardrail_entrada(texto)
    registrar_evento(sessao, f"guardrail_entrada: {permitido}")
    if not permitido:
        # Não guardar mensagens rejeitadas: podem conter dados sensíveis.
        return f"{motivo} {AVISO_HUMANO}"

    especialista = "triador"
    try:
        identificar_modulo(texto, sessao)
        especialista = agente_triador(texto, sessao)
        if especialista == "energia":
            resposta = agente_energia(texto, sessao)
        elif especialista == "manutencao":
            resposta = agente_manutencao(texto, sessao)
        else:
            resposta = agente_dados(texto, sessao)
    except (ValueError, ErroBanco, sqlite3.Error):
        registrar_evento(sessao, "consulta: indisponível ou entrada inválida")
        resposta = (
            "Não foi possível concluir. Confira o código do módulo, as leituras "
            "e a faixa de treinamento. Use um único módulo, como MOD-01."
        )

    resposta = f"{resposta} {AVISO_HUMANO}"
    aprovado, motivo = guardrail_saida(resposta)
    registrar_evento(sessao, f"guardrail_saida: {aprovado}")
    if not aprovado:
        resposta = f"{motivo} {AVISO_HUMANO}"

    sessao.historico.append({
        "pedido": texto, 
        "agente": especialista,
        "modulo": sessao.modulo_id, 
        "resposta": resposta,
    })
    sessao.historico[:] = sessao.historico[-20:]
    return resposta       


def menu_assistente() -> None:
    sessao = Sessao()

    while True:
        print("ASSISTENTE MULTIAGENTE SIMULADO — sem LLM ou API")
      

        if sessao.modulo_id:
            print(f"Módulo em contexto: {sessao.modulo_id}")
        else:
            print("Nenhum módulo selecionado.")

        print("\nO que você deseja consultar?")
        print(" [1] Estimar consumo de um módulo")
        print(" [2] Consultar risco de um módulo")
        print(" [3] Consultar registros de um módulo")
        print(" [4] Consultar registros de todos os módulos")
        print(" [5] Ver histórico da conversa")
        print(" [6] Ver etapas do atendimento (tracing)")
        print(" [7] Limpar conversa e módulo selecionado")
        print(" [0] Voltar ao menu principal")

        print("\nVocê também pode escrever uma consulta, por exemplo:")
        print(" consumo MOD-01")
        print(" risco MOD-01")
        print(" dados de todos os módulos")
        print("\nO assistente apenas consulta e recomenda; não altera o sistema.")

        entrada = input(
            "\nDigite o número da opção ou escreva sua consulta: "
        ).strip()

        comando = normalizar(entrada)

        if comando in ("0", "sair"):
            break

        if comando in ("5", "historico"):
            print("\nHISTÓRICO")

            if not sessao.historico:
                print("Ainda não há consultas. Escolha uma opção de 1 a 4.")

            for interacao in sessao.historico:
                print(f"\nVocê: {interacao['pedido']}")
                print(
                    f"Agente {interacao['agente']}: "
                    f"{interacao['resposta']}"
                )

            input("\nPressione Enter para continuar...")
            continue

        if comando in ("6", "trilha"):
            print("\nETAPAS DO ATENDIMENTO")

            if not sessao.trilha:
                print("Ainda não há eventos. Faça uma consulta primeiro.")

            for evento in sessao.trilha:
                print(f" - {evento}")

            input("\nPressione Enter para continuar...")
            continue

        if comando in ("7", "limpar"):
            sessao = Sessao()
            print("\nConversa e módulo selecionado foram limpos.")
            input("\nPressione Enter para continuar...")
            continue

        if comando in ("1", "2", "3"):
            from . import banco

            try:
                modulos = banco.listar_modulos()
            except (ErroBanco, sqlite3.Error):
                print("\nNão foi possível consultar os módulos.")
                input("\nPressione Enter para continuar...")
                continue

            if not modulos:
                print("\nNão há módulos cadastrados.")
                input("\nPressione Enter para continuar...")
                continue

            print("\nMódulos disponíveis:")
            for modulo in modulos:
                print(f" - {modulo['id']}")

            if sessao.modulo_id:
                print(
                    f"\nPressione Enter para manter {sessao.modulo_id}, "
                    "ou informe outro código."
                )

            modulo_escolhido = input(
                "Código do módulo (exemplo: MOD-01): "
            ).strip().upper()

            if not modulo_escolhido:
                modulo_escolhido = sessao.modulo_id

            if not modulo_escolhido:
                print("\nInforme o código de um módulo.")
                input("\nPressione Enter para continuar...")
                continue

            codigos_validos = [modulo["id"] for modulo in modulos]

            if modulo_escolhido not in codigos_validos:
                print("\nCódigo inválido. Escolha um dos módulos listados.")
                input("\nPressione Enter para continuar...")
                continue

            assuntos = {
                "1": "consumo",
                "2": "risco",
                "3": "dados",
            }

            pedido = f"{assuntos[comando]} {modulo_escolhido}"

        elif comando == "4":
            pedido = "dados de todos os módulos"

        elif not entrada:
            print("\nDigite uma opção ou uma consulta antes de continuar.")
            input("\nPressione Enter para continuar...")
            continue

        elif entrada.isdigit():
            print("\nOpção inválida. Escolha um número de 0 a 7.")
            input("\nPressione Enter para continuar...")
            continue

        else:
            pedido = entrada

        print(f"\nConsulta: {pedido}")
        print("\n" + executar_assistente(pedido, sessao))

        print("\nEtapas recentes:")
        for evento in sessao.trilha[-4:]:
            print(f" - {evento}")

        input("\nPressione Enter para continuar...")