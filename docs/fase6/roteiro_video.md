# Roteiro do Vídeo de Apresentação — Fase 6 (SCIC)
**Projeto Aurora Siger · FIAP 1CCOA-2026**
**Formato:** Apresentador Único (Gravação Solo com Tela Compartilhada + Terminal CLI)
**Duração Máxima:** 5:00 minutos | **Publicação:** YouTube como "Não listado" (Link em `docs/fase6/link_video.txt`)

---

## 📋 Matriz de Cobertura dos Requisitos do Edital

| # | Requisito Obrigatório do Edital | Onde é Apresentado no Vídeo | Opção no Menu CLI |
|---|---|---|---|
| 1 | Descrição da comunicação interplanetária da Aurora Siger | Bloco 1 (0:00 – 0:35) | Slide Arquitetural |
| 2 | Explicação dos dados operacionais e de comunicação | Bloco 2 (0:35 – 1:15) | Opção **[1]** |
| 3 | Leitura, organização e análise de dados (Pandas/NumPy) | Bloco 2 (0:35 – 1:15) | Opção **[1]** |
| 4 | Indicadores de comunicação calculados | Bloco 2 (0:35 – 1:15) | Opção **[1]** |
| 5 | Eletricidade básica, I/O e bases numéricas (Hex/Dec/Bin) | Bloco 3 (1:15 – 1:55) | Opções **[2]**, **[3]** e **[4]** |
| 6 | Erros numéricos (Absoluto/Relativo) e Ponto Flutuante | Bloco 4 (1:55 – 2:35) | Opção **[1]** (Bloco ML) |
| 7 | Modelo simples de previsão (Regressão Linear / scikit-learn) | Bloco 5 (2:35 – 3:15) | Opção **[1]** + Gráfico |
| 8 | Métricas de performance (MAE, MSE, RMSE, R² + Outliers) | Bloco 5 (2:35 – 3:15) | Opção **[1]** + Gráfico |
| 9 | Priorização de alertas com Heap (Max-Heap binário O(log n)) | Bloco 6 (3:15 – 3:55) | Opção **[5]** (Heap) |
| 10 | Busca por prefixo com Trie (Módulos, Sensores Hex e Comandos) | Bloco 7 (3:55 – 4:25) | Opção **[6]** (Trie) |
| 11 | Demonstração prática do sistema em Python (CLI + Análise IA) | Bloco 8 (4:25 – 4:50) | `main.py` Opção **[S]** |
| 12 | Gerenciamento inteligente, manutenção preditiva e ética | Bloco 9 (4:50 – 5:00) | Slide Encerramento |

---

## ⏱️ Roteiro de Fala e Ações na Tela (Apresentador Único)

### Bloco 1 — Abertura e Comunicação Interplanetária (0:00 – 0:35)
* **O que Mostrar:** Slide inicial (Nome, RM, Turma FIAP) + Diagrama Arquitetural do SCIC.
* **Sua Fala:**
  > *"Olá, professor! Sou o Pedro Toledo, apresentando o projeto da nossa equipe da Missão Aurora Siger — composta por mim, pelo Juan Frois e pela Flávia Pennachin. Hoje vou demonstrar o SCIC — Sistema Computacional Integrado da Colônia. Em Marte, a comunicação com a Terra enfrenta latências de 3 a 22 minutos, além de interferências solares. Para manter os 8 módulos da base operacionais, o SCIC integra telemetria em tempo real, física elétrica, regressão estatística para estimar latências locais, e estruturas de dados avançadas em Python para priorização de alertas e busca por prefixo."*

---

### Bloco 2 — Ingestão de Dados, Limpeza e Indicadores Operacionais (0:35 – 1:15)
* **O que Mostrar:** Terminal executando `python main.py` (ou `python -m src.fase6_scic.fase6_scic`) $\rightarrow$ Selecionar Opção **[1] (Gerar e Persistir Dataset de Telemetria)**.
* **Sua Fala:**
  > *"Abrindo a interface CLI do sistema em Python: na opção [1], com Pandas e NumPy, geramos e carregamos a base `dados_aurora_siger.csv`, contendo 120 registros simulados (15 ciclos x 8 módulos). A função `carregar_telemetria_csv()` limpa nulos e duplicados, validando os dados em faixas físicas reais de temperatura, pressão e radiação. O sistema calcula automaticamente os indicadores operacionais: latência média por módulo — variando de 30,5ms na Comunicação Central a 69,5ms na Estufa —, taxa de disponibilidade da colônia de 79,2%, percentual de alertas de 14,2% e 47,5% dos registros com latência acima do previsto."*

---

### Bloco 3 — Eletricidade Básica, Interfaces I/O e Conversão Hexadecimal (1:15 – 1:55)
* **O que Mostrar:** Terminal $\rightarrow$ Testar Opção **[2] (Diagnóstico Elétrico)**, Opção **[3] (Mapear I/O)** e Opção **[4] (Decodificar Hex)**.
* **Sua Fala:**
  > *"Na camada física, na opção [2], aplicamos a Lei de Ohm ($R = V / I$) e a potência elétrica ($P = V \times I$). Um circuito operando em 230V e 28A consome 6.440W; se ultrapassar o limite térmico do módulo, o barramento aciona um alerta de sobrecarga. Na opção [3], mapeamos as interfaces I/O e protocolos: SpaceWire na Comunicação, CAN Bus no Controle, e RS-485 na Estufa. Na opção [4], fazemos a conversão de bases numéricas para registradores de hardware: o sensor `0x2A` do módulo de comunicação é convertido em decimal (42) e binário de 8 bits (`00101010`)."*

---

