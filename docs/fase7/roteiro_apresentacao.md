# Roteiro de Apresentação (Vídeo Pitch — Fase 7: SIFSM)

**Projeto:** SIFSM — Sistema Integrado de Futuro Sustentável em Marte (Missão Aurora Siger)  
**Turma:** 1CCOA-2026 — FIAP  
**Duração Alvo:** 4 min 30 s a 5 min 00 s  
**Modalidade de Entrega:** YouTube (Não listado) — colar URL final em `docs/fase7/link_video.txt`

---

## Preparação Antes de Gravar

1. Abrir o terminal na raiz do projeto (`PBL-Aurora/`).
2. Garantir que o banco esteja no estado limpo original de 120 leituras:
   - Se desejar recriar a base limpa antes da gravação, apague `data/fase7/aurora_siger.db` e inicie `python codigo_fonte.py` (ele recriará o banco automaticamente com as 120 leituras e 5 chamados).
3. Deixar abertos em abas de apoio:
   - `docs/fase7/graficos_ou_imagens/circuito_logico.png`
   - `docs/fase7/graficos_ou_imagens/consumo_cenarios.png` e `bateria.png`
   - `docs/fase7/graficos_ou_imagens/analise_exploratoria.png`, `regressao.png` e `residuos.png`

---

## Bloco 1 — Fundação: Banco SQLite, CRUD, Lógica e Estruturas (0:00 – 1:45 | Integrante 1)

### 1.1 Contexto e Banco de Dados (`0:00 – 0:45`)
* **Fala sugerida:**
  > "Olá! Somos a equipe da Missão Aurora Siger e apresentamos o **SIFSM — Sistema Integrado de Futuro Sustentável em Marte**. Nosso objetivo na Fase 7 é integrar persistência em banco de dados, lógica booleana, estruturas de dados, simulação matemática, regressão linear e agentes determinísticos para apoiar decisões sustentáveis na colônia, sempre sob supervisão humana."
* **Ação na tela:**
  - Executar `.\venv\Scripts\python.exe codigo_fonte.py`.
  - Mostrar brevemente `data/fase7/script_banco.sql` (5 tabelas: `modulos`, `sensores`, `leituras`, `alertas`, `chamados`) e explicar que `dados_aurora_siger.csv` carrega 120 leituras (8 módulos em 15 ciclos de 6 h).
  - No menu:
    - Escolher **Opção `2` (Listar registros)** $\rightarrow$ filtrar por `MOD-01` para mostrar as leituras e a coluna `Risco` calculada dinamicamente.
    - Escolher **Opção `1` (Cadastrar leitura)** $\rightarrow$ demonstrar uma validação ou cadastro em `MOD-01` com consumo elevado (ex.: `6500 W`) gerando alerta automático, e em seguida usar a **Opção `U` (Desfazer)** para mostrar a reversão imediata via Pilha LIFO.

### 1.2 Regra Booleana, Circuito Lógico e Estruturas de Dados (`0:45 – 1:45`)
* **Ação na tela:**
  - Escolher **Opção `5` (Regra booleana e tabela-verdade)**:
    - Explicar: `ALERTA = CONSUMO_ELEVADO AND MODULO_CRITICO AND SENSOR_VALIDO` e `BLOQUEIO = NOT SENSOR_VALIDO`, além da equivalência pela Lei de De Morgan.
  - Escolher **Opção `6` (Circuito lógico / Tinkercad)** e exibir a imagem `circuito_logico.png`:
    - Mostrar as duas portas `AND` em cascata para o LED de Alerta e o inversor `NOT` para o LED de Bloqueio.
  - Escolher **Opção `7` (Estruturas de dados)**:
    - Destacar as 4 estruturas operando com dados reais do banco:
      1. `FilaChamados` (FIFO $O(1)$ para chamados da tripulação);
      2. `PilhaHistorico` (LIFO para desfazer ações do CRUD);
      3. `TabelaSensores` (Tabela Hash polinomial com encadeamento em $O(1)$ médio);
      4. `HeapAlertas` (Max-Heap $O(\log n)$ herdado da Fase 6 para priorizar alertas críticos).

---

## Bloco 2 — Análise: Simulação Energética, Modelo Linear e Agentes (1:45 – 3:45 | Integrante 2)

### 2.1 Simulação Computacional e Integração Numérica (`1:45 – 2:30`)
* **Ação na tela:**
  - Escolher **Opção `8` (Simulação computacional)** e exibir `consumo_cenarios.png` e `bateria.png`:
