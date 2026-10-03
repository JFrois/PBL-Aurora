"""
Módulo de Estruturas de Dados Avançadas — Peps Bonitão
Fase 6: SCIC (Missão Aurora Siger)

Responsabilidades:
- HeapAlertas: fila de prioridade (max-heap) que organiza os alertas da colônia
  pela criticidade, garantindo que o alerta mais urgente seja tratado primeiro.
- TrieModulos: árvore de prefixos para localizar rapidamente módulos, tipos,
  códigos de sensor (hex) e comandos do sistema a partir de um prefixo digitado.

Entradas (geradas pelos Analistas 1 e 2):
- dados_aurora_siger.csv              -> status_operacional, prioridade, mensagem_alerta...
- dados_aurora_siger_com_previsao.csv -> erro_relativo_pct, faixa_erro (ACEITÁVEL/ATENÇÃO/PREOCUPANTE)

Por que Heap e não uma lista comum?
- Lista NÃO ordenada: inserir é O(1), mas achar/remover o mais crítico exige
  percorrer tudo -> O(n) por extração.
- Lista ORDENADA: extrair é O(1), mas cada inserção precisa deslocar elementos
  para manter a ordem -> O(n) por inserção.
- Heap binário: inserir e extrair são O(log n), e consultar o topo é O(1).
  Com alertas chegando continuamente (telemetria em tempo real), o heap
  mantém o custo baixo nas DUAS operações.

Por que Trie?
- A busca por prefixo numa lista exige comparar o prefixo com todas as
  n chaves -> O(n · m). Na Trie, o custo para chegar ao nó do prefixo é
  O(m) (m = tamanho do prefixo), independente de quantos módulos existam;
  depois só se percorre a subárvore com as respostas (O(m + k)).
"""

import time
import random
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAIZ_PROJETO = BASE_DIR.parent.parent
CSV_PREVISOES = RAIZ_PROJETO / "data" / "processed" / "dados_aurora_siger_com_previsao.csv"

# =====================================================================
# PESOS DA CRITICIDADE (regra transparente e auditável)
# =====================================================================
# Cada alerta recebe uma pontuação. Quanto MAIOR, mais urgente.
PESO_STATUS = {"alerta": 40, "manutencao": 10, "ativo": 0}
PESO_MENSAGEM = {
    "Sobrecarga de potência no barramento": 30,  # risco elétrico/incêndio
    "Radiação elevada no módulo": 25,  # risco à saúde da tripulação
    "Latência acima do previsto": 20,  # risco de perda de comando
    "Manutenção preventiva agendada": 5,
    "Operação nominal": 0,
}
PESO_FAIXA_ERRO = {"PREOCUPANTE": 20, "ATENÇÃO": 8, "ACEITÁVEL": 0}
PESO_ESSENCIAL = 15  # suporte à vida / comunicação / controle
PESO_PRIORIDADE = 5  # multiplicado pela prioridade (1 a 4)

# Comandos do menu indexados na Trie (busca por prefixo de comandos)
COMANDOS_SISTEMA = {
    "alertas": "Exibe a fila de alertas críticos (Heap)",
    "atender": "Atende (remove) o alerta mais crítico da fila",
    "buscar": "Busca módulos/sensores por prefixo (Trie)",
    "benchmark": "Compara Heap x lista comum",
    "diagnosticar": "Diagnóstico elétrico de um circuito (P = V x I)",
    "decodificar": "Converte código de sensor hex -> dec -> bin",
    "metricas": "Mostra MAE, MSE, RMSE e R² do modelo",
    "modelo": "Treina a regressão linear de latência",
    "pipeline": "Executa o fluxo completo do SCIC",
    "status": "Resumo operacional da colônia",
}


# =====================================================================
# 1. HEAP DE ALERTAS (FILA DE PRIORIDADE)
# =====================================================================


