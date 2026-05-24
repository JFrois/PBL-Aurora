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

<br>

## 🎯 Objetivos do Projeto
* **Simulação de telemetria:** Geração de dados aleatórios para parâmetros críticos do foguete (temperatura, pressão, energia, integridade, módulos críticos).
* **Verificação de segurança:** Execução de uma sequência de 3 testes pré-lançamento, validando a telemetria contra regras de negócio pré-definidas.
* **Relatórios detalhados no console:** Exibição de relatórios claros para cada rodada, indicando sucesso ou falhas e listando as anomalias detectadas.
* **Análise com IA (Gemini):** Em caso de falha, chamada à API do Gemini para gerar um relatório técnico estruturado, explicando as anomalias e sugerindo ações para a equipe de engenharia.

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

=====================================================================================
              Sejam bem-vindos ao sistema de telemetria da MISSÃO AURORA             
                   Iniciando sequência de 3 testes obrigatórios...                   
=====================================================================================
-------------------------------------------------------------------------------------
|                              RELATÓRIO DE RODADA: 1/3                             |
|                                                                                   |
| TESTE FALHOU                                                                      |
| Rodada 1: Anomalias detectadas.                                                   |
| -------------------------------------------------------------                     |
| VERIFICAÇÃO DE SEGURANÇA:                                                         |
|   > Bateria Útil p/ Sistema: 3039.19 kWh                                          |
|   > Custo de Decolagem.....: 463.78 kWh                                           |
|   > Autonomia energética pós decolagem...: 67.83%                                 |
|   > Temp. Interna: 13.08 C°                                                       |
|   > Temp. Externa: -7.10 C°                                                       |
|   > Integridade: OK                                                               |
|   > Pressão: 422.22 psi                                                           |
| -----------------------------------------------------------------                 |
| ERROS ENCONTRADOS:                                                                |
| - FALHA NA INTEGRIDADE ESTRUTURAL                                                 |
| - Temperatura interna fora do padrão: 13.08 C°                                    |
| - Temperatura externa fora do padrão: -7.10 C°                                    |
| - FALHA NOS MÓDULOS CRÍTICOS                                                      |
| - RISCO DE BLACKOUT: Saldo de 67.83% (Min: 80%)                                   |
|                                                                                   |
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
|                              RELATÓRIO DE RODADA: 2/3                             |
|                                                                                   |
| TESTE FALHOU                                                                      |
| Rodada 2: Anomalias detectadas.                                                   |
| -------------------------------------------------------------                     |
| VERIFICAÇÃO DE SEGURANÇA:                                                         |
|   > Bateria Útil p/ Sistema: 112.89 kWh                                           |
|   > Custo de Decolagem.....: 396.91 kWh                                           |
|   > Autonomia energética pós decolagem...: 6.28%                                  |
|   > Temp. Interna: 19.40 C°                                                       |
|   > Temp. Externa: 6.11 C°                                                        |
|   > Integridade: OK                                                               |
|   > Pressão: 463.72 psi                                                           |
| -----------------------------------------------------------------                 |
| ERROS ENCONTRADOS:                                                                |
| - FALHA NA INTEGRIDADE ESTRUTURAL                                                 |
| - Pressão fora dos padrões: 463.72 psi                                            |
| - RISCO DE BLACKOUT: Saldo de 6.28% (Min: 80%)                                    |
|                                                                                   |
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
|                              RELATÓRIO DE RODADA: 3/3                             |
|                                                                                   |
| TESTE FALHOU                                                                      |
| Rodada 3: Anomalias detectadas.                                                   |
| -------------------------------------------------------------                     |
| VERIFICAÇÃO DE SEGURANÇA:                                                         |
|   > Bateria Útil p/ Sistema: 1066.13 kWh                                          |
|   > Custo de Decolagem.....: 284.43 kWh                                           |
|   > Autonomia energética pós decolagem...: 45.58%                                 |
|   > Temp. Interna: 16.35 C°                                                       |
|   > Temp. Externa: 18.20 C°                                                       |
|   > Integridade: OK                                                               |
|   > Pressão: 384.69 psi                                                           |
| -----------------------------------------------------------------                 |
| ERROS ENCONTRADOS:                                                                |
| - FALHA NA INTEGRIDADE ESTRUTURAL                                                 |
| - Temperatura interna fora do padrão: 16.35 C°                                    |
| - FALHA NOS MÓDULOS CRÍTICOS                                                      |
| - RISCO DE BLACKOUT: Saldo de 45.58% (Min: 80%)                                   |
|                                                                                   |
-------------------------------------------------------------------------------------
=================================================================
RELATÓRIO DE RODADA: 0 Sucessos | 3 Falhas
STATUS: ABORTAR MISSÃO! Verifique os erros acima. 🛑

