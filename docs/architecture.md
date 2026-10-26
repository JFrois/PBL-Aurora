# 🛰️ Blueprint da Arquitetura & Registros de Decisão (ADR)

<span class="mission-patch">ARCHITECTURE</span>
<span class="mission-patch cyan">SYSTEM BLUEPRINT</span>
<span class="mission-patch green">STABLE</span>

A arquitetura da **Missão Aurora Siger** foi projetada seguindo os princípios de engenharia de software aeroespacial: **isolamento de módulos**, **resiliência operacional sem conexão contínua com a Terra**, **invariantes matemáticos verificáveis** e **acesso determinístico a dados críticos**.

---

## 1. Visão Geral do Sistema (Mission Blueprint)

O sistema é dividido em três camadas funcionais:
1. **Camada de Simulação & Hardware**: Emulação de sensores, registradores de hardware (hex/bin), limites termodinâmicos e elétricos (Lei de Ohm e Potência).
2. **Camada Analítica & Cognitiva**: Processamento de dados via Pandas, regressão linear e regularizada (Ridge com Grid Search), lógica booleana e geração de relatórios com LLM (Google Gemini).
3. **Camada de Estruturas de Dados & Decisão**: Fila de prioridade com Max-Heap binário para alertas em tempo real e Árvore de Prefixos (Trie) para indexação instantânea de comandos e telemetria.

```mermaid
graph TB
    subgraph Entrada["🛰️ Coleta de Telemetria & Simulação"]
        S1["Sensores Térmicos & Pressão"]
        S2["Barramento Elétrico (V, I, P)"]
        S3["Registradores Embarcados (Hex/Bin)"]
    end

    subgraph Core["⚙️ Processamento & Modelagem"]
        D1["dados.py (Limpeza & Validação Estrita)"]
        H1["hardware.py (Lei de Ohm & Diagnóstico)"]
        M1["modelagem.py (Regressão & Métricas MAE/RMSE/R²)"]
    end

    subgraph Decisao["🚨 Gestão de Eventos & Consulta"]
        HEAP["HeapAlertas (Max-Heap Binário O(log n))"]
        TRIE["TrieModulos (Árvore de Prefixos O(m))"]
    end

    subgraph Orquestracao["🖥️ Interface & Decisão Central"]
        CLI["main.py (Máquina de Estados Global)"]
        AI["Google GenAI (Relatórios Estruturados com Gemini)"]
    end

    Entrada --> D1
    D1 --> H1
    H1 --> M1
    M1 --> HEAP
    D1 --> TRIE
    HEAP --> CLI
    TRIE --> CLI
    CLI <--> AI
```

---

## 2. Pipeline de Execução e Ciclo de Vida dos Dados

O fluxo operacional do sistema une as etapas de geração de telemetria, modelagem estatística e alimentação das estruturas de busca e priorização:

```mermaid
sequenceDiagram
    autonumber
    actor Operador as Operador de Missão
    participant Main as main.py / SCIC
    participant Dados as dados.py
    participant Hardware as hardware.py
    participant ML as modelagem.py
    participant Heap as estruturas.py (Heap)
    participant Trie as estruturas.py (Trie)

    Operador->>Main: Iniciar Fase 6 (SCIC)
    Main->>Dados: gerar_dataset_telemetria()
    loop Para cada um dos 8 módulos × 15 ciclos
        Dados->>Hardware: calcular_potencia(V, I)
        Hardware-->>Dados: P = V * I (Watts)
        Dados->>Hardware: decodificar_registrador_telemetria(Hex)
        Hardware-->>Dados: Hex -> Dec -> Bin (8-bit)
    end
    Dados->>Dados: limpar_dataset() e verificar_problemas()
    Dados-->>Main: dados_aurora_siger.csv (120 registros)

    Main->>ML: executar_fase6_analista2(df)
    ML->>ML: Treinar Regressão Linear / Ridge
    ML->>ML: Calcular Erro Absoluto e Relativo
    ML-->>Main: dados_aurora_siger_com_previsao.csv + Gráficos

    Main->>Heap: carregar HeapAlertas(csv_com_previsoes)
    Heap-->>Main: Heap montado (Alertas ordenados por criticidade)

    Main->>Trie: construir_trie(df, comandos)
    Trie-->>Main: Trie indexada (Módulos, Sensores e Comandos)

    Operador->>Main: Consultar Alerta Crítico
    Main->>Heap: extrair_max()
    Heap-->>Main: Alerta de Maior Criticidade O(log n)
    Main-->>Operador: Exibir Diagnóstico e Plano de Ação
```