@dataclass
class Alerta:
    """Representa um alerta operacional pronto para entrar na fila."""

    criticidade: float
    timestamp_id: int
    ciclo: int
    modulo_id: str
    nome_modulo: str
    codigo_sensor_hex: str
    status: str
    prioridade: int
    mensagem: str
    latencia_observada_ms: float = 0.0
    latencia_prevista_ms: float = 0.0
    erro_relativo_pct: float = 0.0
    faixa_erro: str = "-"
    potencia_w: float = 0.0
    limite_potencia_w: float = 0.0
    motivos: list = field(default_factory=list)

    def resumo(self):
        return (
            f"[{self.criticidade:6.1f}] ciclo {self.ciclo:>2} | {self.modulo_id} "
            f"{self.nome_modulo:<24} | {self.codigo_sensor_hex} | {self.mensagem}"
        )


def calcular_criticidade(registro):
    """
    Calcula a pontuação de criticidade de um registro (dict ou linha do DataFrame).

    criticidade = status + tipo de alerta + faixa de erro do modelo
                + essencial + prioridade x 5 + excesso de potência + desvio de latência

    Retorna (pontuacao, lista_de_motivos) para que a decisão automática
    seja EXPLICÁVEL ao operador humano.
    """
    motivos = []
    status = str(registro.get("status_operacional", "ativo")).strip().lower()
    mensagem = str(registro.get("mensagem_alerta", "")).strip()
    faixa = str(registro.get("faixa_erro", "")).strip()

    pontos = PESO_STATUS.get(status, 0)
    if pontos:
        motivos.append(f"status={status}")

    p_msg = PESO_MENSAGEM.get(mensagem, 0)
    if p_msg:
        pontos += p_msg
        motivos.append(mensagem)

    p_faixa = PESO_FAIXA_ERRO.get(faixa, 0)
    if p_faixa:
        pontos += p_faixa
        motivos.append(f"erro do modelo {faixa}")

    if int(registro.get("essencial", 0)) == 1:
        pontos += PESO_ESSENCIAL
        motivos.append("módulo essencial")

    pontos += PESO_PRIORIDADE * int(registro.get("prioridade", 1))

    # Excesso de potência: cada 1% acima do limite soma 1 ponto
    potencia = float(registro.get("potencia_w", 0) or 0)
    limite = float(registro.get("limite_potencia_w", 0) or 0)
    if limite > 0 and potencia > limite:
        excesso = (potencia / limite - 1) * 100
        pontos += excesso
        motivos.append(f"potência {excesso:.1f}% acima do limite")

    # Desvio de latência observada x prevista (em %): meio ponto por 1%, teto de 40
    obs = float(registro.get("latencia_observada_ms", 0) or 0)
    prev = float(registro.get("latencia_prevista_ms", 0) or 0)
    if prev > 0 and obs > prev:
        desvio = (obs / prev - 1) * 100
        pontos += min(desvio * 0.5, 40)
        if desvio >= 15:
            motivos.append(f"latência {desvio:.1f}% acima da prevista")

    return round(pontos, 2), motivos


def registro_para_alerta(registro):
    """Converte uma linha da base em um objeto Alerta."""
    pontos, motivos = calcular_criticidade(registro)
    return Alerta(
        criticidade=pontos,
        timestamp_id=int(registro.get("timestamp_id", 0)),
        ciclo=int(registro.get("ciclo", 0)),
        modulo_id=str(registro.get("modulo_id", "")),
        nome_modulo=str(registro.get("nome_modulo", "")),
        codigo_sensor_hex=str(registro.get("codigo_sensor_hex", "")),
        status=str(registro.get("status_operacional", "")),
        prioridade=int(registro.get("prioridade", 1)),
        mensagem=str(registro.get("mensagem_alerta", "")),
        latencia_observada_ms=float(registro.get("latencia_observada_ms", 0) or 0),
        latencia_prevista_ms=float(registro.get("latencia_prevista_ms", 0) or 0),
        erro_relativo_pct=float(registro.get("erro_relativo_pct", 0) or 0),
        faixa_erro=str(registro.get("faixa_erro", "-")),
        potencia_w=float(registro.get("potencia_w", 0) or 0),
        limite_potencia_w=float(registro.get("limite_potencia_w", 0) or 0),
        motivos=motivos,
    )


