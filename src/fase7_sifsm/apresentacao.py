"""Telas explicativas do menu (texto no terminal)  |  INTEGRANTES 1 e 3

O enunciado pede que o sistema "exiba ou explique" o circuito lógico e apresente
uma análise final com limitações. Estas funções são só texto: curtas, claras e
ligadas ao que o sistema realmente faz (nada de texto genérico).
"""

from __future__ import annotations


def exibir_circuito_logico() -> None:
    """INTEGRANTE 1: mostra a regra booleana, o caminho do circuito (PNG/Tinkercad) e como
    cada porta lógica corresponde à função em logica.py."""
    from pathlib import Path

    from src.fase7_sifsm import logica

    raiz = Path(__file__).resolve().parents[2]
    png = raiz / "docs" / "fase7" / "graficos_ou_imagens" / "circuito_logico.png"
    link = raiz / "docs" / "fase7" / "link_tinkercad.txt"

    print(f"\n  {logica.NOME_REGRA}")
    print(f"  {logica.NOME_BLOQUEIO}\n")
    print("  Correspondência circuito <-> código:")
    print("    porta AND (A, B)        -> logica.acionar_alerta(A, B, ...)  (1º nível)")
    print("    porta AND (AB, C)       -> logica.acionar_alerta(A, B, C)    (2º nível)")
    print("    inversor NOT (C)        -> logica.bloquear_operacao(C)")
    print("    LED vermelho / amarelo  -> alerta registrado / operação bloqueada")
    print("    chaves A, B, C          -> consumo_alto(), essencial do módulo, sensor_valido()\n")
    print("  Circuito (diagrama)  :", png if png.exists() else "não gerado - rode: python -m src.fase7_sifsm.circuito_png")
    if link.exists():
        print("  Simulação Tinkercad  :", link.read_text(encoding="utf-8").strip() or "(arquivo vazio)")
    else:
        print("  Simulação Tinkercad  : montagem em docs/fase7/tinkercad/README.md "
              "(cole o link em docs/fase7/link_tinkercad.txt)")
    print("\n  Dica: a opção 5 do menu mostra a tabela-verdade que o circuito deve reproduzir.")


def exibir_arquitetura() -> None:
    """Relaciona o SIFSM aos conceitos de arquitetura do capítulo 14."""
    print("""1. PROCESSAMENTO ATUAL EM CPU

O SIFSM executa localmente o menu, as consultas SQLite, as regras
booleanas, as estruturas de dados e os agentes determinísticos.

A CPU coordena essas tarefas e executa os cálculos da simulação
e da regressão por meio das bibliotecas utilizadas.

Na base didática original, com 120 leituras, não foi demonstrada
necessidade de aceleração especializada. O projeto não apresenta
benchmark que comprove ganhos com outro hardware.

2. CPU, GPU, NPU E TPU

CPU: processador de propósito geral, adequado ao controle do programa,
às validações, às consultas e às decisões condicionais do protótipo.

GPU: possui recursos para executar muitas operações em paralelo.
Poderia ser avaliada em simulações numerosas ou cálculos matriciais
de maior escala, com bibliotecas compatíveis.

NPU: unidade especializada em operações de redes neurais, utilizada
também em dispositivos locais. Seria uma possibilidade para uma
evolução com inferência neural compatível.

TPU: acelerador especializado em operações matriciais e tensoriais
de aprendizado de máquina. Não é utilizado pela regressão atual.

Os agentes do SIFSM são funções por regras. A existência de agentes
não implica execução de redes neurais ou necessidade de aceleradores.

3. PARALELISMO E COMPUTAÇÃO HETEROGÊNEA

Cenários independentes de consumo poderiam ser calculados em paralelo.
O mesmo vale para experimentos de modelos por módulo da colônia.

Na evolução para uma arquitetura heterogênea, a CPU poderia manter
a coordenação, enquanto cálculos compatíveis seriam encaminhados
a um acelerador.

Essa distribuição é conceitual. O código atual não implementa
distribuição explícita entre CPU, GPU, NPU e TPU.

A criação de processos e a transferência de dados têm custo.
Em uma base pequena, esse custo pode superar o benefício.

4. HIERARQUIA DE MEMÓRIA E MOVIMENTAÇÃO DE DADOS

O CSV e o banco SQLite ficam em armazenamento persistente.
Ao consultar registros, o programa cria listas e DataFrames em RAM.
Durante o processamento, o hardware utiliza registradores e caches
para manter instruções e dados próximos das unidades de execução.

A capacidade e a velocidade desses níveis são diferentes.
A largura de banda limita o volume transferido por unidade de tempo;
a latência representa o tempo de espera para um acesso.

Em uma base maior, carregar todo o histórico e criar cópias repetidas
poderia aumentar consumo de RAM e tempo de processamento.

Filtros, seleção de colunas, índices adequados e processamento em
lotes seriam alternativas a avaliar.

5. GARGALOS CONECTADOS AO PROTÓTIPO

O assistente ajusta novamente a regressão a cada pedido de estimativa.
Uma evolução poderia reutilizar um modelo validado e atualizá-lo
quando a base mudasse, mantendo controle de versão.

A geração de gráficos e a conversão das consultas em DataFrames
também devem ser medidas antes de definir otimizações.

Em uma arquitetura com acelerador, transportar matrizes entre
memórias poderia limitar o ganho obtido nos cálculos.

6. CHIPLETS E ARQUITETURAS MODERNAS

Chiplets permitem reunir diferentes dies em um encapsulamento.
Integração heterogênea e memórias de alta largura de banda são
estratégias discutidas para aproximar processamento e dados.

Esses conceitos ajudam a explicar arquiteturas modernas, mas
não representam funcionalidades implementadas no SIFSM.

7. EFICIÊNCIA COMPUTACIONAL E SUSTENTABILIDADE

Evitar treinos repetidos, cópias desnecessárias e consultas excessivas
pode diminuir o trabalho computacional.

Entretanto, menor tempo de execução não comprova, isoladamente,
menor consumo total de energia.

Uma avaliação deveria medir tempo, memória, energia por análise
e custo do equipamento, considerando a mesma tarefa.

O protótipo não mediu emissões nem economia elétrica do computador.
A simulação energética da colônia não mede a energia consumida
pelo software que executa essa simulação.
""")


