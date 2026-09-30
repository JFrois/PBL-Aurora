"""
Módulo de Hardware e Arquitetura Computacional — Analista 1
Fase 6: SCIC (Missão Aurora Siger)

Responsabilidades:
- Dimensionamento de circuitos elétricos via Lei de Ohm (V = R * I) e Potência (P = V * I).
- Validação de integridade de barramento de energia.
- Conversão e codificação de bases numéricas para emulação de registradores (Hex, Bin, Dec).
"""

from typing import Dict, Union


def calcular_potencia(tensao_v: float, corrente_a: float) -> float:
    """Calcula a potência dissipada/consumida em Watts (P = V * I)."""
    if tensao_v < 0 or corrente_a < 0:
        raise ValueError("Tensão e corrente devem ser valores não-negativos.")
    return round(tensao_v * corrente_a, 4)


def calcular_resistencia(tensao_v: float, corrente_a: float) -> float:
    """Calcula a resistência equivalente em Ohms via Lei de Ohm (R = V / I)."""
    if corrente_a <= 0:
        raise ZeroDivisionError(
            "Corrente deve ser estritamente positiva para cálculo de resistência."
        )
    if tensao_v < 0:
        raise ValueError("Tensão deve ser um valor não-negativo.")
    return round(tensao_v / corrente_a, 4)


def diagnosticar_circuito(
    tensao_v: float, corrente_a: float, limite_potencia_w: float
) -> Dict[str, Union[float, str, bool]]:
    """
    Avalia a integridade de um barramento elétrico da colónia.
    Verifica se a potência ultrapassa o limite térmico do componente.
    """
    potencia = calcular_potencia(tensao_v, corrente_a)
    resistencia = calcular_resistencia(tensao_v, corrente_a)
    sobrecarga = potencia > limite_potencia_w

    return {
        "tensao_v": tensao_v,
        "corrente_a": corrente_a,
        "resistencia_ohm": resistencia,
        "potencia_w": potencia,
        "limite_potencia_w": limite_potencia_w,
        "sobrecarga": sobrecarga,
        "status": "CRÍTICO: Sobrecarga Térmica" if sobrecarga else "NOMINAL",
    }


def decimal_para_binario(valor: int, bits: int = 8) -> str:
    """Converte um inteiro decimal para representação binária com largura fixa."""
    if not (0 <= valor < (1 << bits)):
        raise ValueError(
            f"Valor {valor} fora da faixa para representação de {bits} bits."
        )
    return bin(valor)[2:].zfill(bits)


def decimal_para_hexadecimal(valor: int, digitos: int = 2) -> str:
    """Converte um inteiro decimal para representação hexadecimal prefixada."""
    if valor < 0:
        raise ValueError("Apenas inteiros não-negativos são suportados.")
    return "0x" + hex(valor)[2:].upper().zfill(digitos)


def decodificar_registrador_telemetria(hex_str: str) -> Dict[str, Union[int, str]]:
    """
    Decodifica uma palavra de registrador hexadecimal (ex: '0x1F', 'A4')
    retornando o seu estado em decimal e binário de 8 bits.
    """
    limpo = hex_str.strip().lower()
    if limpo.startswith("0x"):
        limpo = limpo[2:]

    valor_dec = int(limpo, 16)
    return {
        "hex": f"0x{limpo.upper().zfill(2)}",
        "decimal": valor_dec,
        "binario": bin(valor_dec)[2:].zfill(8),
    }
