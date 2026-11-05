# Relatório Técnico - Fase 7 
# SIFSM (Sistema Integrado de Futuro Sustentável em Marte)

**Missão Aurora Siger · FIAP · 1CCOA-2026**

Equipe: Juan de Lucas Frois (RM563260) · Flávia Roberta Pennachin (RM561860) · Pedro Valente Toledo (RM570394)


## 1. Contexto e visão geral 

A operação da colônia Aurora Siger exige acompanhar recursos, identificar situações de atenção e avaliar
alternativas antes de modificar a infraestrutura. Leituras isoladas não mostram, por si só, a energia
acumulada, a autonomia de armazenamento ou as limitações de uma estimativa de consumo.

O SIFSM integra organização dos dados, banco de dados, lógica booleana, estruturas de dados,
simulação computacional, modelagem linear e agentes simulados. Seu objetivo é apoiar o planejamento
energético e a revisão de condições operacionais, preservando supervisão humana nas decisões críticas.

A interface principal é o menu textual de `codigo_fonte.py`. O Integrante 1 entrega dados, banco, CRUD, 
lógica e estruturas de dados (opções 1 a 7 e U). O Integrante 2 entrega simulação, regressão, agentes e 
análise integrada (opções 8, 9, 10 e A), com gráficos e documentação. O Integrante 3 entrega arquitetura 
e análise socioambiental (opções 11 e 12).



## 2. Dados e banco de dados (Integrante 1) | **Requisito 5.1**

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



## 3. Regra booleana e circuito lógico (Integrante 1) | **Requisito 5.2**

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



## 4. Estruturas de dados (Integrante 1) | **Requisito 5.3**

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



## 5. Simulação computacional e integração matemática (Integrante 2) | **Requisito 5.4**

O arquivo `src/fase7_sifsm/simulacao.py` organiza as leituras e representa consumo energético e armazenamento.
`simulacao_computacional.py` é o ponto de execução isolada, quando incluído na raiz do projeto.

### 5.1 Variáveis e unidades

| Variável | Significado | Unidade ou domínio |
|---|---|---|
| `data_registro` | Instante da leitura | Data e hora |
| `consumo_w` | Potência elétrica informada pela leitura | W |
| `modulo_id` | Identificação do módulo | Código |
| `essencial` | Indica módulo essencial | 0 ou 1 |
| `tempos_h` | Tempo desde o primeiro instante completo | h |
| `energia_wh` | Energia acumulada no intervalo | Wh |
| `potencia_media_w` | Energia dividida pela duração | W |
| `capacidade_wh` | Capacidade energética ideal da bateria | Wh |
| `geracao_w` | Potência de geração adotada | W |
| `soc` | Fração de energia disponível em relação à capacidade | 0 a 1 |
| `deficit_wh` | Energia acumulada não atendida após esgotamento | Wh |

Embora o campo se chame `consumo_w`, seu valor representa potência. A energia consumida é obtida
integrando essa potência ao longo do tempo.

### 5.2 Organização das leituras e cálculo da energia

A consulta usa `listar_leituras(limite=None, ordem="asc")`, evitando restringir a análise ao limite
padrão de 50 registros. O código organiza leituras por data e módulo, rejeita duplicatas e seleciona
instantes com todos os módulos encontrados na consulta. Ausência não é convertida em consumo zero.
Um módulo ausente de toda a consulta não é detectado por esse critério, o que limita a completude da análise.

O consumo total de cada instante corresponde à soma das potências dos módulos. O horizonte é de até
24 horas, limitado aos dados disponíveis. Se o término estiver entre duas leituras, a potência final
é interpolada linearmente.

A regra dos trapézios aproxima a integral por:

```text
E ≈ Σ [(P_i + P_(i+1)) / 2] × (t_(i+1) − t_i)
```

Como P está em watts e t em horas, E resulta em watt-hora. A potência média é:

```text
P_média = E / duração
```

A implementação manual com laço `for` torna explícito o cálculo da área sob a curva, conforme o
conteúdo de integração numérica do capítulo 6. A aproximação assume segmentos de reta entre amostras;
intervalos grandes podem ocultar variações intermediárias.

### 5.3 Comparação de cenários