---

## 3. Modelagem de Dados & Diagrama de Classes

```mermaid
classDiagram
    class Modulo {
        +string modulo_id
        +string nome_modulo
        +string tipo_modulo
        +bool essencial
        +float potencia_w
        +float limite_potencia_w
        +float latencia_observada_ms
        +float latencia_prevista_ms
        +string status_operacional
        +int prioridade
    }

    class Alerta {
        +int id
        +int pontuacao_criticidade
        +string modulo
        +string tipo_problema
        +string gravidade
        +float latencia_ms
        +float erro_relativo_pct
        +bool essencial
        +calcular_criticidade() int
    }

    class HeapAlertas {
        -list~Alerta~ heap
        +inserir(Alerta) void
        +extrair_max() Alerta
        +espiar() Alerta
        +tamanho() int
        -_subir(indice) void
        -_descer(indice) void
    }

    class TrieNode {
        +dict filhos
        +bool fim_da_palavra
        +list dados
    }

    class TrieModulos {
        -TrieNode raiz
        +inserir(chave, dados) void
        +buscar_por_prefixo(prefixo) list
        -_coletar_todos(no) list
    }

    HeapAlertas "1" *-- "*" Alerta : Gerencia fila de prioridade
    TrieModulos "1" *-- "*" TrieNode : Nós de busca
    Modulo --> Alerta : Dispara evento de sobrecarga/latência
```

---

## 4. Registros de Decisão Arquitetural (ADRs)

### ADR-001: Utilização de Max-Heap Binário para Gestão de Alertas Críticos
* **Contexto**: A colônia marciana opera sob telemetria contínua. Em situações de emergência (tempestade de areia, fuga térmica, sobrecarga em barramento), dezenas de alarmes chegam simultaneamente. A equipe precisa tratar imediatamente a falha com maior potencial catastrófico.
* **Alternativas Analisadas**:
  1. *Lista não ordenada*: Inserção $O(1)$, mas busca pelo alerta mais grave exige varredura completa $O(n)$.
  2. *Lista ordenada*: Extração $O(1)$, porém inserção exige deslocamento de elementos $O(n)$.
  3. *Max-Heap Binário*: Inserção em $O(\log n)$, extração em $O(\log n)$ e consulta do topo em $O(1)$.
* **Decisão**: Implementar `HeapAlertas` usando max-heap binário nativo com cálculo auditável de criticidade ponderada.
* **Consequência**: Garantia de tempo quase-constante para atendimento a emergências de suporte à vida.

---

### ADR-002: Indexação em Tempo de Execução via Árvore de Prefixos (Trie)
* **Contexto**: Operadores no terminal CLI precisam consultar rapidamente módulos (`MOD-01`, `MOD-02`), sensores hexadecimais (`0x2A`) ou comandos do console digitando prefixos abreviados.
* **Decisão**: Implementar `TrieModulos`, indexando os nomes dos módulos, identificadores, códigos de sensores e comandos do sistema.
* **Consequência**: O tempo de localização depende estritamente do tamanho do prefixo digitado $O(m)$ e não da quantidade total de módulos $O(n)$.

---

### ADR-003: Resiliência da Integração com LLM (Google Gemini) com Fallback Offline
* **Contexto**: A missão em Marte está sujeita a quedas no enlace de comunicação interplanetária (Blackout de rádio ou atrasos de sinal de até 22 minutos).
* **Decisão**: Toda chamada à API do Gemini (`google-genai`) possui tratamento de exceção estruturado e chave opcional. Se a chave não existir ou a rede falhar, o sistema reverte automaticamente para regras heurísticas locais de diagnóstico e análise sintética, sem travar a máquina de estados.
* **Consequência**: Sistema 100% tolerante a falhas de conectividade.

---

### ADR-004: Adoção do VitePress com Tema Marciano para Documentação Técnica
* **Contexto**: A documentação precisava combinar alta performance, dark mode temático imersivo, renderização nativa de diagramas Mermaid e deploy automatizado no GitHub Pages.
* **Decisão**: Adotar VitePress com plugin Mermaid nativo e tokens CSS inspirados em telemetria espacial marciana.
* **Consequência**: Carregamento instantâneo em qualquer navegador, suporte a busca offline e atualização contínua via GitHub Actions.