class HeapAlertas:
    """
    Fila de prioridade (MAX-HEAP binário) implementada manualmente sobre uma lista.

    Representação: o nó na posição i tem filhos em 2i+1 e 2i+2 e pai em (i-1)//2.
    Invariante: a criticidade de um pai é SEMPRE >= à de seus filhos, logo o
    alerta mais crítico fica na raiz (posição 0).

    Empate de criticidade -> desempata pelo alerta mais ANTIGO (ordem de chegada),
    evitando que um alerta antigo fique "esquecido" (starvation).

    Complexidades:
        inserir ............ O(log n)  (sobe no máximo a altura da árvore)
        extrair_mais_critico O(log n)  (desce no máximo a altura da árvore)
        espiar ............. O(1)
        construir (heapify)  O(n)
    """

    def __init__(self):
        self._itens = []  # lista de tuplas (criticidade, -ordem, alerta)
        self._contador = 0  # ordem de chegada (desempate estável)
        self.comparacoes = 0  # contador didático de comparações

    # ------------------------- utilidades internas -------------------------
    def _maior(self, i, j):
        """True se o item i deve ficar ACIMA do item j no heap."""
        self.comparacoes += 1
        return self._itens[i][:2] > self._itens[j][:2]

    def _trocar(self, i, j):
        self._itens[i], self._itens[j] = self._itens[j], self._itens[i]

    def _subir(self, i):
        """Sift-up: sobe o item enquanto ele for maior que o pai."""
        while i > 0:
            pai = (i - 1) // 2
            if self._maior(i, pai):
                self._trocar(i, pai)
                i = pai
            else:
                break

    def _descer(self, i):
        """Sift-down: desce o item trocando com o maior filho."""
        n = len(self._itens)
        while True:
            esq, dir_ = 2 * i + 1, 2 * i + 2
            maior = i
            if esq < n and self._maior(esq, maior):
                maior = esq
            if dir_ < n and self._maior(dir_, maior):
                maior = dir_
            if maior == i:
                break
            self._trocar(i, maior)
            i = maior

    # ------------------------- operações públicas --------------------------
    def inserir(self, alerta):
        """Insere um Alerta (ou dict de registro) na fila. O(log n)."""
        if not isinstance(alerta, Alerta):
            alerta = registro_para_alerta(alerta)
        self._itens.append((alerta.criticidade, -self._contador, alerta))
        self._contador += 1
        self._subir(len(self._itens) - 1)

    def extrair_mais_critico(self):
        """Remove e retorna o alerta mais crítico. O(log n)."""
        if not self._itens:
            raise IndexError("A fila de alertas está vazia.")
        self._trocar(0, len(self._itens) - 1)
        _, _, alerta = self._itens.pop()
        if self._itens:
            self._descer(0)
        return alerta

    def espiar(self):
        """Consulta o alerta mais crítico sem removê-lo. O(1)."""
        if not self._itens:
            return None
        return self._itens[0][2]

    def top_n(self, n=5):
        """
        Retorna os n alertas mais críticos SEM alterar a fila.
        Usa uma cópia do heap e extrai n vezes -> O(n log N).
        """
        copia = HeapAlertas()
        copia._itens = list(self._itens)
        copia._contador = self._contador
        return [copia.extrair_mais_critico() for _ in range(min(n, len(copia)))]

    def carregar_de_dataframe(self, df, apenas_criticos=True):
        """
        Popula o heap a partir da base do SCIC.
        apenas_criticos=True -> entram registros com status 'alerta',
        sobrecarga de potência ou erro de previsão PREOCUPANTE.
        Retorna quantos alertas foram inseridos.
        """
        dados = df
        if apenas_criticos:
            filtro = dados["status_operacional"].astype(str).str.strip().str.lower() == "alerta"
            if {"potencia_w", "limite_potencia_w"} <= set(dados.columns):
                filtro |= dados["potencia_w"] > dados["limite_potencia_w"]
            if "faixa_erro" in dados.columns:
                filtro |= dados["faixa_erro"].astype(str).str.strip() == "PREOCUPANTE"
            dados = dados[filtro]

        for registro in dados.to_dict(orient="records"):
            self.inserir(registro)
        return len(dados)

    def esta_vazio(self):
        return len(self._itens) == 0

    def __len__(self):
        return len(self._itens)

    def __bool__(self):
        return bool(self._itens)

    def validar_invariante(self):
        """Confere se todo pai é >= aos filhos (útil para testes)."""
        n = len(self._itens)
        for i in range(n):
            for filho in (2 * i + 1, 2 * i + 2):
                if filho < n and self._itens[filho][:2] > self._itens[i][:2]:
                    return False
        return True