def exibir_sustentabilidade() -> None:
    """Relaciona o protótipo ao item 5.8 e aos capítulos 11, 13 e ESG."""
    print("""1. INTEGRAÇÃO DAS CAMADAS DO SISTEMA

O capítulo 11 apresenta camadas física, de controle e coordenação,
e analítica e de planejamento.

No SIFSM, módulos, sensores e bateria representam conceitualmente
a camada física. As leituras são simuladas; não há equipamento
físico conectado.

As regras booleanas representam parte da lógica de controle:
identificam consumo elevado e bloqueiam decisões sobre sensor
inválido. Não existe atuação física automática.

Simulação, regressão e gráficos compõem a camada analítica.
Os agentes consultam ferramentas e apresentam explicações.

Essa integração permite discutir os recursos como um sistema,
considerando qualidade dos dados e dependências entre módulos.

2. PREVENÇÃO DE DESPERDÍCIOS POR SIMULAÇÃO

A comparação de cenários aplica uma redução hipotética de 15%
somente aos módulos classificados como não essenciais.

Os dados originais são preservados. A economia calculada em Wh
representa uma hipótese, não uma redução realmente alcançada.

A classificação não essencial não autoriza desligamento:
é necessário avaliar impactos sobre pesquisa, alimentação,
armazenamento e necessidades da tripulação.

3. ARMAZENAMENTO, REDES INTELIGENTES E RESILIÊNCIA

A simulação da bateria apresenta estado de carga e energia
não atendida quando os recursos disponíveis se esgotam.

Isso apoia a discussão sobre geração, armazenamento, demanda
e contingências para uma comunidade isolada.

Uma evolução poderia considerar geração variável, perdas,
redundância e coordenação de cargas em uma microrrede.

O protótipo não implementa uma rede inteligente, controle de tensão
ou despacho real de energia. Sua bateria é idealizada.

4. CIDADANIA DIGITAL, PRIVACIDADE E TRANSPARÊNCIA

A base didática utiliza dados sintéticos. Os usuários devem saber
quais dados são consultados, como os indicadores são calculados
e quais limitações existem.

O histórico dos agentes permanece em memória e possui limite.
Isso reduz retenção, mas não substitui proteção de dados.

Uma aplicação real precisaria definir finalidade, acesso,
retenção e proteção dos registros. O SQLite local, sozinho,
não oferece uma política completa de segurança.

5. ECONOMIA DOS DADOS E RISCOS DE VIGILÂNCIA

Leituras associadas a pessoas poderiam revelar presença, rotina
e necessidades da tripulação.

Uma evolução deve evitar identificação desnecessária e impedir
uso dos registros para vigilância ou discriminação.

O envio a serviços externos de IA exigiria avaliar quais dados
são necessários e quais informações poderiam ser expostas.

6. IMPACTO AMBIENTAL DA COMPUTAÇÃO E DA IA

O fluxo atual funciona sem chamadas obrigatórias a um LLM remoto.
Ainda assim, computadores, armazenamento e infraestrutura digital
consomem energia e materiais.

Uma integração com serviços de IA também envolveria processamento
em data centers e movimentação de dados.

Não foi realizada avaliação de ciclo de vida ou medição de emissões.
Portanto, não se declara impacto zero nem superioridade ambiental
comprovada da execução local.

7. INOVAÇÃO RESPONSÁVEL E GOVERNANÇA

A avaliação compara a regressão com uma referência simples.
Se o modelo não a supera, essa limitação deve ser apresentada.

Os agentes consultam e explicam. Não autorizam intervenções
e não operam equipamentos. Guardrails por palavras-chave
podem falhar e não garantem segurança completa.

Decisões críticas exigem revisão humana, critérios transparentes
e definição de responsabilidade.

Na perspectiva ESG:
- Ambiental: acompanhar recursos e comparar cenários de consumo.
- Social: preservar necessidades, inclusão e bem-estar da tripulação.
- Governança: documentar critérios, resultados e responsabilidades.

Esses pontos são uma aplicação didática dos princípios ESG,
não uma certificação de sustentabilidade do sistema.

8. DIVERSIDADE, INCLUSÃO E AUTONOMIA HUMANA

As mensagens devem ser claras, com unidades e explicações,
sem depender apenas de cores.

O menu precisa ser avaliado com leitores de tela e pessoas
com diferentes níveis de experiência.

Prioridades de atendimento devem considerar urgência e necessidades,
com possibilidade de revisão, evitando critérios discriminatórios.

A automação deve apoiar a equipe e sua formação, preservando
capacidade de decisão e procedimentos de contingência.
""")