O cenário original utiliza as leituras sintéticas do banco. O cenário eficiente aplica redução
hipotética de 15% somente nos módulos marcados como não essenciais. São criadas cópias das leituras,
sem modificar o banco. A economia é a diferença entre as energias dos dois cenários, no mesmo intervalo.

A redução de 15% é uma hipótese didática, não uma eficiência comprovada. A marcação de módulo não
essencial também não autoriza desligamento indiscriminado: uma revisão real exigiria avaliar dependências
e necessidades da tripulação.

### 5.4 Bateria e balanço energético

A bateria ilustrativa possui capacidade de 100.000 Wh (100 kWh), carga inicial de 80%, horizonte de
48 horas e passo de 0,5 h. O consumo é constante e igual à potência média do cenário original;
a geração constante corresponde a 80% desse consumo. Esses parâmetros são escolhas do modelo.

```text
E_bateria,seguinte = E_bateria,atual + (P_geração − P_consumo) × Δt
SoC = E_bateria / capacidade
```

A energia é limitada entre zero e a capacidade. Quando a demanda supera a energia disponível,
o modelo acumula energia não atendida. O último passo é ajustado ao horizonte solicitado.

O capítulo 6 apresenta estado de carga por integração da corrente e capacidade em Ah. Aqui, o princípio
de acumulação é adaptado para potência em W e capacidade em Wh. Não se trata de contagem de Coulomb
implementada diretamente nem de um modelo eletroquímico.

### 5.5 Gráficos, resultados e limitações

São gerados `consumo_cenarios.png` e `bateria.png` em `docs/fase7/graficos_ou_imagens/`.
O primeiro compara potências no tempo; o segundo mostra carga percentual. No modelo da bateria,
a demanda média constante não reproduz cada oscilação da série de consumo.

Não há perdas de conversão, envelhecimento, limites de corrente, efeitos térmicos ou geração variável.
Leituras sintéticas em falha permanecem na comparação energética como valores hipotéticos, sem validade
para decisões operacionais. A regra de risco trata a confiabilidade separadamente.

Os totais de energia e economia devem ser obtidos na execução da opção 8 e associados à versão
do banco utilizada. A simulação apoia comparação e planejamento, sem comprovar economia real.



## 6. Modelo linear e interpretação dos resultados (Integrante 2) | **Requisito 5.5**

`src/fase7_sifsm/modelo_linear.py` utiliza Pandas, NumPy, Matplotlib e `LinearRegression`, do scikit-learn, para estimar consumo.

### 6.1 Variáveis e preparação

O alvo é `consumo_w` (W). As entradas são `temperatura_c` (°C) e `umidade_pct` (%).
Essas duas variáveis participam da geração dos dados sintéticos. A carga da bateria não foi usada
como entrada porque é gerada separadamente, sem relação direta definida com o consumo nesse gerador.

A preparação converte valores numéricos e datas, remove ausências e valores não finitos, rejeita faixas
inválidas e exclui leituras com status `falha`. Os picos de consumo são mantidos: removê-los apenas para
melhorar métricas ocultaria uma dificuldade do problema.

Na execução informada pela equipe, 120 registros foram recebidos e 119 utilizados.

### 6.2 Análise exploratória

São apresentados estatísticas descritivas, médias por módulo, gráficos de dispersão e matriz de
correlação. Na base executada, o consumo médio foi 3.019,19 W, com mínimo de 2.282,84 W e máximo
de 7.569,00 W. A diferença entre média, mediana de 2.818,25 W e máximo evidencia valores elevados
que merecem inspeção.

As correlações observadas foram aproximadamente:

| Par de variáveis | Correlação |
|---|---:|
| Temperatura e consumo | 0,540 |
| Umidade e consumo | 0,136 |
| Temperatura e umidade | 0,630 |

Essas associações não demonstram causalidade. A correlação entre entradas é uma verificação inicial;
não foi calculado VIF e não se conclui, apenas com esses valores, que há multicolinearidade grave
ou que ela foi descartada.

### 6.3 Treinamento e coeficientes

A separação é temporal: os primeiros 80% dos instantes são usados para treinamento e os restantes
para teste. O mesmo instante não aparece nos dois conjuntos. Na execução registrada, foram 95 leituras
para treino e 24 para teste, começando em **2026-10-04 00:00:00**.