>>> STATUS FINAL: DECOLAGEM ABORTADA! ❌
A missão requer 3 sucessos consecutivos. Detectamos 3 falha(s).
18:35:44 - A equipe de engenharia está investigando as falhas.

--- ANÁLISE DO DIRETOR DE VOO (IA) ---
**BOLETIM TÉCNICO DE DIAGNÓSTICO – ABORTO DE LANÇAMENTO DA MISSÃO AURORA**

**CLASSIFICAÇÃO DOS DADOS:**

1.  **Integridade Estrutural/Mecânica:**
    *   FALHA NA INTEGRIDADE ESTRUTURAL
    *   Pressão fora dos padrões: 463.72 psi (Indica falha em sistema pressurizado ou vedação)
2.  **Sistemas Críticos/Funcionais:**
    *   FALHA NOS MÓDULOS CRÍTICOS
3.  **Subsistema Elétrico/Energia:**
    *   RISCO DE BLACKOUT: Saldo de 45.58% (Min: 80%)
    *   RISCO DE BLACKOUT: Saldo de 6.28% (Min: 80%)
    *   RISCO DE BLACKOUT: Saldo de 67.83% (Min: 80%)
4.  **Condições Ambientais/Térmicas:**
    *   Temperatura externa fora do padrão: -7.10 C°
    *   Temperatura interna fora do padrão: 13.08 C°
    *   Temperatura interna fora do padrão: 16.35 C°

---

**BOLETIM TÉCNICO DE DIAGNÓSTICO**

**STATUS:**
O lançamento da Missão Aurora foi imediatamente abortado. As verificações pré-lançamento indicaram falhas críticas em 3 de 3 testes, confirmando uma condição NO-GO.

**RISCO:**
O conjunto de anomalias registradas, isoladamente e em conjunto, cria um cenário de risco inaceitável de perda do veículo e da missão.
*   **Falha na Integridade Estrutural e Pressão Anormal:** Indica comprometimento físico da estrutura do veículo ou de seus subsistemas de propulsão/pressurização. Este cenário representa um risco iminente de desintegração catastrófica, explosão ou falha estrutural durante as fases de maior estresse dinâmico do voo, culminando na perda total do veículo e da carga útil.
*   **Falha nos Módulos Críticos:** Aponta para a inoperância ou desempenho degradado de componentes essenciais para controle de voo, navegação, telemetria, sistemas de segurança ou propulsão. A falha de qualquer um desses módulos pode levar à perda de controle da trajetória, incapacidade de executar comandos, falha na separação de estágios ou impossibilidade de abortar a missão de forma segura, resultando na perda do veículo.
*   **Múltiplos Riscos de Blackout:** Com saldos de energia muito abaixo do mínimo operacional exigido (45.58%, 6.28%, 67.83% frente a 80%), este é um indicativo claro de uma falha sistêmica e crítica no subsistema elétrico. A incapacidade de sustentar a alimentação de energia levaria à paralisação de todos os sistemas aviônicos e de suporte à vida a bordo, resultando em perda completa de controle, comunicação e, consequentemente, a perda do veículo em qualquer fase do voo.
*   **Temperaturas Internas e Externas Fora do Padrão:** Sugerem um ambiente operacional inadequado para os equipamentos. Temperaturas extremas podem causar falha eletrônica por superaquecimento ou congelamento, degradação de materiais, comprometimento da lubrificação de componentes mecânicos ou falha de isolamento, afetando diretamente a funcionalidade e estabilidade do veículo. A temperatura externa anormal também pode indicar condições climáticas impróprias ou falha nos sistemas de controle térmico do veículo.