* **Fala sugerida:**
  > "Na Opção 8, integramos a curva de potência no horizonte de 24 horas usando a **Regra dos Trapézios** implementada manualmente. O consumo original totaliza **584,74 kWh**. Ao simular uma redução hipotética de 15% apenas nos módulos não essenciais — preservando todos os módulos vitais — obtemos uma economia potencial de **28,76 kWh (4,92%)**. Já a simulação da bateria de 100 kWh por 48 horas, com geração em 80% da demanda média, evidencia o esgotamento da carga (SoC = 0%) e um déficit de **153,90 kWh**, alertando o planejamento antes de uma falha real."

### 2.2 Modelo Linear de Apoio à Decisão (`2:30 – 3:10`)
* **Ação na tela:**
  - Escolher **Opção `9` (Modelo linear de apoio à decisão)** e mostrar `analise_exploratoria.png`, `regressao.png` e `residuos.png`:
* **Fala sugerida:**
  > "Na Opção 9, preparamos as 119 leituras válidas (excluindo o sensor em falha) e aplicamos separação estritamente temporal (80% treino, 20% teste). Ajustamos a regressão linear para estimar a potência a partir de temperatura e umidade. No teste, obtivemos $\text{MAE} = 589,07\text{ W}$, $\text{RMSE} = 885,97\text{ W}$ e $R^2 = 0,355$. Como a base possui picos operacionais e diferenças entre módulos, o MAE da regressão não superou o baseline da média do treino ($\text{MAE} = 555,51\text{ W}$). Por transparência científica, o sistema reporta essa limitação, impede extrapolações fora da faixa de treino e orienta que o modelo seja usado apenas para estudo exploratório, nunca para controle automático."

### 2.3 Sistema Multiagente Determinístico (`3:10 – 3:45`)
* **Ação na tela:**
  - Escolher **Opção `10` (Assistente multiagente)**:
    - Testar uma consulta válida: `consumo MOD-01` e depois `risco MOD-01` (ou usar os atalhos `1` e `2`), mostrando o `Triador`, o *handoff* para o especialista, o acionamento da ferramenta determinística e a trilha de auditoria (`opção 6`).
    - Mostrar que pedidos fora de escopo ou comandos de atuação (ex.: `desligue o modulo MOD-01`) são barrados pelo `guardrail_entrada`, e que toda saída exige validação humana.

---

## Bloco 3 — Fechamento: Arquitetura, Sustentabilidade e Fluxo Integrado (3:45 – 5:00 | Integrante 3)

### 3.1 Arquitetura Computacional e Cidadania Digital (`3:45 – 4:25`)
* **Ação na tela:**
  - Escolher **Opção `11` (Arquitetura computacional)** e **Opção `12` (Sustentabilidade e cidadania digital)**:
* **Fala sugerida:**
  > "Nas Opções 11 e 12, consolidamos a análise de arquitetura e governança socioambiental. Para 120 leituras, a execução local em CPU é ideal e evita a sobrecarga de transferência de memória que ocorreria ao enviar matrizes pequenas para GPUs ou TPUs. Na colônia em Marte, as regras booleanas rodam na borda (Edge) com consumo mínimo, enquanto o SQLite, a simulação e a regressão rodam no núcleo central. Em cidadania digital e ESG, garantimos quatro pilares no código: 1) Privacidade por minimização de dados (telemetria ligada apenas a códigos de módulo/sensor, sem dados pessoais da tripulação); 2) Sobriedade energética e térmica do módulo de dados `MOD-07`, sem chamadas obrigatórias a LLMs pesados; 3) *Human-in-the-Loop* estrito, bloqueando decisões sobre sensores inválidos (`BLOQUEIO = NOT C`) e isolando as ferramentas dos agentes em modo somente-leitura; e 4) Explicabilidade total das regras e métricas."

### 3.2 Fluxo Integrado (Opção A) e Testes Automatizados (`4:25 – 5:00`)
* **Ação na tela:**
  - Escolher **Opção `A` (ANALISAR SUSTENTABILIDADE DA COLÔNIA)**:
    - Mostrar o pipeline completo executando automaticamente: consulta das 120 leituras $\rightarrow$ classificação da última leitura dos 8 módulos na fila de prioridade $\rightarrow$ simulação energética $\rightarrow$ regressão linear $\rightarrow$ consulta aos 3 agentes especialistas com *tracing* $\rightarrow$ relatório de análise final e limitações.
  - Encerrar com `0` e rodar `.\venv\Scripts\python.exe -m pytest -q` mostrando **`43 passed`**.
* **Fala de encerramento:**
  > "Com a Opção A integrando todas as entregas dos três integrantes e 43 testes automatizados aprovados, encerramos a apresentação do SIFSM. Muito obrigado!"
