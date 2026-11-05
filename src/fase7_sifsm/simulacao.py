"""5.4 Simulação computacional e integração matemática  |  INTEGRANTE 2  |"""


from datetime import datetime
from math import isfinite
from pathlib import Path

import matplotlib.pyplot as plt


PASTA_GRAFICOS = (
    Path(__file__).resolve().parents[2]
    / "docs/fase7/graficos_ou_imagens"
)


def integrar_trapezio(tempos_h, potencias_w) -> float:
    """Calcula energia em Wh: área sob a curva de potência em W."""
    if len(tempos_h) != len(potencias_w) or len(tempos_h) < 2:
        raise ValueError("Informe pelo menos dois pares de tempo e potência.")

    tempos = [float(valor) for valor in tempos_h]
    potencias = [float(valor) for valor in potencias_w]

    for valor in tempos + potencias:
        if not isfinite(valor):
            raise ValueError("Os valores devem ser finitos.")

    if any(potencia < 0 for potencia in potencias):
        raise ValueError("A potência não pode ser negativa.")

    energia_wh = 0.0

    for i in range(1, len(tempos)):
        intervalo_h = tempos[i] - tempos[i - 1]

        if intervalo_h <= 0:
            raise ValueError("Os tempos devem estar em ordem crescente.")

        potencia_media = (potencias[i - 1] + potencias[i]) / 2
        energia_wh += potencia_media * intervalo_h

    return energia_wh


def simular_consumo(leituras: list[dict], horas: int = 24) -> dict:
    """Organiza as leituras por instante e soma o consumo dos módulos."""
    if not leituras or not isfinite(horas) or horas <= 0:
        raise ValueError("Informe leituras e uma duração positiva.")

    registros_por_data = {}
    modulos = set()

    for leitura in leituras:
        data = datetime.fromisoformat(str(leitura["data_registro"]))
        modulo = leitura["modulo_id"]
        consumo = float(leitura["consumo_w"])

        if not isfinite(consumo) or consumo < 0:
            raise ValueError("Há uma leitura com consumo inválido.")

        if data not in registros_por_data:
            registros_por_data[data] = {}

        if modulo in registros_por_data[data]:
            raise ValueError("Há leituras duplicadas por módulo e data.")

        registros_por_data[data][modulo] = consumo
        modulos.add(modulo)

     # Comparar instantes com o mesmo conjunto de módulos.
    datas_completas = []
    for data in sorted(registros_por_data):
        if set(registros_por_data[data]) == modulos:
            datas_completas.append(data)

    if len(datas_completas) < 2:
        raise ValueError("São necessários dois instantes completos.")

    inicio = datas_completas[0]
    tempos = [0.0]
    potencias = [sum(registros_por_data[inicio].values())]

    for data in datas_completas[1:]:
        tempo_h = (data - inicio).total_seconds() / 3600
        potencia = sum(registros_por_data[data].values())

        if tempo_h > horas:
            # Interpola o ponto final quando ele fica entre duas leituras.
            fracao = (horas - tempos[-1]) / (tempo_h - tempos[-1])
            potencia = potencias[-1] + fracao * (potencia - potencias[-1])
            tempos.append(float(horas))
            potencias.append(potencia)
            break

        tempos.append(tempo_h)
        potencias.append(potencia)

        if tempo_h == horas:
            break

    energia_wh = integrar_trapezio(tempos, potencias)
    duracao_h = tempos[-1]

    return {
        "tempos_h": tempos,
        "potencias_w": potencias,
        "energia_wh": energia_wh,
        "potencia_media_w": energia_wh / duracao_h,
        "duracao_h": duracao_h,
        "instantes_descartados": len(registros_por_data) - len(datas_completas),
    }    