**AÇÃO:**
1.  **Engenharia de Hardware:** Foco imediato na inspeção detalhada e diagnóstica das falhas estruturais, dos módulos críticos e do subsistema de pressurização/propulsão. Uma análise aprofundada da arquitetura elétrica e das baterias é imperativa para identificar a raiz dos múltiplos riscos de blackout. É crucial verificar os sensores e sistemas de controle térmico, bem como as condições ambientais da plataforma de lançamento.
2.  **Engenharia de Software:** Auditoria completa dos algoritmos de monitoramento e telemetria para garantir a precisão e robustez dos dados reportados. Revisão dos parâmetros de pré-lançamento e protocolos de verificação para identificar possíveis lacunas que permitiram a progressão a um estado de falha tão crítico. Desenvolver e testar atualizações de software para incorporar novas lógicas de detecção e mitigação baseadas nas descobertas de hardware.
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

# REFLEXÃO CRÍTICA: MISSÃO AURORA
A exploração espacial é o reflexo dos valores da humanidade. Na Missão Aurora, a telemetria não apenas monitora máquinas, mas protege vidas e fundamenta uma presença humana ética e consciente.

### ⚖️ Ética e Responsabilidade
A exploração espacial não é uma fuga dos problemas terrestres, mas uma busca por soluções globais. O espaço deve ser um bem comum, focado na ciência e na cooperação, evitando a militarização e garantindo que o progresso tecnológico beneficie toda a sociedade, não apenas grupos restritos.

### 🛰️ Sustentabilidade e Lixo Espacial
A órbita terrestre é um recurso finito. Para evitar o Efeito Kessler (colisões em cadeia), a missão adota protocolos de Desórbita Programada: cada componente possui um fim de ciclo planejado, garantindo que a "estrada espacial" permaneça limpa e segura para as futuras gerações.

### 🤝 Impacto Social do Lançamento Tripulado
Enviar seres humanos ao espaço gera transformações profundas na estrutura social:

* Inspiração STEM: O "Efeito Apollo" atrai jovens para carreiras científicas e quebra barreiras sociais através da representatividade.

* Diplomacia Global: A manutenção da vida em órbita exige cooperação internacional, promovendo o diálogo e reforçando a identidade planetária (Overview Effect).

* Avanços na Medicina: A telemetria e o suporte à vida impulsionam a telemedicina, cirurgias robóticas e tratamentos de perda óssea/muscular para idosos na Terra.

* Cultura de Segurança: Os rigorosos protocolos de falha zero e as tecnologias de reciclagem de recursos (água e ar) são aplicados hoje em indústrias críticas e na gestão de desastres ambientais.
--- 
**Conclusão:** Decolar exige mais que combustível; exige o compromisso de proteger quem parte, quem fica e o ambiente que nos cerca.

## 🚀 Fase 2: Módulo de Gestão de Pouso e Estabilização da Base (MGPEB)
<details>
<summary>Clique para ver a fase 2:</summary>

Esta fase é responsável por gerenciar o tráfego orbital e a autorização de descida dos módulos na base Aurora Singer em Marte, utilizando estruturas de dados lineares fundamentais, algoritmos de busca/ordenação e lógica booleana estrita para mitigar riscos de colisão e falhas catastróficas.

### 📐 1. Estruturas de Dados Utilizadas
O sistema gerencia os módulos (representados como dicionários) utilizando três conceitos de estruturas de dados lineares:
* **Fila de Pouso (`Queue` - FIFO):** Garante a regra de que o primeiro módulo a chegar/solicitar a descida seja o primeiro a ser processado (`pop(0)`).
* **Listas de Histórico (`List`):** Utilizadas para catalogar o destino final das entidades, divididas entre `lista_pousados` (sucesso na superfície) e `lista_espera` (módulos retidos em órbita por contingência).
* **Pilha de Alertas (`Stack` - LIFO):** Registra as anomalias climáticas e operacionais mais recentes no topo da pilha, garantindo que o último erro inserido seja o primeiro a ser exibido e tratado pelo painel (`pop()`).

### ⚡ 2. Algoritmos Implementados
Para processar e otimizar a fila de pouso, foram desenvolvidos dois algoritmos nativos (sem o uso de bibliotecas externas):
* **Busca Sequencial:** Varre a fila de pouso de forma linear para identificar instantaneamente qual módulo possui o menor nível crítico de combustível.
* **Insertion Sort (Ordenação por Inserção):** Reordena dinamicamente a fila com base na prioridade numérica do módulo (onde a prioridade 1 representa maior urgência), garantindo que os módulos de suporte médico e energético passem à frente.

