# 🚀 Missão Aurora Siger 

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Status](https://img.shields.io/badge/status-Concluído-green.svg)

Projeto desenvolvido para o **Project Based Learning (PBL)** da FIAP, com foco em simulação computacional, análise de telemetria, gerenciamento de pouso e operação inteligente de uma colônia em Marte.

<br>

### Visão Geral

O sistema foi estruturado em três fases integradas, cada uma responsável por uma etapa crítica da missão: validação de decolagem, gestão de pouso dos módulos e funcionamento inteligente da colônia.

<br> 

## A evolução do projeto ocorre através de três macroetapas:
  
### 🚀 Fase 1: Decolagem da Missão
Realiza a validação inicial da missão por meio da análise de telemetria, da checagem automatizada de pré-lançamento e da identificação de anomalias, verificando se as condições operacionais permitem autorizar ou abortar a decolagem.
 
<details>
<summary>Clique para ver a fase 1 em detalhe:</summary>
  
### Visão Geral da Fase
Esta fase concentra a análise inicial da missão, verificando se a nave apresenta condições adequadas para iniciar a operação. O sistema interpreta os dados recebidos, aplica critérios de validação e apresenta um diagnóstico técnico da situação operacional.

<br>

### Objetivo da Fase
* **Simulação de telemetria:** Geração de dados randômicos para parâmetros críticos do foguete (temperatura, pressão, energia, integridade, módulos críticos).
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

### Regras de Negócio de Segurança
Para que a decolagem seja autorizada, todos os critérios abaixo devem ser satisfeitos em 3 rodadas consecutivas:
* **Integridade Estrutural:** deve ser 1 (Operacional).
* **Energia:** mínimo de 80% para decolagem segura.
* **Pressão:** entre 300 e 450 psi.
* **Temperatura Interna:** entre 18°C e 25°C.
* **Módulos Críticos:** todos com status "OK".

Se qualquer uma dessas condições falhar em uma rodada, o teste é marcado como FALHA, e a missão é abortada ao final da sequência, com emissão de relatório técnico da IA.

<br>

### Exemplo de Saída no Console
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

###  Arquitetura e Fluxo de Decisão

Em alto nível, o sistema segue o fluxo:

1. **Geração de telemetria simulada** (valores aleatórios dentro/fora dos limites).

2. **Aplicação das regras de negócio** para cada rodada de teste.

3. **Cálculo do status da missão** (GO / NO-GO) após 3 rodadas.

4. **Em caso de falha**:

    * Registro das anomalias por rodada.

    * Geração de relatório técnico com IA (Gemini).

<br>

### Fluxo de Decisão da Missão
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

### REFLEXÃO CRÍTICA: MISSÃO AURORA
A exploração espacial é o reflexo dos valores da humanidade. Na Missão Aurora, a telemetria não apenas monitora máquinas, mas protege vidas e fundamenta uma presença humana ética e consciente.

###  Ética e Responsabilidade
A exploração espacial não é uma fuga dos problemas terrestres, mas uma busca por soluções globais. O espaço deve ser um bem comum, focado na ciência e na cooperação, evitando a militarização e garantindo que o progresso tecnológico beneficie toda a sociedade, não apenas grupos restritos.

###  Sustentabilidade e Lixo Espacial
A órbita terrestre é um recurso finito. Para evitar o Efeito Kessler (colisões em cadeia), a missão adota protocolos de Desórbita Programada: cada componente possui um fim de ciclo planejado, garantindo que a "estrada espacial" permaneça limpa e segura para as futuras gerações.

###  Impacto Social do Lançamento Tripulado
Enviar seres humanos ao espaço gera transformações profundas na estrutura social:

* Inspiração STEM: O "Efeito Apollo" atrai jovens para carreiras científicas e quebra barreiras sociais através da representatividade.

* Diplomacia Global: A manutenção da vida em órbita exige cooperação internacional, promovendo o diálogo e reforçando a identidade planetária (Overview Effect).

* Avanços na Medicina: A telemetria e o suporte à vida impulsionam a telemedicina, cirurgias robóticas e tratamentos de perda óssea/muscular para idosos na Terra.

* Cultura de Segurança: Os rigorosos protocolos de falha zero e as tecnologias de reciclagem de recursos (água e ar) são aplicados hoje em indústrias críticas e na gestão de desastres ambientais.

<br>

**Conclusão:** Decolar exige mais que combustível; exige o compromisso de proteger quem parte, quem fica e o ambiente que nos cerca.
</details>

<br>

### 🚀 Fase 2: Módulo de Gestão de Pouso e Estabilização da Base (MGPEB)
Coordena a aproximação e o pouso dos módulos da missão, organizando a sequência de descida, priorizando situações críticas e aplicando regras lógicas, estruturas dinâmicas e algoritmos para garantir uma operação segura.  
<details>
<summary>Clique para ver a fase 2 em detalhe:</summary>

### Visão Geral da Fase:
Nesta etapa, o sistema controla a descida dos módulos da missão até a base marciana. A lógica considera fatores operacionais e emergenciais para reorganizar prioridades, reter módulos em órbita quando necessário e registrar alertas críticos da operação.

<br>

### Objetivo da Fase

- Gerenciar a fila de pouso dos módulos em aproximação orbital.
- Priorizar módulos em situação crítica.
- Aplicar lógica booleana para autorizar ou negar pousos.
- Utilizar algoritmos de busca e ordenação para apoiar a tomada de decisão.
- Registrar alertas e contingências durante a operação.
<br>

### Estruturas de Dados Utilizadas
O sistema gerencia os módulos (representados como dicionários) utilizando três conceitos de estruturas de dados lineares:
* **Fila de Pouso (`Queue` - FIFO):** Garante a regra de que o primeiro módulo a chegar/solicitar a descida seja o primeiro a ser processado (`pop(0)`).
* **Listas de Histórico (`List`):** Utilizadas para catalogar o destino final das entidades, divididas entre `lista_pousados` (sucesso na superfície) e `lista_espera` (módulos retidos em órbita por contingência).
* **Pilha de Alertas (`Stack` - LIFO):** Registra as anomalias climáticas e operacionais mais recentes no topo da pilha, garantindo que o último erro inserido seja o primeiro a ser exibido e tratado pelo painel (`pop()`).

<br>

### Algoritmos Implementados
Para processar e otimizar a fila de pouso, foram desenvolvidos dois algoritmos nativos (sem o uso de bibliotecas externas):
* **Busca Sequencial:** Varre a fila de pouso de forma linear para identificar instantaneamente qual módulo possui o menor nível crítico de combustível.
* **Insertion Sort (Ordenação por Inserção):** Reordena dinamicamente a fila com base na prioridade numérica do módulo (onde a prioridade 1 representa maior urgência), garantindo que os módulos de suporte médico e energético passem à frente.

<br>

### Portas Lógicas e Regras de Decisão
A autorização final para o pouso de cada módulo exige uma validação booleana composta através de operadores lógicos estritos:
1. **Regra de Sucesso Primária (`AND` Estrito):** O pouso só é executado com sucesso se:
   $$\text{combustivel\_ok} \land \text{sensores\_ok} \land \text{clima\_ok} \land \text{area\_livre}$$
2. **Regra de Contingência Energética:** Se um módulo apresentar combustível crítico ($\le 15\%$) mas não possuir prioridade alta, o sistema intercepta a entidade, eleva sua prioridade e reordena a fila.
3. **Regra de Retenção por Clima e Sensores:** Se o radar acusar clima adverso **E** os sensores do módulo estiverem em falha, o pouso é negado imediatamente e o evento é enviado para o topo da pilha de alertas.

<br>

### Exemplo de Entrada e Saída (Telemetria Simulada)
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

````
</details>

<br>


### 🚀 Fase 3: Sistema de Funcionamento Inteligente da Colônia
Gerencia de forma inteligente os subsistemas da colônia, priorizando recursos críticos e apoiando decisões automáticas para manter a operação da base.
<details>
<summary>Clique para ver a fase 3 em detalhe:</summary><br>

### Visão Geral da Fase:
Esta fase unifica processamento de dados e tomada de decisão para manter a colônia em funcionamento. O sistema avalia condições energéticas, prioriza recursos críticos e utiliza previsão para apoiar a continuidade operacional da colônia Aurora Prime.

<br>

### Objetivo da Fase
- Monitorar os subsistemas essenciais da colônia.
- Aplicar regras condicionais para respostas automáticas.
- Avaliar o equilíbrio entre geração e consumo de energia.
- Apoiar decisões relacionadas à eficiência energética.
- Estimar cenários futuros com base em regressão linear.

<br>

###  Exemplo de Entrada e Saída (Validação do Sistema)

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

### Exemplo saída terminal:

```
=====================================================================================
                     INICIANDO SISTEMA INTEGRADO DA MISSÃO AURORA                    
=====================================================================================

=====================================================================================
            INICIANDO FASE 1: TELEMETRIA E PRÉ-DECOLAGEM (SISTEMA NOMINAL)           
=====================================================================================
-------------------------------------------------------------------------------------
|                                RODADA 1/3 - SUCESSO                               |
|                                                                                   |
| STATUS: OPERAÇÃO NOMINAL                                                          |
|   > Bateria Útil: 4560.30 kWh                                                     |
|   > Autonomia após decolagem: 94.36% (Safe > 80%)                                 |
|   > Pressão interna: 399.42 psi                                                   |
|   > Temperatura Interna: 22.31 C°                                                 |
| STATUS DOS MÓDULOS CRÍTICOS: OK                                                   |
|                                                                                   |
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
|                                RODADA 2/3 - SUCESSO                               |
|                                                                                   |
| STATUS: OPERAÇÃO NOMINAL                                                          |
|   > Bateria Útil: 4722.60 kWh                                                     |
|   > Autonomia após decolagem: 93.90% (Safe > 80%)                                 |
|   > Pressão interna: 378.33 psi                                                   |
|   > Temperatura Interna: 20.22 C°                                                 |
| STATUS DOS MÓDULOS CRÍTICOS: OK                                                   |
|                                                                                   |
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
|                                RODADA 3/3 - SUCESSO                               |
|                                                                                   |
| STATUS: OPERAÇÃO NOMINAL                                                          |
|   > Bateria Útil: 4758.56 kWh                                                     |
|   > Autonomia após decolagem: 94.25% (Safe > 80%)                                 |
|   > Pressão interna: 392.11 psi                                                   |
|   > Temperatura Interna: 21.82 C°                                                 |
| STATUS DOS MÓDULOS CRÍTICOS: OK                                                   |
|                                                                                   |
-------------------------------------------------------------------------------------

>>> STATUS FINAL: DECOLAGEM AUTORIZADA! 🚀

=====================================================================================
                    INICIANDO FASE 2: APROXIMAÇÃO E POUSO (MGPEB)                    
=====================================================================================

--- INICIANDO PROTOCOLO DE POUSO ---

[Analisando] MOD-MED-01 (Prioridade 1 | Combustível: 24.9%)
   -> FALHA: Pouso negado.
      Motivo: Condição atmosférica adversa (Cisalhamento de Vento, Tempestade de Areia, Frio Extremo Inesperado).

[Analisando] MOD-ENE-01 (Prioridade 2 | Combustível: 12.7%)
   -> ALERTA MÁXIMO: Falha de Sensores + Clima Adverso (Frio Extremo Inesperado) no módulo MOD-ENE-01

[Analisando] MOD-HAB-01 (Prioridade 3 | Combustível: 33.7%)
   -> SUCESSO: Pouso autorizado.

[Analisando] MOD-LOG-01 (Prioridade 4 | Combustível: 27.8%)
   -> SUCESSO: Pouso autorizado.

[Analisando] MOD-LAB-01 (Prioridade 5 | Combustível: 43.5%)
   -> SUCESSO: Pouso autorizado.

=====================================================================================
                   INICIANDO FASE 3: SISTEMA INTELIGENTE DA COLÓNIA                  
=====================================================================================

=====================================================================================
                          RESUMO TÉCNICO - FASE 3 (COLÔNIA)                          
Balanço Energético: 10.06 MW
Status do Sistema: ENERGIA EXCEDENTE
Ações tomadas: Nenhuma
=====================================================================================

=====================================================================================
                       PROCESSAMENTO DE DADOS E AUDITORIA (IA)                       
=====================================================================================
>> Extraindo correlações e gerando contexto analítico profundo...
>> Sintetizando Boletim Executivo Estruturado...

--- BOLETIM DO DIRETOR DE VOO ---
INICIANDO FASE 1: TELEMETRIA E PRÉ-DESCOLAGEM
-> A Fase 1 (Lançamento) foi concluída com sucesso completo, registrando três lançamentos bem-sucedidos.
-> Não foram detectadas falhas ou anomalias durante esta fase crítica da missão.
-> A execução precisa estabeleceu uma base operacional sólida para as fases subsequentes.

INICIANDO FASE 2: APROXIMAÇÃO E POUSO (MGPEB)
-> Três módulos essenciais (MOD-HAB-01, MOD-LOG-01, MOD-LAB-01) pousaram com êxito.
-> Contudo, os módulos MOD-MED-01 e MOD-ENE-01 permanecem em espera, gerando um atraso crítico.
-> Foi emitido "ALERTA MÁXIMO" para o MOD-ENE-01 devido a falha de sensores e frio extremo inesperado.
-> Esta condição representa uma vulnerabilidade substancial à infraestrutura energética primária.

INICIANDO FASE 3: SISTEMA INTELIGENTE DA COLÓNIA
-> A colônia opera com estabilidade energética atual, registrando um excedente de 10.06 MW.
-> A geração de 85.06 MW supera o consumo de 75.0 MW, auxiliada por ventos de 36.0.
-> Recomenda-se o armazenamento proativo deste excedente para otimizar a resiliência.
-> Contudo, esta margem é temporária e a ausência do MOD-ENE-01 limita expansão e redundância futura.
-> O frio extremo inesperado pode impactar o consumo de aquecimento e a eficiência geral dos sistemas.
=====================================================================================
```

</details>

<br>

## Estrutura do Projeto
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
<br>

## Tecnologias Utilizadas

- Python
- Estruturas condicionais
- Estruturas de repetição
- Listas, filas e pilhas
- Algoritmos de busca e ordenação
- Regressão linear
- Organização modular em arquivos Python

<br>

## Configuração e Instalação
Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos
- [Python 3.9+](https://www.python.org/downloads/)
- Chave de API do [Google AI Studio (Gemini)](https://aistudio.google.com/app/apikey)
<br>

### Passos para Executar o Projeto
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

<br>

## 👥 Equipe (FIAP 2026)
| Nome | RM |
| :--- | :--- |
| **Juan de Lucas Frois** | RM563260 |
| **Flávia Roberta Pennachin** | RM561860 |
| **Pedro Valente Toledo** | RM570394 |
| **Bruno Antonio Santos Silva** | RM573180 | 
| **Renan Mano Otero** | RM573615 |

---
**Instituição:** FIAP\
**Ano:** 2026\
**Turma:** 1CCOA-2026  
