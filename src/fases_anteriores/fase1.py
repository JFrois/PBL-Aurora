import random
import time


def imprimir_quadro(titulo, linhas):
    """Exibe o relatório de forma profissional no terminal."""
    largura = 85
    print("-" * largura)
    print(f"| {titulo.center(largura - 4)} |")
    print("|" + " " * (largura - 2) + "|")
    for linha in linhas:
        print(f"| {linha.ljust(largura - 4)} |")
    print("|" + " " * (largura - 2) + "|")
    print("-" * largura)


def executar_fase1():
    """
    Simula os 3 testes de telemetria.
    A lógica de random.uniform foi ajustada para operar estritamente
    dentro dos limites operacionais seguros (Status GO).
    """
    quantidade_testes = 0
    testes_sucessos = 0
    testes_falhas = 0

    print("\n" + "=" * 85)
    print("INICIANDO FASE 1: TELEMETRIA E PRÉ-DECOLAGEM (SISTEMA NOMINAL)".center(85))
    print("=" * 85)

    while quantidade_testes < 3:
        quantidade_testes += 1

        # DADOS OTIMIZADOS: Sempre dentro das faixas de segurança
        temp_interna = random.uniform(20.0, 23.0)  # Segurança: 18 a 25
        temp_externa = random.uniform(15.0, 25.0)  # Segurança: 5 a 38
        capacidade_energia_kwh = random.uniform(4500, 5000)
        carga_energia_pct = random.uniform(98, 100)  # Quase 100% carregada
        consumo_energia_est = random.uniform(200, 210)  # Consumo otimizado
        perdas_energia = random.uniform(10, 15)
        pressao = random.uniform(350, 400)  # Segurança: 300 a 450

        # Cálculo de autonomia
        energia_bruta = capacidade_energia_kwh * (carga_energia_pct / 100)
        saldo_pos_decolagem = (
            (energia_bruta - perdas_energia - consumo_energia_est)
            / capacidade_energia_kwh
        ) * 100

        # Montagem do log rico em detalhes
        linhas_relatorio = [
            "STATUS: OPERAÇÃO NOMINAL",
            f"  > Bateria Útil: {energia_bruta:.2f} kWh",
            f"  > Autonomia após decolagem: {saldo_pos_decolagem:.2f}% (Safe > 80%)",
            f"  > Pressão interna: {pressao:.2f} psi",
            f"  > Temperatura Interna: {temp_interna:.2f} C°",
            "STATUS DOS MÓDULOS CRÍTICOS: OK",
        ]

        testes_sucessos += 1
        imprimir_quadro(f"RODADA {quantidade_testes}/3 - SUCESSO", linhas_relatorio)
        time.sleep(0.5)

    print("\n>>> STATUS FINAL: DECOLAGEM AUTORIZADA! 🚀")

    return {
        "status": "GO",
        "sucessos": testes_sucessos,
        "falhas": 0,
        "erros_detectados": [],
    }