### 🧠 3. Portas Lógicas e Regras de Decisão
A autorização final para o pouso de cada módulo exige uma validação booleana composta através de operadores lógicos estritos:
1. **Regra de Sucesso Primária (`AND` Estrito):** O pouso só é executado com sucesso se:
   $$\text{combustivel\_ok} \land \text{sensores\_ok} \land \text{clima\_ok} \land \text{area\_livre}$$
2. **Regra de Contingência Energética:** Se um módulo apresentar combustível crítico ($\le 15\%$) mas não possuir prioridade alta, o sistema intercepta a entidade, eleva sua prioridade e reordena a fila.
3. **Regra de Retenção por Clima e Sensores:** Se o radar acusar clima adverso **E** os sensores do módulo estiverem em falha, o pouso é negado imediatamente e o evento é enviado para o topo da pilha de alertas.

### ⚙️ Exemplo de Entrada e Saída (Telemetria Simulada)
* **Entrada na Fila:** Módulos `MOD-MED-01` (Prioridade 1), `MOD-ENE-01` (Prioridade 2), `MOD-HAB-01` (Prioridade 3), `MOD-LOG-01` (Prioridade 4), `MOD-LAB-01` (Prioridade 5).
* **Saída no Terminal (Log de Operação):**
```
=====================================================================================
               INICIANDO FASE 2: APROXIMAÇÃO A MARTE E POUSO DE MÓDULOS              
=====================================================================================

Módulo com menor combustível detectado: MOD-LAB-01 (10.9%)

Fila de pouso configurada e ordenada por prioridade.

--- INICIANDO PROTOCOLO DE POUSO ---

[Analisando] MOD-MED-01 (Prioridade 1 | Combustível: 77.6%)
   -> RADAR METEOROLÓGICO: Detectado(s) Cisalhamento de Vento!
   -> FALHA: Pouso negado.
      Motivo: Condição atmosférica adversa. Entrando em espera.

[Analisando] MOD-ENE-01 (Prioridade 2 | Combustível: 39.9%)
   -> RADAR METEOROLÓGICO: Detectado(s) Tempestade de Areia, Frio Extremo Inesperado!
   -> ALERTA MÁXIMO: Falha de Sensores + Clima Adverso (Tempestade de Areia) no módulo MOD-ENE-01

[Analisando] MOD-HAB-01 (Prioridade 3 | Combustível: 31.1%)
   -> RADAR METEOROLÓGICO: Detectado(s) Tempestade de Areia, Cisalhamento de Vento!
   -> FALHA: Pouso negado.
      Motivo: Condição atmosférica adversa. Entrando em espera.

[Analisando] MOD-LOG-01 (Prioridade 4 | Combustível: 25.8%)
   -> SUCESSO: Pouso autorizado.

[Analisando] MOD-LAB-01 (Prioridade 5 | Combustível: 10.9%)
   -> RADAR METEOROLÓGICO: Detectado(s) Tempestade de Areia!
   -> ALERTA: Combustível crítico! Reavaliando prioridade.

[Analisando] MOD-LAB-01 (Prioridade 1 | Combustível: 10.9%)
   -> RADAR METEOROLÓGICO: Detectado(s) Tempestade de Areia, Frio Extremo Inesperado, Cisalhamento de Vento!
   -> FALHA: Pouso negado.
      Motivo: Condição atmosférica adversa. Entrando em espera.


-------------------------------------------------------------------------------------
|                        RELATÓRIO FINAL DE OPERAÇÃO - MGPEB                        |
|                                                                                   |
| Módulos Pousados (1):                                                             |
|   [+] MOD-LOG-01                                                                  |
|                                                                                   |
| Módulos em Espera (4):                                                            |
|   [-] MOD-MED-01                                                                  |
|   [-] MOD-ENE-01                                                                  |
|   [-] MOD-HAB-01                                                                  |
|   [-] MOD-LAB-01                                                                  |
|                                                                                   |
| Alertas Críticos na Pilha (2):                                                    |
|   (!) Alerta de Combustível: MOD-LAB-01                                           |
|   (!) ALERTA MÁXIMO: Falha de Sensores + Clima Adverso (Tempestade de Areia) no módulo MOD-ENE-01 |
|                                                                                   |
-------------------------------------------------------------------------------------

--- ANÁLISE DO DIRETOR DE VOO (IA FASE 2) ---
Boletim Técnico de Diagnóstico – Missão Aurora – Pouso Fase 2

Fase 2: MOD-LOG-01 pousado com sucesso. MOD-MED-01, MOD-ENE-01, MOD-HAB-01, MOD-LAB-01 retidos em órbita.
MOD-ENE-01 apresenta ALERTA MÁXIMO (falha de sensores + tempestade de areia), inviabilizando pouso seguro.
MOD-LAB-01 com Alerta de Combustível crítico, comprometendo manobras e permanência orbital.
Ação imediata: Priorizar diagnóstico detalhado de MOD-ENE-01 (órbita/superfície) e MOD-LAB-01 (propelente).
Reavaliar perfis de reentrada dos demais módulos e janelas de pouso conforme dados atualizados.
=====================================================================================

```
</details>

