import random
import time


def imprimir_quadro(titulo, linhas):
    """
    Função auxiliar para desenhar um quadro formatado no terminal.
    Garante que a interface de texto seja limpa e profissional.
    """
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
    Simula os 3 testes de telemetria exigidos para autorizar a descolagem.
    Retorna um dicionário com os dados em bruto para que o main.py possa
    enviá-los para a Inteligência Artificial analisar posteriormente.
    """
    quantidade_testes = 0
    testes_sucessos = 0
    testes_falhas = 0
    todos_erros = []  # Acumula todos os erros encontrados para o relatório final

    print("\n" + "=" * 85)
    print("INICIANDO FASE 1: TELEMETRIA E PRÉ-DESCOLAGEM".center(85))
    print("=" * 85)

    while quantidade_testes < 3:
        erros = []  # Reinicia a lista de erros a cada rodada de teste
        quantidade_testes += 1

        # Geração de dados de telemetria simulados dentro e fora dos limites
        temp_interna = random.uniform(18.5, 24.5)
        temp_externa = random.uniform(6.0, 37.0)
        capacidade_energia_kwh = random.uniform(4000, 5000)
        carga_energia_pct = random.uniform(95, 100)
        consumo_energia_est = random.uniform(200, 250)
        perdas_energia = random.uniform(10, 20)
        pressao = random.uniform(310, 440)

        # Cálculo de viabilidade energética
        energia_bruta_kwh = capacidade_energia_kwh * (carga_energia_pct / 100)
        energia_restante_kwh = energia_bruta_kwh - perdas_energia - consumo_energia_est
        saldo_pos_decolagem_pct = max(
            0, (energia_restante_kwh / capacidade_energia_kwh) * 100
        )

        # Verificação de restrições de segurança (Lógica Condicional)
        if pressao < 300 or pressao > 450:
            erros.append(f"Pressão anómala: {pressao:.2f} psi")
        if temp_interna < 18 or temp_interna > 25:
            erros.append(f"Temp interna anómala: {temp_interna:.2f} C°")
        if temp_externa < 5 or temp_externa > 38:
            erros.append(f"Temp externa anômala: {temp_externa:.2f} C°")

        # Registo do resultado do teste atual
        if not erros:
            testes_sucessos += 1
            imprimir_quadro(
                f"RODADA {quantidade_testes}/3 - SUCESSO", ["Parâmetros normais."]
            )
        else:
            testes_falhas += 1
            todos_erros.extend(erros)
            imprimir_quadro(f"RODADA {quantidade_testes}/3 - FALHA", erros)

        time.sleep(1)  # Pausa para simular o processamento em tempo real

    # Define o veredicto da fase
    status_lancamento = "GO" if testes_falhas == 0 else "NO-GO"

    # Retorna o dicionário para ser agregado no Data Lake do main.py
    return {
        "status": status_lancamento,
        "sucessos": testes_sucessos,
        "falhas": testes_falhas,
        "erros_detectados": list(set(todos_erros)),  # O set() remove duplicados
    }
