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

    try:
        valor_dec = int(limpo, 16)
    except ValueError:
        raise ValueError(
            f"O valor introduzido ('{hex_str}') não é um hexadecimal válido."
        )

    return {
        "hex": f"0x{limpo.upper().zfill(2)}",
        "decimal": valor_dec,
        "binario": bin(valor_dec)[2:].zfill(8),
    }


def mapear_interfaces_io(modulo_id: str = None) -> Dict[str, Dict[str, str]]:
    """
    Mapeamento conceitual de I/O e interfaces de transmissão da colônia Aurora Siger.
    Mapeia os módulos e sensores para protocolos físicos (CAN Bus, SpaceWire, 4-20mA, RS-485).
    """
    interfaces = {
        "MOD-01": {
            "modulo": "Habitação Alfa",
            "interface_comunicacao": "SpaceWire / Ethernet Óptica",
            "sensores_io": "GPIO Digital (0x1A) + ADC Analógico Temp (0x1B)",
            "barramento_eletrico": "230V AC - Barramento Principal A",
        },
        "MOD-02": {
            "modulo": "Comunicação Central",
            "interface_comunicacao": "SpaceWire / RF Link Orbital",
            "sensores_io": "UART Registrador Hex (0x2A) + Transceptor RF (0x2B)",
            "barramento_eletrico": "230V AC - Barramento Crítico Backup",
        },
        "MOD-03": {
            "modulo": "Controle de Missão",
            "interface_comunicacao": "CAN Bus Redundante (ISO 11898)",
            "sensores_io": "Telemetria SPI (0x3A) + I2C Registrador (0x3B)",
            "barramento_eletrico": "230V AC - Barramento Primário",
        },
        "MOD-04": {
            "modulo": "Laboratório Científico",
            "interface_comunicacao": "Ethernet Industrial / RS-485",
            "sensores_io": "4-20mA Espectrômetro (0x4A) + Sensor Rad (0x4B)",
            "barramento_eletrico": "230V AC - Barramento Auxiliar",
        },
        "MOD-05": {
            "modulo": "Suporte Médico",
            "interface_comunicacao": "SpaceWire Redundante Classe Hospitalar",
            "sensores_io": "ADC Médico Iso (0x5A) + Pressão Digital (0x5B)",
            "barramento_eletrico": "230V AC - Barramento Crítico Suporte Vida",
        },
        "MOD-06": {
            "modulo": "Estufa Agrícola",
            "interface_comunicacao": "RS-485 Modbus RTU",
            "sensores_io": "ADC Clima (0x6A) + Sensor Iluminação (0x6B)",
            "barramento_eletrico": "230V AC - Barramento Agrícola High-Power",
        },
        "MOD-07": {
            "modulo": "Armazenamento de Dados",
            "interface_comunicacao": "PCIe Fabric / SpaceWire High-Speed",
            "sensores_io": "NVMe Bus (0x7A) + Telemetria Storage (0x7B)",
            "barramento_eletrico": "230V AC - Barramento Computacional",
        },
        "MOD-08": {
            "modulo": "Produção de Oxigênio",
            "interface_comunicacao": "CAN Bus Industrial Redundante",
            "sensores_io": "4-20mA Sensor O2 (0x8A) + Válvula Solenoide (0x8B)",
            "barramento_eletrico": "230V AC - Barramento Suporte Vida Crítico",
        },
    }

    if modulo_id:
        mod_upper = modulo_id.strip().upper()
        if mod_upper in interfaces:
            return {mod_upper: interfaces[mod_upper]}
        raise ValueError(f"Módulo '{modulo_id}' não encontrado no mapeamento de I/O.")
    return interfaces

