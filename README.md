# Missão Aurora Siger 🚀

Este repositório contém a documentação e o protótipo inicial de telemetria da nave **Aurora**. O projeto integra conceitos de Ciência da Computação, Engenharia de Foguetes e Meteorologia para validar a segurança de um lançamento espacial.

## 📋 Sobre o Projeto
O objetivo desta fase é fornecer informações essenciais sobre o funcionamento de foguetes, abrangendo cálculos técnicos, estimativa de custos e o impacto social da exploração espacial. O projeto culmina em um script Python que processa dados de telemetria simulados para autorizar ou abortar uma decolagem.

### Parâmetros de Telemetria Monitorados:
* **Temperatura:** Interna e externa.
* **Integridade Estrutural:** Status operacional do corpo da nave.
* **Níveis de Energia:** Capacidade e carga disponível (%).
* **Pressão:** Monitoramento dos tanques.
* **Módulos Críticos:** Verificação de status dos sistemas essenciais.

---

## 👥 Equipe (FIAP 2026)
| Nome | RM |
| :--- | :--- |
| **Juan de Lucas Frois** | RM563260 |
| **Flávia Roberta Pennachin** | RM561860 |
| **Pedro Valente Toledo** | RM570394 |
| **Bruno Antonio Santos Silva** | RM573180 | 
| **Renan Mano Otero** | RM573615 |

---

## 🛠️ Implementação Técnica
O script Python realiza a leitura dos dados simulados e executa as seguintes verificações de segurança para permitir o lançamento:

### Regras de Negócio:
* **Integridade Estrutural:** Deve ser 1 (Operacional).
* **Energia:** Mínimo de 80% para decolagem segura.
* **Pressão:** Deve estar entre 300 e 450 psi.
* **Temperatura Interna:** Faixa segura entre 18°C e 25°C.
* **Módulos Críticos:** Devem retornar status "OK".

### Exemplo de Saída:
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

---

## 🌍 Reflexão Ética e Sustentabilidade
O projeto aborda a responsabilidade na exploração espacial, discutindo temas como:
* **Lixo Espacial:** Riscos de colisão e desórbita programada.
* **Impacto Social:** Como a tecnologia aeroespacial auxilia na agricultura e prevenção de desastres na Terra.
* **Ética:** Justificativa da expansão humana versus problemas globais imediatos.

---

**Instituição:** FIAP
**Ano:** 2026