def exibir_analise_final(resultados: dict | None = None) -> None:
    """Interpreta resultados da opção A sem assumir valores fixos."""
    print("\nANÁLISE FINAL DO SIFSM")
    print("=" * 70)

    if resultados is None:
        print("Resultados não recebidos. Execute a análise integrada.")
    else:
        # Contrato: a opção A envia avaliações, simulação e modelo.
        avaliacoes = resultados.get("avaliacoes")
        simulacao = resultados.get("simulacao")
        modelo = resultados.get("modelo")

        if avaliacoes is not None:
            contagens = {
                "bloqueado": 0,
                "alto": 0,
                "medio": 0,
                "baixo": 0,
            }

            for avaliacao in avaliacoes:
                risco = avaliacao["risco"]
                contagens[risco] += 1

            print("\nRISCO DAS ÚLTIMAS LEITURAS")
            for risco, quantidade in contagens.items():
                print(f" - {risco}: {quantidade} módulo(s)")

            print("A classificação não representa todo o histórico.")

            if contagens["bloqueado"]:
                print("Prioridade: verificar sensores bloqueados.")
            if contagens["alto"]:
                print("Solicitar revisão dos módulos essenciais em alerta.")
            if contagens["medio"]:
                print("Avaliar consumo e dependências dos demais módulos.")

        if simulacao is not None:
            atual = simulacao["atual"]
            energia = atual["energia_wh"]
            economia = simulacao["economia_wh"]
            deficit = simulacao["bateria"]["deficit_wh"][-1]

            print("\nENERGIA E ARMAZENAMENTO")
            print(f" - Horizonte: {atual['duracao_h']:.1f} h")
            print(f" - Energia original: {energia / 1000:.2f} kWh")
            print(f" - Economia hipotética: {economia / 1000:.2f} kWh")

            if energia > 0:
                print(f" - Redução relativa: {100 * economia / energia:.2f}%")

            print(f" - Energia não atendida: {deficit / 1000:.2f} kWh")

            if deficit > 0:
                print("Revisar geração, armazenamento ou demanda.")
            else:
                print("Não houve déficit no cenário simulado.")
                print("Isso não garante autonomia em outras condições.")

            print("Os módulos essenciais preservam o consumo original.")
        else:
            print("\nSimulação indisponível nesta execução.")

        if modelo is not None:
            print("\nAVALIAÇÃO DO MODELO")
            print(f" - MAE: {modelo['mae']:.2f} W")
            print(f" - RMSE: {modelo['rmse']:.2f} W")
            print(f" - R²: {modelo['r2']:.3f}")
            print(f" - MAE da referência: {modelo['mae_baseline']:.2f} W")

            if modelo["mae"] >= modelo["mae_baseline"]:
                print("A regressão não superou a referência em MAE.")
                print("Não há vantagem demonstrada nessa métrica.")
            else:
                print("A regressão superou a referência neste teste.")
                print("Ainda é necessária validação com outros dados.")

            print("R² não é porcentagem de acertos.")
        else:
            print("\nModelo indisponível nesta execução.")

    print("""
LIMITAÇÕES E MELHORIAS
----------------------------------------------------------------------
- Os dados são sintéticos e não validam operação real.
- A integração aproxima a potência por segmentos de reta.
- A bateria não considera perdas ou envelhecimento.
- A simulação mantém leituras em falha como valores hipotéticos.
- A regressão pode ser afetada por picos e diferenças entre módulos.
- Os agentes possuem compreensão limitada a regras e palavras-chave.
- Não foram medidos consumo computacional ou emissões.

Melhorias propostas:
- Ampliar dados representativos e validar sensores.
- Definir uma política para falhas e lacunas nas medições.
- Avaliar modelos por módulo e referências alternativas.
- Incluir geração variável e perdas no armazenamento.
- Reutilizar modelos validados quando os dados não mudarem.
- Avaliar acessibilidade, controle de acesso e retenção.

RESPONSABILIDADE
----------------------------------------------------------------------
Economia simulada não equivale a benefício ambiental comprovado.
Os resultados apoiam planejamento e discussão técnica.
Toda intervenção exige validação humana.
""")