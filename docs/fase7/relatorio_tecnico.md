# Relatório Técnico - Fase 7: SIFSM (Sistema Integrado de Futuro Sustentável em Marte)

**Missão Aurora Siger · FIAP · 1CCOA-2026**

Equipe: Juan de Lucas Frois (RM563260) · Flávia Roberta Pennachin (RM561860) · Pedro Valente Toledo (RM570394)

> Rascunho em construção. As seções 2 a 4 (Integrante 1) já refletem o código entregue; as seções
> marcadas com **(a preencher)** pertencem aos Integrantes 2 e 3. O Integrante 3 consolida o texto final.

## 1. Contexto e visão geral *(a preencher - Integrante 3)*
Como o SIFSM integra dados, regra lógica, estruturas, simulação, modelo linear e agentes para apoiar a
sustentabilidade da Aurora Siger. Fluxo: `codigo_fonte.py` (menu) -> `src/fase7_sifsm/*`.

## 2. Dados e banco de dados (Integrante 1)

**Escolha do banco.** SQLite (`sqlite3`, biblioteca padrão do Python). O Oracle do material do curso exige
servidor e credenciais; o SQLite roda em qualquer máquina sem instalação, o que permite ao avaliador
executar o projeto. O esquema está em `data/fase7/script_banco.sql` e o banco (`aurora_siger.db`) é criado
na primeira execução.

**Tabelas.**

| Tabela | Conteúdo | Observações |
|---|---|---|
| `modulos` | os 8 módulos da colônia (id, nome, tipo, `essencial`, `limite_consumo_w`, status) | `essencial = 1` define o módulo crítico da regra booleana |
| `sensores` | código hexadecimal (ex.: `0x1A`), módulo e tipo | herdados da Fase 6 |
| `leituras` | consumo (W), temperatura, umidade, carga da bateria, status, data | tabela principal do CRUD |
| `alertas` | alertas gerados pela regra booleana | ligados à leitura de origem |
| `chamados` | solicitações da tripulação | alimentam a fila (FIFO) |

As restrições do próprio banco (`CHECK`, chaves estrangeiras, `NOT NULL`) funcionam como segunda barreira de
validação: consumo negativo, umidade fora de 0-100 ou módulo inexistente são rejeitados mesmo se a validação
em Python falhar.

**Base simulada.** `data/fase7/dados_aurora_siger.csv` tem 120 leituras (8 módulos x 15 ciclos de 6 h),
geradas de forma determinística por `src/fase7_sifsm/dados_simulados.py` (semente 42). O consumo depende
linearmente da temperatura e da umidade, com ruído, para sustentar a regressão linear (seção do Integrante 2).
Foram injetados 7 picos de consumo, 1 falha de sensor e 1 manutenção, para exercitar a regra de decisão.

**CRUD** (`src/fase7_sifsm/banco.py`, opções 1 a 4 do menu):

| Operação | Função | Cuidados |
|---|---|---|
| Cadastrar | `cadastrar_leitura` | valida tipos, faixas, formato de data e do código do sensor; avalia o risco e registra alerta |
| Listar | `listar_leituras` | filtros por módulo e status, limite e ordem validados |
| Alterar | `alterar_leitura` | só campos permitidos (lista fixa); revalida o registro mesclado |
| Excluir | `excluir_leitura` | pede confirmação no menu |
| Desfazer | `restaurar_leitura` | desfaz a última ação usando a pilha de histórico |