### Bloco 4 — Ponto Flutuante e Erros Numéricos (1:55 – 2:35)
* **O que Mostrar:** Terminal (Resultados do Bloco de Ponto Flutuante e Tabela de Erros gerados na opção [1]).
* **Sua Fala:**
  > *"Na análise numérica, demonstramos a limitação do padrão IEEE 754 de ponto flutuante: no Python, `0.1 + 0.2 == 0.3` resulta em `False` devido ao ruído de representação binária (`1.11e-16`). Medimos os erros entre a latência observada ($y$) e a prevista pelo modelo ($\hat{y}$): o Erro Absoluto ($EA = |y - \hat{y}|$) teve média de 3,60ms; o Erro Relativo ($ER = |y - \hat{y}|/|y|$) teve média de 7,92%. O sistema classifica automaticamente a precisão: 37,5% das leituras na faixa Aceitável (<5%), 58,3% em Atenção (5-15%) e 4,2% em Preocupante (>15%)."*

---

### Bloco 5 — Modelo de Previsão de Latência e Métricas (MAE, MSE, RMSE, R²) (2:35 – 3:15)
* **O que Mostrar:** Terminal (Tabela de Métricas Treino vs Teste) + Abrir a imagem `graficos_ou_imagens/avaliacao_modelo_scic.png`.
* **Sua Fala:**
  > *"Construímos um modelo de Regressão Linear com scikit-learn utilizando One-Hot Encoding para os módulos, divisão 80/20 e validação cruzada 5-fold. No conjunto de teste, obtivemos: MAE de 3,60ms, MSE de 34,42ms², RMSE de 5,87ms e $R^2$ de 0,776. Como a razão RMSE/MAE é de 1,63 (superior a 1,4), o RMSE penalizou erros mais severos decorrentes de picos esporádicos de latência (outliers). No painel visual gerado pelo Matplotlib, observamos a dispersão real vs. previsto, os resíduos e a distribuição dos erros."*

---

### Bloco 6 — Fila de Prioridade com Heap Binário (3:15 – 3:55)
* **O que Mostrar:** Terminal $\rightarrow$ Selecionar Opção **[5] (Central de Alertas Críticos — Heap)** $\rightarrow$ [1] Top Alertas, [2] Atender Alerta.
* **Sua Fala:**
  > *"Para organizar as emergências da colônia, na opção [5], implementei a classe `HeapAlertas`, um Max-Heap binário codificado do zero em Python. Em vez de usar uma lista comum que exigiria busca $O(n)$, o heap insere e extrai o alerta mais crítico em $O(\log n)$ e permite consultar a raiz em $O(1)$. A criticidade é calculada combinando status, tipo de alerta, excesso de potência e desvio de latência, desempatando pela ordem de chegada para evitar starvation. No benchmark integrado (opção [7]) de 5.000 alertas, o Heap respondeu em 53ms contra 468ms da lista comum."*

---

### Bloco 7 — Busca por Prefixo com Trie (3:55 – 4:25)
* **O que Mostrar:** Terminal $\rightarrow$ Selecionar Opção **[6] (Busca por Prefixo — Trie)** $\rightarrow$ Digitar `com`, `0x2` e `/di`.
* **Sua Fala:**
  > *"Para busca rápida durante operações de emergência, na opção [6], desenvolvi a classe `TrieModulos`. A árvore de prefixos armazena 62 chaves normalizadas sem acentos nem caixa alta. Ao digitar o prefixo `com`, a Trie retorna 'Comunicação Central'; ao digitar `0x2`, traz os sensores `0x2A` e `0x2B` com suas conversões binárias; e ao digitar `di`, encontra o comando `/diagnosticar`. A busca roda em $O(m+k)$, dependendo apenas do tamanho do prefixo digitado e não da quantidade de dados."*

---

### Bloco 8 — Integração no `main.py` e Análise Unificada com IA (4:25 – 4:50)
* **O que Mostrar:** Terminal $\rightarrow$ Voltar ao Menu Principal (`0`) e digitar **[S] (Análise Integrada da Missão com IA)**.
* **Sua Fala:**
  > *"No orquestrador principal `main.py`, unificamos todas as 6 fases do projeto. Cada etapa executada grava automaticamente logs estruturados no arquivo `registros_colonia.txt`. Ao pressionar a opção [S], o sistema envia todo o histórico acumulado de logs para a API do Gemini, gerando um Boletim Executivo do Diretor de Voo com diagnóstico cronológico, correlações entre energia, rede e latência, e recomendações técnicas."*

---

### Bloco 9 — Gerenciamento Inteligente e Encerramento (4:50 – 5:00)
* **O que Mostrar:** Slide de Encerramento (Nomes da Equipe, RMs, Turma FIAP, Link do Repositório).
* **Sua Fala:**
  > *"Assim, o SCIC viabiliza a manutenção preditiva — detectando anomalias de latência antes que ocorra a falha —, otimiza a rede elétrica e mantém a tomada de decisão transparente e auditável por operadores humanos. Todo o código, a suíte de testes unitários e a documentação estão no repositório. Muito obrigado!"*

---

## 🛠️ Guia Rápido das Opções do Menu CLI da Fase 6

```plaintext
[1] Gerar e Persistir Dataset de Telemetria (CSV)
[2] Executar Diagnóstico de Circuito Elétrico (Lei de Ohm)
[3] Mapear Interfaces de I/O e Transmissão da Colônia
[4] Decodificar Registrador Hexadecimal
[5] Central de Alertas Críticos (Heap / Fila de Prioridade)
[6] Busca por Prefixo de Módulos e Sensores (Trie)
[7] Benchmark Heap x Lista Comum
[8] Executar Pipeline Completo do SCIC (dados -> modelo -> heap -> trie)
[0] Voltar ao Menu Principal / Sair
```