---
## 🌌 Fase 3: Sistema de Funcionamento Inteligente da Colônia
<details>
<summary>Clique para ver a fase 3 em detalhe:</summary><br>

Este módulo unifica o processamento de dados e tomada de decisão para garantir a sobrevivência e a estabilidade energética da colônia Aurora Prime.

### ⚙️ Exemplo de Entrada e Saída (Validação do Sistema)

#### 1. Módulo de Decisão Condicional
* **Entrada:** `bateria_nivel_pct = 40`, `consumo_total = 80` (Suporte de vida + Sistemas não essenciais ligados).
* **Saída:** `"ALERTA: Energia < 50% e Consumo Alto. Modo Economia ATIVADO! Desligando sistemas não essenciais."`

#### 2. Módulo de Previsão Climática (Regressão Linear)
* **Entrada (Histórico):** Vento: `[8, 10, 12]` | Geração: `[20, 25, 30]` -> **Nova entrada:** `vento = 11`
* **Saída:** `Previsão de energia ≈ 27.5 kWh`

#### 3. Módulo de Eficiência Energética
* **Entrada:** `geracao_total = 70W`, `consumo_total = 35W` (Após o corte automático do módulo não essencial).
* **Saída:** `"SUGESTÃO: Geração total (70W) maior que o Consumo (35W). Armazenar energia excedente."`
<br>
## Exemplo saída terminal:

```
=====================================================================================
                     INICIANDO SISTEMA INTEGRADO DA MISSÃO AURORA                    
=====================================================================================

=====================================================================================
                    INICIANDO FASE 1: TELEMETRIA E PRÉ-DESCOLAGEM                    
=====================================================================================
-------------------------------------------------------------------------------------
|                                RODADA 1/3 - SUCESSO                               |
|                                                                                   |
| Parâmetros nominais.                                                              |
|                                                                                   |
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
|                                RODADA 2/3 - SUCESSO                               |
|                                                                                   |
| Parâmetros nominais.                                                              |
|                                                                                   |
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
|                                RODADA 3/3 - SUCESSO                               |
|                                                                                   |
| Parâmetros nominais.                                                              |
|                                                                                   |
-------------------------------------------------------------------------------------

=====================================================================================
                    INICIANDO FASE 2: APROXIMAÇÃO E POUSO (MGPEB)                    
=====================================================================================

--- INICIANDO PROTOCOLO DE POUSO ---
[+] MOD-MED-01 pousou com sucesso.
[+] MOD-ENE-01 pousou com sucesso.
[-] MOD-HAB-01 retido em órbita.
[-] MOD-LOG-01 retido em órbita.
[+] MOD-LAB-01 pousou com sucesso.

=====================================================================================
                   INICIANDO FASE 3: SISTEMA INTELIGENTE DA COLÓNIA                  
=====================================================================================

=====================================================================================
                       PROCESSAMENTO DE DADOS E AUDITORIA (IA)                       
=====================================================================================
>> Extraindo correlações e gerando contexto analítico profundo...
>> Sintetizando Boletim Executivo Estruturado...

Prezados membros da equipe de Missão Aurora,

Com a máxima seriedade e empenho na segurança e sucesso de nossa empreitada, apresento o boletim operacional consolidado, com base na análise técnica detalhada recebida. Nossa missão enfrenta desafios críticos que exigem atenção e ação imediatas.

INICIANDO FASE 1: TELEMETRIA E PRÉ-DESCOLAGEM
-> A Fase 1, compreendendo as operações de telemetria e pré-descolagem, foi executada com sucesso pleno, conforme os parâmetros de missão. O status "GO" foi confirmado sem o registro de falhas operacionais ou anomalias detectadas em qualquer subsistema. Os logs brutos confirmam a ausência de erros de telemetria, garantindo a integridade dos dados e a conformidade com a linha de base planejada. Concluímos esta fase sem indícios de quaisquer eventos que pudessem ter impactado negativamente as fases subsequentes, refletindo a excelência da engenharia e das equipes de lançamento.

INICIANDO FASE 2: APROXIMAÇÃO E POUSO (MGPEB)
-> A Fase 2 de Aproximação e Pouso (MGPEB) representa o primeiro desvio crítico em relação ao plano de missão. Embora tenhamos obtido sucesso no pouso dos módulos Médico (MOD-MED-01), Energia (MOD-ENE-01) e Laboratório (MOD-LAB-01), o gerenciamento de pouso falhou para dois módulos de importância vital: Habitação (MOD-HAB-01) e Logística (MOD-LOG-01). Estes módulos foram retidos na órbita de espera devido a anomalias não especificadas, o que impõe uma revisão urgente do processo decisório e dos critérios de prontidão para desdobramento. A eficiência da ordenação da fila, neste contexto, foi comprometida pela incapacidade de se proceder com o pouso dos módulos críticos. Os riscos operacionais advindos da retenção desses módulos são severos e sistêmicos: a ausência do MOD-HAB-01 degrada drasticamente nossa capacidade de sustentação de vida e acomodação da tripulação no solo, forçando uma dependência precária de abrigos temporários. Igualmente, a retenção do MOD-LOG-01 compromete a gestão de recursos, a capacidade de manutenção, o reabastecimento e a recuperação de falhas, elevando exponencialmente a vulnerabilidade da colônia a longo prazo e a exaustão de suprimentos essenciais.

INICIANDO FASE 3: SISTEMA INTELIGENTE DA COLÓNIA
-> A Fase 3, referente às Operações Iniciais da Colônia e ao Sistema Inteligente, apresenta uma situação aparentemente paradoxal que exige nossa mais profunda análise. Embora os dados indiquem um balanço energético momentaneamente positivo, com um superávit de 10.06 MW, uma ação de segurança fundamental foi implementada: o corte de energia no módulo Laboratório para preservação das baterias. Esta decisão, que à primeira vista pareceria contraditória dado o superávit, é, na realidade, uma consequência direta e alarmante das falhas na Fase 2. O algoritmo de balanceamento de carga, embora eficaz em gerenciar a demanda instantânea, está agora operando sob um regime de resiliência severamente comprometida. A precisão da previsão eólica por regressão linear, que indicou condições favoráveis para uma geração robusta de 85.06 MW com ventos registrados de 36.0 unidades, é, por si só, insuficiente para compensar a vulnerabilidade estrutural. O impacto real do corte seletivo de energia nos módulos não essenciais, como o Laboratório, sinaliza uma gestão de risco intensamente conservadora imposta pela ausência do MOD-LOG-01 (que deveria prover capacidade de manutenção e substituição de baterias) e uma provável capacidade de armazenamento de energia (buffers) insuficiente para lidar com períodos de baixa geração prolongados. Esse corte é uma medida proativa para mitigar riscos futuros, indicando que o "superávit" atual é enganoso, pois o consumo total real seria significativamente maior com todos os módulos operacionais, e reflete uma priorização crítica para a sobrevivência em um ambiente degradado.
=====================================================================================
```

</details>

<br>

## 📂 Estrutura do Projeto
```Plaintext
PBL-Aurora/
├── .env                        # Chave de segurança da IA
├── .gitignore                  # Regras de exclusão do Git
├── requirements.txt            # Dependências do projeto
├── codigo/
│   ├── fase1.py                # Microsserviço de Lançamento
│   ├── fase2.py                # Microsserviço de Pouso Orbital
│   ├── fase3.py                # Microsserviço da Colônia e Regressão
│   └── main.py                 # Orquestrador Central e Integração IA
└── README.md                   # Documentação do projeto
```
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

### Executando a Simulação

O projeto possui duas saídas principais: uma simulação via console e uma interface web em desenvolvimento.

- **Para rodar a simulação no console:**
  ```bash
  python codigo/main.py
  ```
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
**Ano:** 2026\
**Turma:** 1CCOA-2026  