A equação ajustada foi:

```text
Consumo estimado (W) = −1491,83
                      + 228,35 × temperatura_c
                      − 16,41 × umidade_pct
```

Mantendo a outra variável constante, +1 °C está associado a +228,35 W e +1 ponto percentual de
umidade a −16,41 W no ajuste. O intercepto representa o valor matemático com entradas iguais a zero,
condição fora das faixas observadas, sem interpretação física direta neste estudo.

O coeficiente negativo da umidade não prova que aumentar umidade reduz consumo. O modelo agrupa
módulos com características diferentes e contém picos, o que pode alterar a interpretação dos coeficientes.
Ele não recupera necessariamente os parâmetros usados para gerar a base sintética.

### 6.4 Avaliação e apoio à decisão

Resultados apresentados no terminal pela equipe:

| Métrica | Valor |
|---|---:|
| MAE | 589,07 W |
| MSE | 784.937,04 W² |
| RMSE | 885,97 W |
| R² no teste | 0,355 |
| MAE da referência pela média do treino | 555,51 W |

MAE e RMSE expressam erros em watts; o MSE está em watts ao quadrado e penaliza erros grandes.
R² não é porcentagem de acertos. Seu valor descreve a redução do erro quadrático em relação à
referência da média do próprio conjunto de teste usada na definição dessa métrica.

**O modelo não superou a previsão constante pela média do treino em MAE.** Assim, não foi demonstrada
vantagem preditiva nessa métrica nem adequação para controle operacional. A comparação de MAE e o R²
utilizam referências diferentes, portanto não são resultados contraditórios.

São gerados `analise_exploratoria.png`, `regressao.png` e `residuos.png`. Resíduos são observados menos
previstos. Padrões, dispersão variável e erros extremos devem ser examinados; os gráficos, por si só,
não demonstram atendimento a todas as hipóteses estatísticas da regressão.

Para condições ilustrativas de 22,51 °C e 40,4% de umidade, o sistema estimou aproximadamente
2.985,2 W. Trata-se de estimativa condicional, não de previsão de um ciclo futuro, de um módulo
específico calibrado separadamente ou de risco de falha. O MAE não constitui intervalo de confiança
nem limite garantido de erro. Entradas fora das faixas individuais do treino são rejeitadas; estar dentro
dessas faixas não garante que a combinação tenha sido observada ou que a estimativa seja confiável.

O uso proposto é discutir planejamento energético e necessidades de revisão. Antes de orientar mudanças,
seriam necessários mais dados, validação externa e melhoria do desempenho. Alterações no banco podem
modificar os resultados apresentados nesta seção.



## 7. Agentes, guardrails e integração de IA (Integrante 2) | **Requisito  5.6**

A proposta implementa uma simulação de arquitetura multiagente com
funções Python em `src/fase7_sifsm/agentes.py`. Não há LLM, Agents SDK, RAG, webhook ou plataforma
low-code em execução nesse fluxo.

### 7.1 Papéis e ferramentas

| Agente | Responsabilidade | Ferramenta ou fonte |
|---|---|---|
| Triador | Identificar o assunto por palavras-chave e encaminhar | Regras de roteamento |
| Energia | Explicar estimativa de consumo e seus limites | `ferramenta_prever_consumo` → `modelo_linear.py` |
| Manutenção | Apresentar risco da última leitura e orientação consultiva | `ferramenta_classificar_risco` → `logica.py` |
| Dados | Informar quantidade e data dos registros consultados | `ferramenta_consultar_leituras` → `banco.py` |

Uma solicitação sobre bateria remete à opção 8, sem inventar telemetria. O triador não calcula o risco:
transfere o atendimento ao especialista, que utiliza a ferramenta. Esse encaminhamento é o handoff
simulado. Não há interpretação livre de linguagem natural.

### 7.2 Fluxo determinístico e memória

```text
Entrada → guardrail de entrada → triador → handoff → especialista
        → ferramenta determinística → explicação padrão
        → guardrail de saída → resposta + histórico + tracing
```