def comparar_heap_vs_lista(tamanhos=(500, 2_000, 5_000), semente=42):
    """
    Benchmark didático: insere n alertas e extrai TODOS em ordem de criticidade.
    - Lista comum: insere com append (O(1)) e extrai procurando o máximo (O(n)).
      Total ~ O(n²).
    - Heap: insere e extrai em O(log n). Total ~ O(n log n).
    Retorna uma lista de dicionários com os tempos em milissegundos.
    """
    rng = random.Random(semente)
    resultados = []
    for n in tamanhos:
        valores = [rng.uniform(0, 200) for _ in range(n)]

        # Lista comum
        inicio = time.perf_counter()
        lista = []
        for v in valores:
            lista.append(v)
        while lista:
            idx = max(range(len(lista)), key=lista.__getitem__)
            lista.pop(idx)
        t_lista = (time.perf_counter() - inicio) * 1000

        # Heap
        inicio = time.perf_counter()
        heap = HeapAlertas()
        for i, v in enumerate(valores):
            heap.inserir(
                Alerta(v, i, 0, "MOD", "bench", "0x00", "alerta", 1, "bench")
            )
        while heap:
            heap.extrair_mais_critico()
        t_heap = (time.perf_counter() - inicio) * 1000

        resultados.append(
            {
                "n": n,
                "lista_ms": round(t_lista, 2),
                "heap_ms": round(t_heap, 2),
                "ganho_x": round(t_lista / t_heap, 1) if t_heap else float("inf"),
            }
        )
    return resultados


# =====================================================================
# 2. TRIE DE MÓDULOS (BUSCA POR PREFIXO)
# =====================================================================