**Tratamento de erros.** Entradas inválidas levantam `ErroBanco` com mensagem clara (ex.: "O campo
'consumo_w' deve ser numérico (recebido: 'abc')"). As operações usam `try/except/else/finally`: `except` converte
erros do SQLite em mensagens para o usuário e faz `rollback`; `else` devolve o resultado; `finally` fecha a
conexão. O menu captura `ErroBanco`, `ValueError` e `sqlite3.Error` sem encerrar o programa.

**Segurança.** Todas as consultas são parametrizadas (`?`); nomes de coluna só vêm de listas fixas. Há teste
automatizado de tentativa de SQL injection (`tests/test_fase7_banco.py`).

## 3. Regra booleana e circuito lógico (Integrante 1)

Variáveis: **A** = `CONSUMO_ELEVADO` (consumo > 90% do limite do módulo), **B** = `MODULO_CRITICO`
(módulo essencial), **C** = `SENSOR_VALIDO` (leitura confiável: sem falha e com valores plausíveis).

- `ALERTA = A AND B AND C`
- `BLOQUEIO = NOT C` (não decidir com base em sensor inválido)
- De Morgan: `NOT ALERTA = (NOT A) OR (NOT B) OR (NOT C)`

| A | B | C | ALERTA | BLOQUEIO |
|---|---|---|:---:|:---:|
| 0 | 0 | 0 | 0 | 1 |
| 0 | 0 | 1 | 0 | 0 |
| 0 | 1 | 0 | 0 | 1 |
| 0 | 1 | 1 | 0 | 0 |
| 1 | 0 | 0 | 0 | 1 |
| 1 | 0 | 1 | 0 | 0 |
| 1 | 1 | 0 | 0 | 1 |
| 1 | 1 | 1 | **1** | 0 |

A função `classificar_risco` traduz a regra em quatro níveis: `bloqueado` (sensor inválido), `alto`
(alerta), `medio` (consumo elevado em módulo não crítico) e `baixo`. Está em `src/fase7_sifsm/logica.py`
e é usada pelo cadastro, pela listagem, pelo heap de alertas e pelos módulos do Integrante 2.

**Circuito.** `docs/fase7/circuito_logico.png`: duas portas AND em cascata (A, B -> AND; saída e C -> AND) ligadas
ao LED vermelho de ALERTA, e um inversor ligado ao LED amarelo de BLOQUEIO. A montagem no Tinkercad (portas
74HC08/74HC04 ou Arduino Uno, com o código `docs/fase7/tinkercad/sifsm_alerta.ino`) está descrita em
`docs/fase7/tinkercad/README.md`. A tabela de teste do circuito é a mesma do sistema (opção 5 do menu).

## 4. Estruturas de dados (Integrante 1)

| Estrutura | Uso na colônia | Por que | Custo |
|---|---|---|---|
| Fila (FIFO) | chamados da tripulação | justiça: o primeiro chamado é o primeiro atendido | enfileirar e atender O(1) |
| Pilha (LIFO) | histórico de ações do CRUD, para desfazer | a última ação é a primeira a ser revertida | empilhar e desempilhar O(1) |
| Tabela hash (encadeamento) | busca de sensor por código hexadecimal | acesso direto ao sensor/módulo; colisões tratadas com listas | O(1) médio |
| Heap máximo (Fase 6) | alertas, do mais crítico ao menos crítico | sempre atende primeiro o mais grave | inserir e extrair O(log n) |

A tabela hash é implementada manualmente (função de hash polinomial, redimensionamento com fator de carga
0,75) em `src/fase7_sifsm/estruturas.py`. O heap reaproveita `HeapAlertas` da Fase 6 por meio de
`montar_heap_de_alertas`, que converte as leituras da Fase 7 para o formato da Fase 6. A opção 7 do menu
demonstra as quatro estruturas com dados reais do banco.

## 5. Simulação computacional e integração matemática *(a preencher - Integrante 2)*
## 6. Modelo linear e interpretação dos resultados *(a preencher - Integrante 2)*
## 7. Agentes, guardrails e integração de IA *(a preencher - Integrante 2)*
## 8. Arquitetura computacional, processamento e aceleração *(a preencher - Integrante 3)*
## 9. Sustentabilidade, cidadania digital e impacto socioambiental *(a preencher - Integrante 3)*
## 10. Limitações e melhorias *(a preencher - todos; consolidação: Integrante 3)*
## 11. Como executar *(a preencher - Integrante 3)*