A sessão mantém o módulo informado para consultas seguintes. Exemplo: após `consumo MOD-01`,
a pergunta `e o risco?` reutiliza esse módulo. Um código inexistente não substitui o contexto válido.
A consulta `dados de todos os módulos` remove o filtro de módulo.

O histórico mantém até 20 interações aceitas e a trilha, até 100 eventos. Ambos ficam em memória,
sem gravação em disco. Pedidos rejeitados não são armazenados no histórico. Histórico textual ainda
pode conter informações digitadas em pedidos aceitos; por isso a equipe deve usar apenas dados fictícios
na demonstração e limpar a sessão quando necessário.

O menu pode oferecer atalhos numerados, consulta textual e os comandos `historico`, `trilha`, `limpar`
e `sair`. Os atalhos devem encaminhar ao mesmo fluxo, sem contornar guardrails e ferramentas.

### 7.3 Guardrails, segurança e responsabilidade humana

O guardrail de entrada verifica texto vazio, limite de 1.000 caracteres, escopo e termos relacionados
a ações perigosas, alterações de registros ou credenciais. O de saída rejeita determinadas alegações
de ação executada ou certeza indevida e exige menção à validação humana.

São verificações heurísticas: podem rejeitar frases inocentes e deixar passar formulações inesperadas.
Não garantem segurança completa nem verificam toda a fidelidade factual de uma resposta.
A barreira principal é estrutural: as ferramentas expostas aos agentes só consultam e calculam;
não cadastram, alteram ou excluem registros, nem operam suporte de vida ou outros equipamentos.

A classificação de risco permanece na regra booleana. A regressão apenas estima consumo e sua avaliação
insatisfatória em MAE é comunicada pelo especialista de energia. Nenhuma recomendação equivale a autorização
para atuar. A validação humana é uma responsabilidade externa ao protótipo, não um fluxo de aprovação
operacional implementado.

### 7.4 Integração opcional com LLM e fallback

O projeto possui `src/core/ia.py` como ponto de integração opcional com Gemini. Neste fluxo, a integração
é uma proposta conceitual; não se afirma que os agentes revisados chamam esse módulo.

```text
Entrada validada → triador → especialista → ferramentas determinísticas
→ resultados calculados + explicação padrão
→ Gemini opcional, apenas para redigir explicação
→ verificar preservação dos resultados e limites
→ guardrail de saída → resposta

Sem chave, com falha ou com resposta rejeitada:
explicação determinística → guardrail de saída → resposta
```

Uma implementação futura precisaria verificar que o texto preserva valores e classificações, não inventa
fontes ou autoriza ações. O guardrail atual não faz sozinho essa verificação. O LLM não receberia poderes
para alterar regras, dados ou equipamentos. O funcionamento básico continuaria independente de API.



## 8. Arquitetura computacional, processamento e aceleração (Integrante 3) | **Requisito 5.7**

### 8.1 Execução local e escolha de processamento

Para 120 leituras, uma CPU convencional é suficiente para consultas SQLite, regras, estruturas de dados,
simulação, regressão e agentes por regras. O armazenamento local evita serviço remoto obrigatório.
Não foram realizados benchmarks para demonstrar consumo energético, latência ou superioridade de hardware.

| Unidade | Relação com o SIFSM |
|---|---|
| CPU | Executa o fluxo geral, consultas, validações e cálculos da demonstração. |
| GPU | Poderia beneficiar cálculos matriciais e grandes lotes paralelos em escala maior, dependendo da carga. |
| NPU | Poderia atender inferência local de modelos compatíveis, caso uma evolução adotasse esse recurso. |
| TPU | Acelerador especializado para cargas tensoriais compatíveis; não necessário nem utilizado no protótipo. |

Não se justifica exigir aceleradores para esta amostra sem medir benefício. Em escala maior, uma arquitetura
heterogênea poderia manter consultas e regras na CPU e encaminhar operações paralelizáveis à unidade adequada.
Isso exigiria analisar compatibilidade, transferências, custo de inicialização e utilização real do dispositivo.

### 8.2 Memória, dados e sustentabilidade computacional

O caminho armazenamento → RAM → processamento envolve custo de acesso e movimentação. Caches reduzem
acessos repetidos à RAM, mas bases maiores podem exigir consultas por período, seleção de colunas e processamento
em lotes. A consulta sem limite é adequada à pequena base didática; não representa a estratégia ideal para
uma base de produção crescente.