def simular_bateria(
    capacidade_wh: float,
    geracao_w: float,
    consumo_w: float,
    horas: int = 48,
    passo_h: float = 0.5,
    soc_inicial: float = 0.8,
) -> dict:
    """Atualiza a energia da bateria em pequenos intervalos de tempo."""
    valores = [capacidade_wh, geracao_w, consumo_w, horas, passo_h, soc_inicial]

    if not all(isfinite(valor) for valor in valores):
        raise ValueError("Os parâmetros devem ser finitos.")
    if capacidade_wh <= 0 or horas <= 0 or passo_h <= 0:
        raise ValueError("Capacidade, duração e passo devem ser positivos.")
    if geracao_w < 0 or consumo_w < 0 or not 0 <= soc_inicial <= 1:
        raise ValueError("Geração, consumo ou carga inicial inválidos.")
    if horas / passo_h > 100000:
        raise ValueError("Use um passo maior para reduzir o número de cálculos.")

    tempo = 0.0
    energia_wh = capacidade_wh * soc_inicial
    deficit_wh = 0.0
    tempos = [tempo]
    cargas = [soc_inicial]
    deficits = [0.0]

    while tempo < horas:
        intervalo_h = min(passo_h, horas - tempo)
        energia_wh += (geracao_w - consumo_w) * intervalo_h

        if energia_wh < 0:
            deficit_wh += -energia_wh
            energia_wh = 0.0
        elif energia_wh > capacidade_wh:
            energia_wh = capacidade_wh

        tempo = min(tempo + intervalo_h, float(horas))
        tempos.append(tempo)
        cargas.append(energia_wh / capacidade_wh)
        deficits.append(deficit_wh)

    return {"tempos_h": tempos, "soc": cargas, "deficit_wh": deficits}    


def comparar_cenarios(leituras: list[dict]) -> dict:
    atual = simular_consumo(leituras)
    leituras_reduzidas = []

    for leitura in leituras:
        copia = leitura.copy()
        if not bool(leitura["essencial"]):
            copia["consumo_w"] = float(leitura["consumo_w"]) * 0.85
        leituras_reduzidas.append(copia)

    eficiente = simular_consumo(leituras_reduzidas)

    return {
        "atual": atual,
        "eficiente": eficiente,
        "economia_wh": atual["energia_wh"] - eficiente["energia_wh"],
    }


def gerar_graficos(resultado: dict, pasta_saida=None) -> list[str]:
    pasta = Path(pasta_saida) if pasta_saida else PASTA_GRAFICOS
    pasta.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 4))
    for nome in ("atual", "eficiente"):
        cenario = resultado[nome]
        plt.plot(cenario["tempos_h"], cenario["potencias_w"], label=nome)
    plt.xlabel("Tempo (h)")
    plt.ylabel("Potência total (W)")
    plt.title("Comparação dos cenários de consumo")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    consumo = pasta / "consumo_cenarios.png"
    plt.savefig(consumo)
    plt.close()

    bateria = resultado["bateria"]
    cargas_percentuais = [carga * 100 for carga in bateria["soc"]]
    plt.figure(figsize=(9, 4))
    plt.plot(bateria["tempos_h"], cargas_percentuais)
    plt.xlabel("Tempo (h)")
    plt.ylabel("Carga da bateria (%)")
    plt.title("Bateria ideal: geração e consumo constantes")
    plt.ylim(0, 105)
    plt.grid(True)
    plt.tight_layout()
    arquivo_bateria = pasta / "bateria.png"
    plt.savefig(arquivo_bateria)
    plt.close()

    return [str(consumo), str(arquivo_bateria)]


def executar_simulacao() -> dict:
    from . import banco

    leituras = banco.listar_leituras(limite=None, ordem="asc")
    resultado = comparar_cenarios(leituras)
    media_w = resultado["atual"]["potencia_media_w"]

    resultado["bateria"] = simular_bateria(
        capacidade_wh=100000,
        geracao_w=media_w * 0.8,
        consumo_w=media_w,
    )
    resultado["graficos"] = gerar_graficos(resultado)

    print(f"Duração analisada: {resultado['atual']['duracao_h']:.1f} h")
    print(f"Energia acumulada: {resultado['atual']['energia_wh']:.1f} Wh")
    print(f"Potência média: {media_w:.1f} W")
    print(f"Economia hipotética: {resultado['economia_wh']:.1f} Wh")
    print(f"Instantes incompletos descartados: {resultado['atual']['instantes_descartados']}")
    print("Bateria ilustrativa: 100 kWh, carga inicial 80%, geração de 80% da demanda média.")
    print(f"Energia não atendida em 48 h: {resultado['bateria']['deficit_wh'][-1]:.1f} Wh")
    print("Limitações: dados sintéticos, bateria ideal, sem perdas ou variação na geração.")
    print("A bateria utiliza demanda média constante; não reproduz a série instantânea.")
    print("Leituras em falha são valores hipotéticos, sem validade para decisões operacionais.")
    for caminho in resultado["graficos"]:
        print("Gráfico salvo:", caminho)

    return resultado
