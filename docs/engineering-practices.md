# ⚙️ Práticas de Engenharia, Qualidade & Governança

<span class="mission-patch">QUALITY</span>
<span class="mission-patch cyan">ENGINEERING STANDARDS</span>
<span class="mission-patch green">PYTEST CERTIFIED</span>

O desenvolvimento da **Missão Aurora Siger** segue rigorosos padrões de engenharia de software para assegurar que sistemas críticos para a vida e a comunicação na colônia marciana mantenham alta disponibilidade, reprodutibilidade e rastreabilidade.

---

## 1. Estratégia de Branching (Git Flow Aeroespacial)

Utilizamos um modelo adaptado de Git Flow para organizar as entregas:

```text
main (produção / entregas estáveis)
  └── feat/docs (documentação e infraestrutura de páginas)
  └── feat/fase-6-scic (desenvolvimento de estruturas e ML)
  └── fix/heap-balance (correções críticas de prioridade)
```

- **`main`**: Código aprovado em banca, estável e testado.
- **`feat/*`**: Branches de funcionalidade (novos algoritmos, modelagens estatísticas ou expansões de telemetria).
- **`fix/*`**: Correções urgentes de anomalias detectadas em testes.

---

## 2. Convenção de Commits (Conventional Commits)

As mensagens de commit devem seguir o padrão Conventional Commits para alimentar changelogs automáticos:

| Prefixo | Finalidade Operacional | Exemplo |
|---|---|---|
| `feat` | Nova funcionalidade ou módulo de missão | `feat(scic): implementar busca por prefixo via Trie` |
| `fix` | Correção de bug ou anomalia de cálculo | `fix(hardware): corrigir arredondamento da Lei de Ohm` |
| `docs` | Alterações na documentação técnica | `docs: adicionar diagramas de sequência da arquitetura` |
| `test` | Criação ou refatoração de testes | `test(heap): validar extração com prioridades empatadas` |
| `refactor` | Melhoria de código sem alterar regra de negócio | `refactor(dados): otimizar geração do dataset com RNG fixo` |

---

## 3. Padrões de Código Python (PEP 8 & Tipagem)

- **Python 3.12+**: Uso de type hints estritos (`typing.Union`, `typing.Optional`, `typing.Dict`).
- **Nomes Significativos**: Funções declarativas (`calcular_resistencia`, `diagnosticar_circuito`, `decodificar_registrador_telemetria`).
- **Tratamento de Exceções**: Erros explícitos (`ValueError`, `ZeroDivisionError`) com mensagens orientadas ao diagnóstico do operador.
- **Formatação**: Código compatível com formatadores modernos (`ruff` e `black`) com largura máxima de 88/100 caracteres.

---

## 4. Suíte de Testes Automatizados (pytest)

Os testes estão localizados no diretório `tests/` e cobrem os invariantes fundamentais das estruturas de dados do SCIC.

### Execução dos Testes:
```bash
pytest tests/ -v
```

### Casos de Teste Atuais (`tests/test_estruturas.py`):
1. **`test_heap_insere_e_extrai_em_ordem`**: Valida se o alerta de maior criticidade é sempre extraído primeiro.
2. **`test_heap_topo_sem_remover`**: Garante que o método de espiar o topo não altera a quantidade de elementos.
3. **`test_trie_busca_exata`**: Confirma que termos exatos (ex: `MOD-01`) retornam os dados corretos do módulo.
4. **`test_trie_busca_por_prefixo`**: Verifica se prefixos (ex: `MOD-` ou `0x`) listam todos os nós correspondentes.
5. **`test_trie_busca_inexistente`**: Garante retorno de lista vazia sem levantar exceções não tratadas.
6. **`test_trie_sensibilidade_a_maiusculas`**: Valida a normalização de texto e insensibilidade a caixa alta/baixa.

::: tip [TELEMETRIA: REPRODUTIBILIDADE MATEMÁTICA]
A geração de dados em `dados.py` utiliza semente fixa (`numpy.random.default_rng(seed=42)`), garantindo que qualquer rodada de testes unitários ou simulação produza exatamente os mesmos 120 registros em 15 ciclos.
:::

---

## 5. Observabilidade & Logs Operacionais

O sistema implementa múltiplos níveis de rastreabilidade:
- **Terminal CLI com Estética de Telemetria**: Bordas com larguras padronizadas (80 e 85 caracteres) para legibilidade em monitores espaciais.
- **Persistência de Dados**:
  - `data/processed/dados_aurora_siger.csv`: Telemetria bruta validada.
  - `data/processed/dados_aurora_siger_com_previsao.csv`: Telemetria enriquecida com erro absoluto, relativo e previsão de latência.
  - `data/processed/registros_colonia.txt`: Log sequencial textual de ocorrências.
  - `data/processed/dados_colonia.json`: Estado relacional em formato JSON dos módulos.