Repetir treino a cada pedido do assistente é simples para demonstrar o fluxo, mas pode ser ineficiente em escala.
Uma evolução manteria um modelo validado em memória e o atualizaria quando os dados mudassem, com controle
de versão. Paralelizar tarefas muito pequenas ou copiar matrizes entre CPU e GPU pode custar mais que o cálculo.

Chiplets permitem compor unidades em um mesmo encapsulamento, mas sua presença não garante benefício ao SIFSM.
O critério seria medir tempo, memória, energia e custo para a carga real. Reduzir cópias, chamadas remotas e
processamento desnecessário é uma orientação de projeto; não há redução ambiental medida no protótipo.



## 9. Sustentabilidade, cidadania digital e impacto socioambiental (Integrante 3) | **Requisito 5.8**

### 9.1 Uso responsável dos recursos

Banco, regra e simulação relacionam registros de potência, condição dos módulos e energia acumulada.
O cenário de redução atua apenas sobre cópias dos dados dos módulos não essenciais. A classificação de risco
preserva critérios explícitos para módulos essenciais e suspende decisões sobre sensores inválidos.
A indicação não essencial deve ser revista por humanos antes de qualquer intervenção real.

### 9.2 Prevenção de desperdícios por simulação

Comparar cenários permite discutir alternativas antes de implantar alterações físicas. O resultado em Wh
quantifica uma hipótese, sem confundi-la com economia realizada. Dados de falha e lacunas limitam a confiança;
validar medições é parte do uso responsável da informação.

### 9.3 Armazenamento, resiliência e autonomia

Carga e déficit da bateria permitem discutir insuficiência de geração e necessidade de contingência.
Uma colônia real precisaria considerar redes inteligentes, redundância, prioridades e armazenamento com perdas.
Esses elementos são perspectivas de evolução; o protótipo não implementa uma rede elétrica inteligente.

### 9.4 Cidadania digital, privacidade e transparência

A demonstração utiliza dados simulados, sem necessidade de informações pessoais da tripulação. Histórico
limitado e limpeza de sessão reduzem retenção. Regras, métricas e tracing tornam o fluxo explicável.
Uma versão real exigiria controle de acesso, políticas de retenção e revisão dos registros exibidos no vídeo.
O SQLite local, sozinho, não garante confidencialidade ou autorização.

### 9.5 Economia dos dados e risco de uso indevido

Dados de consumo e solicitações poderiam permitir inferir presença, rotina ou condições de pessoas caso
fossem associados a identidades. Reutilizá-los para vigilância, discriminação ou finalidade não informada
seria um risco. Uma evolução deve minimizar identificação, definir finalidade e limitar compartilhamento,
especialmente ao considerar envio a serviços de IA.

### 9.6 Impacto ambiental de IA e processamento

O funcionamento sem LLM remoto evita chamadas externas obrigatórias e facilita execução local. Isso não
significa impacto zero nem comprova menor emissão: equipamentos locais e data centers consomem energia
e recursos. Uma integração com Gemini deveria considerar volume, necessidade, retenção de dados e custos.
Treinar repetidamente um modelo sem mudança nos dados também deve ser evitado em escala.

### 9.7 Benefícios, riscos e inovação responsável

A principal contribuição é integrar conceitos e tornar as limitações visíveis. A regressão que não supera
a referência pela média mostra por que inovação exige avaliação, e não apenas uma previsão numérica.
Separar cálculo, explicação e autorização reduz a chance de transformar uma resposta textual em ação crítica.
Não se declara que os guardrails garantem segurança ou que o sistema é apto para operação real.

### 9.8 Diversidade, inclusão e responsabilidade social

Atalhos guiados e exemplos de códigos de módulos podem reduzir a dificuldade de uso do assistente.
Mensagens devem evitar jargões e não depender apenas de cores. O menu textual ainda precisa ser avaliado
com leitores de tela, diferentes níveis de experiência e necessidades de acessibilidade.
Priorização de chamados e decisões de recurso devem ser transparentes e revisáveis, sem discriminação.
Uma fila FIFO organiza ordem de chegada; urgências exigem critérios próprios de prioridade, sem presumir
que ordem de chegada seja suficiente para todas as situações.



