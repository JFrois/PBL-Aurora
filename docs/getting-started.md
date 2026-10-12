# 🚀 Guia Rápido de Instalação & Sequência de Lançamento

<span class="mission-patch">OPERATIONS</span>
<span class="mission-patch cyan">QUICKSTART</span>
<span class="mission-patch green">PYTHON 3.12+</span>

Este guia fornece o passo a passo para clonar, configurar as variáveis de ambiente, instalar dependências e inicializar a **Missão Aurora Siger** tanto no modo CLI do terminal quanto no portal de documentação local.

---

## 1. Pré-Requisitos do Sistema

Certifique-se de que sua estação de trabalho atende aos requisitos mínimos:

- **Python**: Versão `>= 3.12`
- **Gerenciador de Pacotes Python**: `uv` (recomendado pela velocidade) ou `pip` tradicional
- **Node.js**: Versão `>= 18.0` (necessário para rodar a documentação localmente)
- **Git**: Para controle de versão e envio de branches

---

## 2. Clonagem e Configuração do Ambiente

```bash
# 1. Clone o repositório
git clone https://github.com/JFrois/PBL-Aurora.git
cd PBL-Aurora

# 2. Crie e ative o ambiente virtual
# Utilizando uv (rápido):
uv venv
source .venv/bin/activate   # Linux/macOS
# ou .venv\Scripts\activate # Windows

# Ou utilizando python venv padrão:
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Instalação das Dependências

### Dependências Python da Missão
```bash
# Com uv:
uv pip install -r requirements.txt

# Ou com pip tradicional:
pip install -r requirements.txt
```

### Dependências da Documentação (VitePress)
```bash
npm install
```

---

## 4. Configuração das Variáveis de Ambiente (.env)

Copie o arquivo de exemplo e configure sua chave de API para o subsistema de IA generativa (Google Gemini):

```bash
cp .env.example .env
```

Edite o arquivo `.env`:
```ini
# Chave de API do Google Gemini (IA Generativa)
GEMINI_API_KEY="sua_chave_aqui"

# Modelo Gemini recomendado (padrão: gemini-3.1-flash-lite)
GEMINI_MODEL="gemini-3.1-flash-lite"
```

::: tip [TELEMETRIA: OPERAÇÃO AUTÔNOMA SEM IA]
A chave `GEMINI_API_KEY` é opcional. Se a variável não estiver preenchida ou a conexão falhar, o sistema executará normalmente utilizando **respostas locais simuladas** e regras heurísticas da base marciana.
:::

---

## 5. Execução do Sistema

### Modo 1: Orquestrador Geral e Máquina de Estados (CLI Interativa)
Apresenta o painel completo da missão com as 6 fases e análise integrada:
```bash
python main.py
# ou com uv:
uv run python main.py
```

### Modo 2: Execução Direta da Fase 6 (SCIC - Modo Automático)
Executa o pipeline completo (dados -> regressão -> heap -> trie) sem interrupções de menu:
```bash
python -m src.fase6_scic.fase6_scic --auto
```

### Modo 3: Menu Interativo da Fase 6 (SCIC)
Permite navegar isoladamente pelas opções de análise de hardware, métricas de regressão, fila de alertas e busca por prefixo na Trie:
```bash
python -m src.fase6_scic.fase6_scic
```

---

## 6. Execução dos Testes Automatizados

Valide as estruturas de dados críticas executando a suíte de testes com `pytest`:

```bash
pytest tests/
# ou utilizando o interpretador do ambiente virtual:
.venv/bin/pytest
```

---

## 7. Servidor Local da Documentação (VitePress)

Para visualizar o portal de documentação com tema marciano e recarregamento automático (HMR):

```bash
npm run docs:dev
```

Acesse o endereço exibido no terminal (geralmente `http://localhost:5173/`). Para gerar a versão de produção:

```bash
npm run docs:build
npm run docs:preview
```
