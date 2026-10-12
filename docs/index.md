---
layout: home

hero:
  name: "MISSÃO AURORA SIGER"
  text: "Centro de Comando & Engenharia de Sistemas em Marte"
  tagline: "Plataforma integrada de simulação aeroespacial, análise de telemetria, núcleo cognitivo e monitoramento da colônia marciana."
  image:
    src: /mars_patch.jpg
    alt: Insígnia da Missão Aurora Siger
  actions:
    - theme: brand
      text: "🚀 Iniciar Missão (Guia Rápido)"
      link: "/getting-started"
    - theme: alt
      text: "🛰️ Blueprint da Arquitetura"
      link: "/architecture"

features:
  - icon: "⚡"
    title: "Telemetria & Pré-Decolagem (Fase 1)"
    details: "Validação de limites físicos (temperatura, pressão, bateria e integridade) em 3 rodadas consecutivas para autorização de lançamento (GO / NO-GO)."
    link: "/fases/fase-1-telemetria"
  - icon: "🛬"
    title: "Aproximação e Pouso MGPEB (Fase 2)"
    details: "Gerenciamento de descida orbital com Insertion Sort por criticidade de módulos, filas FIFO e mitigação de clima marciano extremo."
    link: "/fases/fase-2-pouso"
  - icon: "🌪️"
    title: "Matriz Energética SIC (Fase 3)"
    details: "Modelagem eólica via Regressão Linear Simples por Mínimos Quadrados, cálculo de R² e corte seletivo automatizado de carga."
    link: "/fases/fase-3-energia"
  - icon: "🕸️"
    title: "Infraestrutura SIGIC (Fase 4)"
    details: "Topologia da base modelada como Grafo Ponderado, Matriz de Adjacência, cálculo de distâncias euclidianas e latência de rede interna."
    link: "/fases/fase-4-infraestrutura"
  - icon: "🧠"
    title: "Núcleo Cognitivo NCAS (Fase 5)"
    details: "Lógica proposicional simplificada com Leis de De Morgan, persistência estruturada em JSON/TXT e IA Generativa (Google Gemini) com fallback resiliente."
    link: "/fases/fase-5-cognitivo"
  - icon: "🔬"
    title: "SCIC: Hardware & ML (Fase 6)"
    details: "Dimensionamento via Lei de Ohm, previsão de latência com scikit-learn, fila de prioridade com Heap binário e busca em O(m) com Trie."
    link: "/fases/fase-6-scic"
---

<div class="hud-telemetry-banner">
  <div class="hud-item">
    <span class="hud-dot live"></span>
    <span class="hud-label">STATUS DA BASE</span>
    <span class="hud-val green">NOMINAL (GO)</span>
  </div>
  <div class="hud-item">
    <span class="hud-label">LOCALIZAÇÃO</span>
    <span class="hud-val cyan">CRATERA JEZERO · MARTE</span>
  </div>
  <div class="hud-item">
    <span class="hud-label">SOL MARCIANO</span>
    <span class="hud-val amber">SOL 142.6</span>
  </div>
  <div class="hud-item">
    <span class="hud-label">PRESSÃO ATM</span>
    <span class="hud-val">0.63 kPa</span>
  </div>
  <div class="hud-item">
    <span class="hud-label">TEMP AMBIENTE</span>
    <span class="hud-val">-63.4 °C</span>
  </div>
  <div class="hud-item">
    <span class="hud-label">ENLACE TERRA</span>
    <span class="hud-val cyan">14m 22s ATRASO</span>
  </div>
</div>

<div class="mars-grid-overlay">

## 🛰️ Mission Briefing (Visão Geral da Missão)

<span class="mission-patch">ARES MISSION</span>
<span class="mission-patch cyan">ORBITAL TELEMETRY</span>
<span class="mission-patch green">STATUS: OPERACIONAL</span>
<span class="mission-patch amber">SOL 142</span>

A **Missão Aurora Siger** representa um marco no desenvolvimento de software crítico para exploração espacial autônoma. Desenvolvida no âmbito do **Project Based Learning (PBL)** da **FIAP**, a plataforma une rigor matemático, estruturas de dados de alta performance, modelos estatísticos de aprendizado de máquina e tomada de decisão cognitiva com inteligência artificial para viabilizar a sobrevivência e sustentabilidade da primeira base permanente em Marte.

<div class="metrics-grid">
  <div class="metric-box">
    <div class="metric-label">Módulos Conectados</div>
    <div class="metric-value">8 <span class="metric-unit">módulos</span></div>
  </div>
  <div class="metric-box">
    <div class="metric-label">Taxa de Disponibilidade</div>
    <div class="metric-value">98.4 <span class="metric-unit">%</span></div>
  </div>
  <div class="metric-box">
    <div class="metric-label">Latência Média de Rede</div>
    <div class="metric-value">18.7 <span class="metric-unit">ms</span></div>
  </div>
  <div class="metric-box">
    <div class="metric-label">Capacidade Energética</div>
    <div class="metric-value">6.8 <span class="metric-unit">kW / mod</span></div>
  </div>
</div>

---

## 📋 Launch Checklist (Protocolo Pré-Voo)

Antes de autorizar a ignição ou iniciar a máquina de estados, confirme os seguintes procedimentos:

::: tip [STATUS DA MISSÃO: VERIFICAÇÃO ATIVA]
- [x] **Ambiente Virtual**: Interpretador Python 3.12+ configurado via `uv` ou `.venv`.
- [x] **Dependências Matemáticas**: `numpy`, `pandas`, `scikit-learn` e `matplotlib` integrados.
- [x] **Subsistema de IA**: Chave de API Google Gemini (`GEMINI_API_KEY`) no arquivo `.env` (modo mock disponível automaticamente em caso de indisponibilidade de sinal).
- [x] **Suíte de Testes**: Execução de `pytest tests/` validando o Max-Heap e a Trie de Módulos.
:::

---

## 🗺️ Mapa de Navegação da Engenharia

| Módulo / Documento | Objetivo Operacional | Camada de Software |
|---|---|---|
| [Blueprint da Arquitetura](/architecture) | Visão sistêmica, diagramas de sequência e ADRs | Sistema & Decisões |
| [Guia Rápido de Instalação](/getting-started) | Setup do ambiente local, variáveis e execução | Operação CLI |
| [Fase 1: Telemetria](/fases/fase-1-telemetria) | 3 rodadas de verificação física e lógica GO / NO-GO | Validação de Entrada |
| [Fase 2: Pouso Marciano](/fases/fase-2-pouso) | MGPEB, Insertion Sort e mitigação climática | Ordenação & Filas |
| [Fase 3: Matriz Energética](/fases/fase-3-energia) | Regressão linear por mínimos quadrados e R² | Análise Numérica |
| [Fase 4: Infraestrutura & Redes](/fases/fase-4-infraestrutura) | Grafo da colônia, matriz de adjacência e latência | Teoria dos Grafos |
| [Fase 5: Núcleo Cognitivo](/fases/fase-5-cognitivo) | Leis de De Morgan, persistência JSON e LLMs | Lógica & IA |
| [Fase 6: Sistema Integrado SCIC](/fases/fase-6-scic) | Hardware, scikit-learn, Max-Heap e Trie | ML & Algoritmos |
| [Práticas de Engenharia](/engineering-practices) | Git Flow, Conventional Commits e pytest | Qualidade & QA |
| [Deploy & CI/CD](/deployment) | Workflow do GitHub Actions para GitHub Pages | DevOps & Entrega |

</div>