## 10. Limitações e melhorias 

| Limitação atual | Consequência | Possível melhoria |
|---|---|---|
| Base sintética e pequena | Não valida ambiente real nem generalização | Coletar dados representativos e validar sensores. |
| Lacunas e leituras em falha na simulação | Energia pode representar medições não confiáveis | Definir critérios de qualidade e política explícita de imputação ou exclusão. |
| Bateria ideal e geração constante | Autonomia não incorpora perdas ou clima | Incluir eficiência, geração variável e limites de potência. |
| Regressão não supera a média em MAE | Sem vantagem demonstrada nessa métrica | Avaliar modelos por módulo, mais dados e atributos justificados. |
| Diferenças entre módulos e picos | Coeficientes podem ser difíceis de interpretar | Analisar estratos, resíduos e estabilidade dos coeficientes. |
| Guardrails por palavras-chave | Falsos bloqueios e pedidos não detectados | Combinar validações estruturadas, avaliação e revisão humana. |
| Sessão apenas em memória | Contexto se perde ao sair | Persistência opcional, com retenção e controle de acesso definidos. |
| Ausência de atuação física e autorização operacional | Não controla a colônia | Manter consulta separada de eventual atuação validada e auditada. |
| Sem benchmarks ou avaliação de acessibilidade | Benefícios computacionais e inclusão não comprovados | Medir tempo, memória e energia; realizar testes com usuários. |



## 11. Como executar 
Pré-requisito: Python 3.12 ou superior. Na raiz do projeto, em PowerShell:

```powershell
# Apenas se o ambiente ainda não existir:
py -3.12 -m venv venv

.\venv\Scripts\python.exe -m pip install numpy pandas matplotlib scikit-learn pytest python-dotenv
.\venv\Scripts\python.exe codigo_fonte.py
```

SQLite, `datetime`, `math`, `pathlib`, `dataclasses`, `re`, `sqlite3` e `unicodedata` pertencem à biblioteca
padrão. Pandas e NumPy apoiam a modelagem, scikit-learn ajusta a regressão, Matplotlib gera gráficos e
pytest executa os testes. O fluxo dos agentes não exige arquivo `.env`, chave Gemini ou acesso à internet.
As fases anteriores podem ter dependências adicionais, distintas do fluxo da Fase 7.

Na primeira execução, o menu cria o banco em `data/fase7/aurora_siger.db` e importa o CSV se a tabela de
leituras estiver vazia. Alterações de CRUD persistem no banco e podem mudar os resultados. Não se deve
apagar um banco com alterações importantes apenas para reproduzir métricas.




## 12. Testes e evidências disponíveis

```powershell
.\venv\Scripts\python.exe -m pytest -q
.\venv\Scripts\python.exe -m py_compile src/fase7_sifsm/simulacao.py src/fase7_sifsm/modelo_linear.py src/fase7_sifsm/agentes.py
```

A equipe confirmou 37 testes passando na base do Integrante 1. Foi apresentada a saída completa da opção 9,
com métricas registradas na seção 6, e a abertura do assistente. A revisão do código de simulação verificou
casos controlados de integral constante, comparação, interpolação e esgotamento; isso não substitui a validação
final do repositório integrado. Os testes adicionais fornecidos devem ser incorporados e executados antes
de registrar uma contagem final. Não se declara neste relatório que toda a suíte ampliada passou.

As figuras esperadas em `docs/fase7/graficos_ou_imagens/` são:

- `consumo_cenarios.png` e `bateria.png`;
- `analise_exploratoria.png`, `regressao.png` e `residuos.png`.

Na revisão final, conferir legibilidade e correspondência entre gráficos, banco e resultados. O registro
final dos testes, evidências do CRUD e execução da opção A ainda deve ser consolidado pela equipe.



## 13. vídeo

O vídeo pitch da Fase 7 apresenta o funcionamento do SIFSM, as principais decisões técnicas e os resultados obtidos. 
Está disponível no YouTube, na modalidade “Não listado”, pelo link [inserir link do vídeo], também registrado no arquivo `link_video.txt`.




