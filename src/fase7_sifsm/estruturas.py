"""Estruturas de dados aplicadas à colônia  |  INTEGRANTE 1  |  Cap. 4 (sistemas complexos)

Escolhas (justificativa):
  * Fila (FIFO)       -> chamados da tripulação: quem chama primeiro é atendido primeiro (justo).
  * Pilha (LIFO)      -> histórico de ações do CRUD: a última ação é a primeira a ser desfeita.
  * Tabela hash       -> busca de sensor por código hexadecimal em O(1) médio (implementada com
                         encadeamento para tratar colisões, como no Cap. 4).
  * Heap de alertas   -> REAPROVEITADO da Fase 6 (HeapAlertas): prioriza o alerta mais crítico
                         em O(log n). Também disponíveis: TrieModulos (Fase 6) e grafo (Fase 4).
"""

from __future__ import annotations

from collections import deque
from typing import Any, Optional

from src.fase7_sifsm import banco, logica


class FilaChamados:
    """Fila FIFO de chamados da tripulação (enfileirar e atender em O(1))."""

    def __init__(self) -> None:
        self._itens: deque = deque()

    def enfileirar(self, chamado: dict) -> None:
        if not isinstance(chamado, dict) or not chamado.get("descricao"):
            raise ValueError("Chamado inválido: informe um dicionário com 'descricao'.")
        self._itens.append(chamado)

    def atender(self) -> Optional[dict]:
        """Remove e devolve o chamado mais antigo (None se vazia)."""
        return self._itens.popleft() if self._itens else None

    def espiar(self) -> Optional[dict]:
        return self._itens[0] if self._itens else None

    def listar(self) -> list[dict]:
        return list(self._itens)

    def __len__(self) -> int:
        return len(self._itens)


class PilhaHistorico:
    """Pilha LIFO com o histórico de ações (cadastrar/alterar/excluir) para desfazer."""

    def __init__(self, limite: int = 50) -> None:
        self._itens: list[dict] = []
        self._limite = limite

    def empilhar(self, acao: dict) -> None:
        self._itens.append(acao)
        if len(self._itens) > self._limite:  # descarta a mais antiga para não crescer sem fim
            self._itens.pop(0)

    def desempilhar(self) -> Optional[dict]:
        """Remove e devolve a ação mais recente (None se vazia)."""
        return self._itens.pop() if self._itens else None

    def topo(self) -> Optional[dict]:
        return self._itens[-1] if self._itens else None

    def listar(self) -> list[dict]:
        """Do topo (mais recente) para a base."""
        return list(reversed(self._itens))

    def __len__(self) -> int:
        return len(self._itens)


class TabelaSensores:
    """Tabela hash com encadeamento: código hexadecimal do sensor -> dados do sensor/módulo."""

    def __init__(self, capacidade: int = 8, fator_carga_max: float = 0.75) -> None:
        self._baldes: list[list[list]] = [[] for _ in range(capacidade)]
        self._tamanho = 0
        self._fator_max = fator_carga_max
        self.colisoes = 0

    @staticmethod
    def _normalizar(codigo_hex: str) -> str:
        return str(codigo_hex).strip().upper()

    @staticmethod
    def _hash(chave: str, capacidade: int) -> int:
        valor = 0
        for caractere in chave:  # hash polinomial simples (base 31)
            valor = (valor * 31 + ord(caractere)) % (2 ** 32)
        return valor % capacidade

    def inserir(self, codigo_hex: str, dados: Any) -> None:
        chave = self._normalizar(codigo_hex)
        balde = self._baldes[self._hash(chave, len(self._baldes))]
        for par in balde:
            if par[0] == chave:  # atualiza se já existe
                par[1] = dados
                return
        if balde:
            self.colisoes += 1
        balde.append([chave, dados])
        self._tamanho += 1
        if self._tamanho / len(self._baldes) > self._fator_max:
            self._redimensionar()

    def buscar(self, codigo_hex: str) -> Optional[Any]:
        chave = self._normalizar(codigo_hex)
        for par in self._baldes[self._hash(chave, len(self._baldes))]:
            if par[0] == chave:
                return par[1]
        return None

    def remover(self, codigo_hex: str) -> bool:
        chave = self._normalizar(codigo_hex)
        balde = self._baldes[self._hash(chave, len(self._baldes))]
        for i, par in enumerate(balde):
            if par[0] == chave:
                del balde[i]
                self._tamanho -= 1
                return True
        return False

    def _redimensionar(self) -> None:
        antigos = [par for balde in self._baldes for par in balde]
        self._baldes = [[] for _ in range(len(self._baldes) * 2)]
        self._tamanho = 0
        self.colisoes = 0
        for chave, dados in antigos:
            self.inserir(chave, dados)

    def estatisticas(self) -> dict:
        return {
            "capacidade": len(self._baldes),
            "tamanho": self._tamanho,
            "fator_de_carga": round(self._tamanho / len(self._baldes), 2),
            "colisoes": self.colisoes,
        }

    def __len__(self) -> int:
        return self._tamanho

    def __contains__(self, codigo_hex: str) -> bool:
        return self.buscar(codigo_hex) is not None


