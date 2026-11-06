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
    try:
        return prever(modelo, entrada)
    except ValueError as erro:
        raise ValueError(
            f"Não foi possível estimar o consumo de {modulo_id}. "
            f"Leitura utilizada: {entrada['data_registro']}. {erro} "
            "Use a opção 3 do assistente para conferir o último registro. "
            "Se houver erro de cadastro, corrija-o no menu principal. "
            "Se a medição estiver correta, o modelo precisa de dados "
            "representativos dessa condição e nova validação."
        ) from erro


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
        if sessao.modulo_id is not None:
            ultima = leituras[0]
            resposta += (
                f" Potência registrada: {ultima['consumo_w']} W."
                f" Temperatura: {ultima['temperatura_c']} °C."
                f" Umidade: {ultima['umidade_pct']}%."
                f" Status: {ultima['status_operacional']}."
                " Estes são valores registrados, não estimativas do modelo."
            )
    else:
        resposta += " Não há leituras para apresentar nesse escopo."
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
    except ValueError as erro:
        registrar_evento(sessao, "consulta: indisponível ou entrada inválida")
        resposta = str(erro)
    except (ErroBanco, sqlite3.Error):
        registrar_evento(sessao, "consulta: indisponível ou entrada inválida")
        resposta = (
            "Não foi possível acessar os dados necessários. "
            "Verifique o banco pelo menu principal e tente novamente."
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
    import os
    from textwrap import fill

    from . import banco

    sessao = Sessao()
    largura = 70

    def titulo(texto):
        print("\n" + "=" * largura)
        print(texto.center(largura))
        print("=" * largura)

    def mostrar_texto(texto):
        print(
            fill(
                texto,
                width=largura,
                initial_indent="  ",
                subsequent_indent="  ",
            )
        )

    def mostrar_etapas(eventos):
        if not eventos:
            mostrar_texto(
                "Ainda não há eventos. Faça uma consulta nas opções 1 a 4."
            )
            return

        nomes = {
            "guardrail_entrada: True": "Entrada aprovada",
            "guardrail_entrada: False": "Entrada bloqueada",
            "guardrail_saida: True": "Resposta aprovada",
            "guardrail_saida: False": "Resposta bloqueada",
            "tool: consultar_leituras": "Ferramenta: consultar registros",
            "tool: classificar_risco": "Ferramenta: classificar risco",
            "tool: prever_consumo": "Ferramenta: estimar consumo",
            "consulta: indisponível ou entrada inválida":
                "Consulta indisponível ou entrada inválida",
        }

        for numero, evento in enumerate(eventos, start=1):
            descricao = nomes.get(evento, evento)

            if evento.startswith("Triador -> handoff -> "):
                especialista = evento.split(" -> ")[-1]
                especialistas = {
                    "energia": "Energia",
                    "manutencao": "Manutenção",
                    "dados": "Dados",
                }
                nome = especialistas.get(especialista, especialista)
                descricao = f"Triador encaminhou ao especialista de {nome}"

            mostrar_texto(f"{numero}. {descricao}")

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        titulo("ASSISTENTE DA COLÔNIA")

        print("  Simulação por regras | Sem LLM ou chave de API")
        print(
            f"  Módulo selecionado: "
            f"{sessao.modulo_id or 'nenhum'}"
        )

        print("\n  CONSULTAS")
        print("  [1] Estimar consumo nas condições da última leitura válida")
        print("  [2] Avaliar risco da última leitura de um módulo")
        print("  [3] Ver resumo e última leitura de um módulo")
        print("  [4] Ver resumo dos registros de toda a colônia")

        print("\n  CONVERSA")
        print("  [5] Ver histórico")
        print("  [6] Ver etapas do atendimento")
        print("  [7] Limpar conversa e módulo selecionado")
        print("  [0] Voltar ao menu principal")

        print("\n" + "-" * largura)
        mostrar_texto(
            "Digite uma opção de 0 a 7 ou uma consulta, "
            "como: consumo MOD-01 ou risco MOD-05."
        )
        mostrar_texto(
            "A estimativa pode ser bloqueada fora da faixa de treinamento. "
            "Use a opção 3 para conferir os valores registrados."
        )

        entrada = input("\nSua escolha ou consulta: ").strip()
        comando = normalizar(entrada)

        if comando in ("0", "sair"):
            print("\nRetornando ao menu principal...")
            break

        if not entrada:
            mostrar_texto("Nenhuma opção informada. Escolha uma opção de 0 a 7.")
            continue

        if comando in ("5", "historico"):
            titulo("HISTÓRICO DA CONVERSA")

            if not sessao.historico:
                mostrar_texto(
                    "Ainda não há consultas registradas. "
                    "Comece pelas opções 1 a 4."
                )

            for numero, interacao in enumerate(sessao.historico, start=1):
                print(f"\n  CONSULTA {numero}")
                mostrar_texto(f"Você: {interacao['pedido']}")
                mostrar_texto(f"Agente: {interacao['agente']}")

                print("\n  Resposta:")
                mostrar_texto(interacao["resposta"])

            continue

        if comando in ("6", "trilha"):
            titulo("ETAPAS DO ATENDIMENTO")
            mostrar_etapas(sessao.trilha)
            continue

        if comando in ("7", "limpar"):
            sessao = Sessao()
            titulo("CONVERSA LIMPA")
            mostrar_texto(
                "O histórico, as etapas e o módulo selecionado foram limpos."
            )
            continue

        if comando in ("1", "2", "3"):
            try:
                modulos = banco.listar_modulos()
            except (ErroBanco, sqlite3.Error):
                mostrar_texto(
                    "Não foi possível consultar os módulos. "
                    "Verifique a disponibilidade do banco."
                )
                continue

            if not modulos:
                mostrar_texto("Não há módulos cadastrados.")
                continue

            os.system("cls" if os.name == "nt" else "clear")
            titulo("SELEÇÃO DO MÓDULO")

            for modulo in modulos:
                nome = modulo.get("nome") or modulo.get("nome_modulo") or ""
                descricao = f"{modulo['id']} — {nome}" if nome else modulo["id"]
                mostrar_texto(descricao)

            if sessao.modulo_id:
                print()
                mostrar_texto(
                    f"Pressione Enter para manter {sessao.modulo_id} "
                    "ou informe outro código."
                )

            modulo_escolhido = input(
                "\nCódigo do módulo (ex.: MOD-05; 0 para cancelar): "
            ).strip().upper()

            if modulo_escolhido == "0":
                mostrar_texto("Consulta cancelada.")
                continue

            if not modulo_escolhido:
                modulo_escolhido = sessao.modulo_id

            codigos_validos = [modulo["id"] for modulo in modulos]

            if modulo_escolhido not in codigos_validos:
                mostrar_texto(
                    "Código não informado ou inválido. "
                    "Utilize um dos códigos apresentados."
                )
                continue

            assuntos = {
                "1": "consumo",
                "2": "risco",
                "3": "dados",
            }
            pedido = f"{assuntos[comando]} {modulo_escolhido}"

        elif comando == "4":
            pedido = "dados de todos os módulos"

        elif entrada.isdigit():
            mostrar_texto("Opção inválida. Escolha um número de 0 a 7.")
            continue

        else:
            pedido = entrada

        # Guarda os eventos anteriores para mostrar somente os desta consulta.
        eventos_anteriores = len(sessao.trilha)
        trilha_anterior = sessao.trilha.copy()

        resposta = executar_assistente(pedido, sessao)

        # Considera o limite de 100 eventos mantidos na sessão.
        if (
            eventos_anteriores == 0
            or sessao.trilha[:eventos_anteriores] == trilha_anterior
        ):
            eventos_consulta = sessao.trilha[eventos_anteriores:]
        else:
            # Quando a trilha atinge o limite, mostra os eventos mais recentes.
            eventos_consulta = sessao.trilha[-4:]

        os.system("cls" if os.name == "nt" else "clear")
        titulo("RESULTADO DA CONSULTA")
        mostrar_texto(f"Consulta: {pedido}")
        print(
            f"  Módulo em contexto: "
            f"{sessao.modulo_id or 'nenhum — consulta global'}"
        )

        print("\n  RESPOSTA")
        print("  " + "-" * (largura - 4))

        # Exibe o aviso de responsabilidade em um bloco próprio.
        texto_resposta = resposta
        if resposta.endswith(AVISO_HUMANO):
            texto_resposta = resposta[:-len(AVISO_HUMANO)].strip()

        mostrar_texto(texto_resposta)

        print("\n  RESPONSABILIDADE")
        mostrar_texto(AVISO_HUMANO)

        print("\n  ETAPAS DESTA CONSULTA")
        mostrar_etapas(eventos_consulta)


        input("\nPressione Enter para voltar ao menu do assistente...")
        continue
