# 🚀 Missão Aurora Siger - Sistema de Telemetria e Decisão de Voo

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Status](https://img.shields.io/badge/status-Concluído-green.svg)

Este repositório contém a documentação e o protótipo do sistema de telemetria da nave **Aurora**. O projeto integra conceitos de Ciência da Computação, Engenharia de Foguetes e Meteorologia para validar a segurança de janelas de lançamento aeroespacial.

O projeto culmina em um script Python que atua como uma camada de Inteligência de Voo, automatizando a decisão de Lançar ou Abortar com base em telemetria simulada e regras de negócio, considerando não apenas aspectos técnicos, mas também custo e impacto social da exploração espacial. 

<br>


## 📋 Visão Geral
Este repositório contém:

* Um protótipo de simulação de telemetria com regras de segurança.

* Um módulo de análise com IA (Gemini) que age como um “Diretor de Voo” virtual.

* Um dashboard interativo (WIP) com Streamlit para futuras visualizações em tempo real.

<br>

## 🎯 Objetivos do Projeto
* **Simulação de telemetria:** Geração de dados aleatórios para parâmetros críticos do foguete (temperatura, pressão, energia, integridade, módulos críticos).
* **Verificação de segurança:** Execução de uma sequência de 3 testes pré-lançamento, validando a telemetria contra regras de negócio pré-definidas.
* **Relatórios detalhados no console:** Exibição de relatórios claros para cada rodada, indicando sucesso ou falhas e listando as anomalias detectadas.
* **Análise com IA (Gemini):** Em caso de falha, chamada à API do Gemini para gerar um relatório técnico estruturado, explicando as anomalias e sugerindo ações para a equipe de engenharia.
* **Dashboard Interativo (WIP):** Protótipo de interface em Streamlit para visualização de telemetria e resultados dos testes em tempo quase real.

<br>

### **Parâmetros Monitorados**
Durante a simulação, a camada de telemetria monitora:
* **🌡️ Temperatura:** interna e externa da nave.
* **🏗️ Estrutural:** status de integridade da fuselagem e célula da nave.
* **⚡Energia:** capacidade e carga disponível (%) para sistemas essenciais.
* **🎈 Pressão:** monitoramento dos tanques (faixa operacional segura).
* **💻 Módulos Críticos:** status dos sistemas essenciais de bordo.

<br>

## ⚖️ Regras de Negócio de Segurança
Para que a decolagem seja autorizada, todos os critérios abaixo devem ser satisfeitos em 3 rodadas consecutivas:
* **Integridade Estrutural:** deve ser 1 (Operacional).
* **Energia:** mínimo de 80% para decolagem segura.
* **Pressão:** entre 300 e 450 psi.
* **Temperatura Interna:** entre 18°C e 25°C.
* **Módulos Críticos:** todos com status "OK".

Se qualquer uma dessas condições falhar em uma rodada, o teste é marcado como FALHA, e a missão é abortada ao final da sequência, com emissão de relatório técnico da IA.

<br>

### 🚀 Exemplo de Saída no Console
<details>
<summary>Clique para ver um exemplo de relatório em caso de falha nas três rodadas de teste</summary>

```text
Sejam bem-vindos ao sistema de telemetria da Missão Aurora!
Iniciando sequência de 3 testes obrigatórios...

-----------------------------------------------------------------
|                    RELATÓRIO DE RODADA: 1/3                   |
|                                                               |
| TESTE FALHOU                                                  |
| Rodada 1: Anomalias detectadas.                               |
| ------------------------------------------------------------- |
| ERROS ENCONTRADOS:                                            |
| - Energia insuficiente: 25.78% (Min: 80%)                     |
| - Pressão fora dos padrões: 510.68 psi                        |
| - FALHA NOS MÓDULOS CRÍTICOS                                  |
|                                                               |
-----------------------------------------------------------------
-----------------------------------------------------------------
|                    RELATÓRIO DE RODADA: 2/3                   |
|                                                               |
| TESTE FALHOU                                                  |
| Rodada 2: Anomalias detectadas.                               |
| ------------------------------------------------------------- |
| ERROS ENCONTRADOS:                                            |
| - FALHA NA INTEGRIDADE ESTRUTURAL                             |
| - Temperatura interna fora do padrão: 16.84 C°                |
| - FALHA NOS MÓDULOS CRÍTICOS                                  |
|                                                               |
-----------------------------------------------------------------
-----------------------------------------------------------------
|                    RELATÓRIO DE RODADA: 3/3                   |
|                                                               |
| TESTE FALHOU                                                  |
| Rodada 3: Anomalias detectadas.                               |
| ------------------------------------------------------------- |
| ERROS ENCONTRADOS:                                            |
| - Energia insuficiente: 22.57% (Min: 80%)                     |
| - Pressão fora dos padrões: 498.31 psi                        |
| - Temperatura interna fora do padrão: 10.09 C°                |
|                                                               |
-----------------------------------------------------------------

=================================================================
RESUMO FINAL: 0 Sucessos | 3 Falhas
>>> STATUS FINAL: DECOLAGEM ABORTADA! ❌
A missão requer 3 sucessos consecutivos. Detectamos 3 falha(s).
21:53:3 - A equipe de engenharia está investigando as falhas.

--- ANÁLISE DO DIRETOR DE VOO (IA) ---
Conectando aos servidores de IA...

**RELATÓRIO DE ENGENHARIA DE VOO: MISSÃO AURORA**
**PARA:** Comando de Missão / Equipe de Operações
**ASSUNTO:** Análise Técnica de Abortagem de Lançamento (Status: NO-GO)

Após a falha em três rodadas consecutivas de testes pré-voo, o lançamento do foguete Aurora foi abortado. Abaixo, apresento a análise técnica das anomalias e as diretrizes para investigação imediata.

### 1. Análise das Anomalias Técnicas

*   **Déficit Energético Crítico (22.57% e 25.78% / Min: 80%):** O sistema opera com menos de um terço da carga nominal necessária. Sem energia suficiente, os aviônicos, sistemas de suporte à vida e atuadores hidráulicos não podem manter a estabilidade durante a ascensão. É um risco iminente de perda total de telemetria e controle.
*   **Instabilidade de Pressão (498.31 psi e 510.68 psi):** As leituras indicam que o sistema pneumático ou de propelentes está fora do envelope operacional. Pressões fora do padrão sugerem vazamentos ou falhas em válvulas reguladoras, o que pode levar à cavitação de bombas ou, em caso extremo, à explosão do tanque.
*   **Anomalias Térmicas (10.09 °C e 16.84 °C):** Temperaturas fora da janela operacional indicam falha no Sistema de Controle Ambiental (ECS) ou no isolamento térmico. Isso compromete a viscosidade de fluidos e a integridade de semicondutores sensíveis.
*   **Falha de Integridade Estrutural e Módulos Críticos:** Este é o ponto de maior gravidade. O diagnóstico de falha estrutural indica fadiga de material, fissuras ou falhas de fixação na célula do foguete. Combinado com a falha em módulos críticos (computadores de bordo ou sistemas de navegação), o veículo sofreria desintegração catastrófica sob as cargas dinâmicas do *Max-Q* (máxima pressão dinâmica).

### 2. Justificativa para o Aborto
O lançamento nestas condições resultaria em falha catastrófica em T+ poucos segundos. A combinação de energia insuficiente para redundância e integridade estrutural comprometida torna o veículo incapaz de suportar o estresse aerodinâmico e as necessidades de processamento de dados da trajetória.

### 3. Diretrizes para Investigação

A equipe de terra deve iniciar imediatamente os seguintes protocolos de inspeção:

1.  **Sistemas Elétricos:** Diagnóstico completo nas células de combustível e baterias primárias para identificar curto-circuito ou degradação química precoce.
2.  **Sistemas Pneumáticos e Hidráulicos:** Teste de estanqueidade e calibração dos transdutores de pressão para identificar o ponto exato da flutuação.
3.  **Análise Estrutural (NDT):** Realizar ensaios não destrutivos (ultrassom e raio-X) na fuselagem e nas interfaces dos módulos críticos para localizar falhas na liga metálica ou compósitos.
4.  **Revisão de Software e Barramentos:** Investigar o barramento de dados para entender se as "falhas em módulos críticos" são falhas de hardware ou erros de paridade na comunicação lógica.

**Conclusão:** O veículo Aurora permanece em solo por tempo indeterminado até que a redundância de 80% de energia seja restabelecida e a integridade estrutural seja certificada.

**Engenheiro de Voo Sênior**
*Setor de Sistemas de Lançamento*
=================================================================
```
</details>

<br>

## 🏗️ Arquitetura e Fluxo de Decisão

Em alto nível, o sistema segue o fluxo:

1. **Geração de telemetria simulada** (valores aleatórios dentro/fora dos limites).

2. **Aplicação das regras de negócio** para cada rodada de teste.

3. **Cálculo do status da missão** (GO / NO-GO) após 3 rodadas.

4. **Em caso de falha**:

    * Registro das anomalias por rodada.

    * Geração de relatório técnico com IA (Gemini).

5. (WIP) Envio/visualização dos dados no **dashboard Streamlit**.

<br>

### 🧭 Fluxo de Decisão da Missão
```mermaid
graph TD
    A([Início da Simulação]) --> B[1. Gerar Telemetria];
    B --> C[2. Aplicar Regras de Negócio];
    C --> D{Parâmetros OK?};
    D -- Não --> E[Registrar Falhas];
    E --> F{Rodada 3/3?};
    D -- Sim --> F;
    F -- Não --> B;
    F -- Sim --> G{3 Rodadas Válidas?};
    G -- Não --> H[Status: DECOLAGEM ABORTADA ❌];
    H --> I[Gerar Relatório com IA];
    I --> K([Fim]);
    G -- Sim --> J[Status: DECOLAGEM AUTORIZADA 🚀];
    J --> K;
```
<br>

## 🛠️ Configuração e Instalação
Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos
- [Python 3.9+](https://www.python.org/downloads/)
- Chave de API do [Google AI Studio (Gemini)](https://aistudio.google.com/app/apikey)
<br>

### Passos para Execução
1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/PBL-Aurora.git
    cd PBL-Aurora
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    O projeto utiliza um arquivo `requirements.txt` para gerenciar as bibliotecas.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    - Crie um arquivo chamado `.env` na raiz do projeto.
    - Adicione sua chave da API do Gemini, como no exemplo abaixo:
    ```
    GEMINI_API_KEY="SUA_CHAVE_DE_API_AQUI"
    ```
    <br>     

### Executando a Simulação

O projeto possui duas saídas principais: uma simulação via console e uma interface web em desenvolvimento.

- **Para rodar a simulação no console:**
  ```bash
  python codigo/main.py
  ```
  Isso irá:
    * Executar os 3 testes de telemetria
    * Exibir os relatórios de cada rodada no terminal 
    * Gerar, em caso de falha, um relatório detalhado via IA (Gemini).

<br>

- **Para iniciar o dashboard web (WIP):**
  ```bash
  streamlit run codigo/main.py
  ```
  Abra seu navegador e acesse `http://localhost:8501` para ver a interface.


<br> 

## 📂 Estrutura do Projeto
```
PBL-Aurora/
├── .env                  # Chave de segurança 
├── .gitignore            # Regras de exclusão do Git
├── requirements.txt      # Dependências do projeto
├── codigo/
│   └── main.py           # código
└── README.md             # Documentação do projeto
```

<br>

## 🌍 Ética, Sustentabilidade e Impacto
Além da parte técnica, a Missão Aurora também aborda a responsabilidade na exploração espacial, incluindo:
* **Lixo Espacial:** riscos de colisão em órbita e importância de estratégias de desórbita programada.
* **Impacto Social:** como tecnologias aeroespaciais apoiam agricultura, monitoramento climático e prevenção de desastres.
* **Ética:** discussão sobre a justificativa da expansão humana para além da Terra frente a problemas globais imediatos.
  
<br>

## 👥 Equipe (FIAP 2026)
| Nome | RM |
| :--- | :--- |
| **Juan de Lucas Frois** | RM563260 |
| **Flávia Roberta Pennachin** | RM561860 |
| **Pedro Valente Toledo** | RM570394 |
| **Bruno Antonio Santos Silva** | RM573180 | 
| **Renan Mano Otero** | RM573615 |

<br>

---
**Instituição:** FIAP\
**Ano:** 2026