def montar_heap_de_alertas(leituras: list[dict]):
    """Monta o HeapAlertas da Fase 6 com as leituras de risco 'alto' ou 'medio'.

    Mapeia os campos da Fase 7 (consumo_w, limite_consumo_w...) para o formato que o heap
    da Fase 6 entende (potencia_w, limite_potencia_w...). Importa a Fase 6 só aqui, pois ela
    depende de pandas.
    """
    from src.fases_anteriores.fase6_scic.estruturas import HeapAlertas

    heap = HeapAlertas()
    for leitura in leituras:
        limite = float(leitura["limite_consumo_w"])
        risco = logica.classificar_risco(leitura, limite, bool(leitura["essencial"]))
        if risco not in ("alto", "medio", "bloqueado"):
            continue
        percentual = 100.0 * float(leitura["consumo_w"]) / limite
        heap.inserir({
            "timestamp_id": leitura["id"], "ciclo": 0,
            "modulo_id": leitura["modulo_id"], "nome_modulo": leitura["nome_modulo"],
            "codigo_sensor_hex": leitura.get("codigo_sensor") or "-",
            "status_operacional": leitura["status_operacional"],
            "essencial": leitura["essencial"],
            "prioridade": {"alto": 5, "medio": 3, "bloqueado": 4}[risco],
            "potencia_w": leitura["consumo_w"], "limite_potencia_w": limite,
            "mensagem_alerta": f"Risco {risco}: consumo em {percentual:.0f}% do limite",
        })
    return heap


def _titulo(texto: str) -> None:
    print(f"\n--- {texto} " + "-" * max(3, 62 - len(texto)))


def demonstrar_estruturas(historico: Optional[PilhaHistorico] = None) -> None:
    """Demonstração para o menu/vídeo: usa dados REAIS do banco em cada estrutura."""
    _titulo("1. FILA (FIFO) - chamados da tripulação")
    fila = FilaChamados()
    for chamado in banco.listar_chamados():
        fila.enfileirar(chamado)
    print(f"  {len(fila)} chamado(s) na fila. Atendendo na ordem de chegada:")
    for _ in range(min(2, len(fila))):
        c = fila.atender()
        print(f"   -> atendido #{c['id']} [{c['modulo_id']}] {c['descricao']}")
    proximo = fila.espiar()
    print(f"  Próximo da fila: {proximo['descricao'] if proximo else '(vazia)'}")

    _titulo("2. PILHA (LIFO) - histórico de ações do CRUD (desfazer)")
    if historico is None or len(historico) == 0:
        print("  Nenhuma ação nesta sessão ainda. Cadastre, altere ou exclua uma leitura e volte aqui.")
    else:
        print(f"  {len(historico)} ação(ões); a próxima a ser desfeita é a do topo:")
        for posicao, acao in enumerate(historico.listar()[:5]):
            marca = "TOPO" if posicao == 0 else "    "
            print(f"   {marca} {acao['acao']} (leitura #{acao['id']})")

    _titulo("3. TABELA HASH - busca de sensor por código")
    tabela = TabelaSensores()
    for sensor in banco.listar_sensores():
        tabela.inserir(sensor["codigo_hex"], sensor)
    print(f"  Estatísticas: {tabela.estatisticas()}")
    for codigo in ("0x1A", "0x6B", "0xFF"):
        achado = tabela.buscar(codigo)
        print(f"   buscar({codigo}) -> "
              + (f"módulo {achado['modulo_id']} ({achado['tipo']})" if achado else "não encontrado"))

    _titulo("4. HEAP (Fase 6) - alertas mais críticos primeiro")
    try:
        heap = montar_heap_de_alertas(banco.listar_leituras(limite=None))
    except ImportError as erro:
        print(f"  [Aviso] Heap indisponível (dependência ausente: {erro}).")
        return
    print(f"  {len(heap)} alerta(s) na fila de prioridade. Top 3:")
    for alerta in heap.top_n(3):
        print("   " + alerta.resumo())