def normalizar(texto):
    """
    Deixa a chave em minúsculas e sem acentos, para que 'com', 'Com' e
    'comunicação' encontrem 'Comunicação Central'.
    """
    texto = unicodedata.normalize("NFKD", str(texto).strip().lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


class _NoTrie:
    __slots__ = ("filhos", "fim", "registros")

    def __init__(self):
        self.filhos = {}  # caractere -> _NoTrie
        self.fim = False  # marca o fim de uma chave completa
        self.registros = {}  # rótulo exibido -> dados associados


class TrieModulos:
    """
    Árvore de prefixos para módulos, tipos, códigos de sensor e comandos.

    Cada caractere da chave normalizada é uma aresta. Uma mesma entidade pode
    ser indexada por várias chaves (ex.: 'comunicacao central', 'central',
    'mod-02', '0x2a'), então digitar qualquer um desses prefixos a encontra.

    Complexidades (m = tamanho da chave/prefixo, k = nº de resultados):
        inserir ........ O(m)
        buscar_exato ... O(m)
        buscar_prefixo . O(m + tamanho da subárvore) ~ O(m + k)
    """

    def __init__(self):
        self.raiz = _NoTrie()
        self.total_chaves = 0

    def inserir(self, chave, rotulo, dados=None):
        """Insere 'chave' apontando para a entidade 'rotulo' (com seus dados)."""
        no = self.raiz
        for c in normalizar(chave):
            no = no.filhos.setdefault(c, _NoTrie())
        if not no.fim:
            self.total_chaves += 1
        no.fim = True
        no.registros[rotulo] = dados or {}

    def _no_do_prefixo(self, prefixo):
        no = self.raiz
        for c in normalizar(prefixo):
            no = no.filhos.get(c)
            if no is None:
                return None
        return no

    def buscar_exato(self, chave):
        """Retorna os registros associados à chave exata (ou {} se não existir)."""
        no = self._no_do_prefixo(chave)
        return dict(no.registros) if no and no.fim else {}

    def contem_prefixo(self, prefixo):
        return self._no_do_prefixo(prefixo) is not None

    def buscar_prefixo(self, prefixo, limite=None):
        """
        Retorna {rotulo: dados} de todas as entidades cuja alguma chave começa
        com 'prefixo'. Resultados sem repetição, em ordem alfabética.
        """
        no = self._no_do_prefixo(prefixo)
        if no is None:
            return {}
        encontrados = {}
        pilha = [no]  # DFS iterativa (evita recursão profunda)
        while pilha:
            atual = pilha.pop()
            if atual.fim:
                encontrados.update(atual.registros)
            pilha.extend(atual.filhos.values())
        rotulos = sorted(encontrados)
        if limite:
            rotulos = rotulos[:limite]
        return {r: encontrados[r] for r in rotulos}

    def autocompletar(self, prefixo, limite=10):
        """Retorna somente os rótulos encontrados (útil para sugestões no CLI)."""
        return list(self.buscar_prefixo(prefixo, limite).keys())

    def __len__(self):
        return self.total_chaves


def construir_trie(df, incluir_comandos=True):
    """
    Monta a Trie a partir da base do SCIC indexando, para cada módulo:
    nome completo, cada palavra do nome, modulo_id, tipo_modulo e códigos hex.
    """
    trie = TrieModulos()
    colunas = ["modulo_id", "nome_modulo", "tipo_modulo", "essencial", "limite_potencia_w"]
    modulos = df[colunas].drop_duplicates("modulo_id")
    sensores = df.groupby("modulo_id")["codigo_sensor_hex"].unique()

    for m in modulos.to_dict(orient="records"):
        codigos = sorted(sensores.get(m["modulo_id"], []))
        rotulo = f"{m['modulo_id']} - {m['nome_modulo']}"
        dados = {
            "categoria": "módulo",
            "modulo_id": m["modulo_id"],
            "nome_modulo": m["nome_modulo"],
            "tipo_modulo": m["tipo_modulo"],
            "essencial": bool(m["essencial"]),
            "sensores": list(codigos),
        }
        chaves = {m["nome_modulo"], m["modulo_id"], m["tipo_modulo"]}
        chaves.update(m["nome_modulo"].split())  # 'central' acha 'Comunicação Central'
        chaves.update(m["tipo_modulo"].split("_"))
        for chave in chaves:
            if len(chave) > 2:  # ignora 'de', 'da'...
                trie.inserir(chave, rotulo, dados)

        # Códigos de sensor: cada código é uma entidade própria
        for codigo in codigos:
            trie.inserir(
                codigo,
                f"{codigo} (sensor do {m['modulo_id']} - {m['nome_modulo']})",
                {**dados, "categoria": "sensor", "codigo": codigo, "decimal": int(codigo, 16),
                 "binario": bin(int(codigo, 16))[2:].zfill(8)},
            )

    if incluir_comandos:
        for comando, descricao in COMANDOS_SISTEMA.items():
            trie.inserir(comando, f"/{comando}", {"categoria": "comando", "descricao": descricao})
    return trie


# =====================================================================
# 3. CARREGAMENTO DA BASE E EXECUÇÃO DA FASE
# =====================================================================


def carregar_base_previsoes(caminho=None):
    """
    Lê o CSV enriquecido do Analista 2. Faz strip em cabeçalhos e textos,
    pois o arquivo pode ter sido 'alinhado' por algum editor (espaços extras).
    """
    origem = Path(caminho) if caminho else CSV_PREVISOES
    if not origem.exists():
        raise FileNotFoundError(f"Base com previsões não encontrada em: {origem}")
    df = pd.read_csv(origem, encoding="utf-8", skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].astype(str).str.strip()
    return df


def obter_base_completa():
    """
    Garante a base pronta para as estruturas: usa o CSV de previsões se existir;
    caso contrário, executa o pipeline dos Analistas 1 e 2.
    """
    try:
        return carregar_base_previsoes()
    except (FileNotFoundError, KeyError, ValueError):
        from .dados import gerar_dataset_telemetria, salvar_telemetria_csv
        from .modelagem import executar_fase6_analista2

        df = gerar_dataset_telemetria()
        salvar_telemetria_csv(df)
        return executar_fase6_analista2(df, exibir=False)["df_previsoes"]


def _secao(numero, titulo):
    print(f"\n[{numero}] {titulo}")
    print("-" * 80)


def imprimir_alerta_detalhado(alerta, posicao=None):
    prefixo = f"#{posicao} " if posicao is not None else ""
    print(f"{prefixo}{alerta.resumo()}")
    print(
        f"      latência obs/prev: {alerta.latencia_observada_ms:.2f}/"
        f"{alerta.latencia_prevista_ms:.2f} ms | erro {alerta.erro_relativo_pct:.2f}% "
        f"({alerta.faixa_erro}) | P = {alerta.potencia_w:.0f}/{alerta.limite_potencia_w:.0f} W"
    )
    print(f"      motivos: {', '.join(alerta.motivos) or '-'}")


def imprimir_busca(trie, prefixo):
    resultados = trie.buscar_prefixo(prefixo)
    print(f"\nPrefixo '{prefixo}' -> {len(resultados)} resultado(s)")
    for rotulo, dados in resultados.items():
        cat = dados.get("categoria", "")
        if cat == "comando":
            extra = dados["descricao"]
        elif cat == "sensor":
            extra = f"dec {dados['decimal']} | bin {dados['binario']}"
        else:
            extra = f"tipo {dados.get('tipo_modulo')} | sensores {', '.join(dados.get('sensores', []))}"
        print(f"  [{cat:<7}] {rotulo:<55} {extra}")
    return resultados


def executar_fase6_analista3(df_previsoes=None, exibir=True, top=5):
    """Monta o Heap e a Trie e (opcionalmente) imprime uma demonstração."""
    df = df_previsoes if df_previsoes is not None else obter_base_completa()

    heap = HeapAlertas()
    inseridos = heap.carregar_de_dataframe(df, apenas_criticos=True)
    mais_criticos = heap.top_n(top)
    trie = construir_trie(df)
    benchmark = comparar_heap_vs_lista()

    if exibir:
        print("\n" + "=" * 80)
        print("ESTRUTURAS DE DADOS: HEAP DE ALERTAS + TRIE (SCIC)".center(80))
        print("=" * 80)

        _secao(1, "HEAP DE ALERTAS CRÍTICOS (max-heap)")
        print(f"Registros na base: {len(df)} | alertas na fila: {inseridos}")
        print(f"Invariante do heap válida: {heap.validar_invariante()}")
        print(f"Top {top} alertas (ordem de atendimento):")
        for i, alerta in enumerate(mais_criticos, 1):
            imprimir_alerta_detalhado(alerta, i)

        _secao(2, "HEAP x LISTA COMUM (inserir n + extrair todos em ordem)")
        print(f"{'n':>8} | {'lista (ms)':>12} | {'heap (ms)':>10} | ganho")
        for r in benchmark:
            print(f"{r['n']:>8} | {r['lista_ms']:>12.2f} | {r['heap_ms']:>10.2f} | {r['ganho_x']}x")
        print("Lista: extração O(n) -> total O(n²). Heap: O(log n) -> total O(n log n).")

        _secao(3, "TRIE: BUSCA POR PREFIXO")
        print(f"Chaves indexadas: {len(trie)}")
        for prefixo in ("com", "0x2", "mod-0", "su", "di"):
            imprimir_busca(trie, prefixo)
        print("\n" + "=" * 80)

    return {
        "status": "sucesso",
        "heap": heap,
        "trie": trie,
        "alertas_na_fila": inseridos,
        "top_alertas": [
            {"modulo": a.nome_modulo, "ciclo": a.ciclo, "mensagem": a.mensagem,
             "criticidade": a.criticidade}
            for a in mais_criticos
        ],
        "benchmark": benchmark,
        "chaves_trie": len(trie),
    }


if __name__ == "__main__":
    executar_fase6_analista3()
