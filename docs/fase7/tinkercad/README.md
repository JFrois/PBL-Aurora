# Circuito lógico no Tinkercad - SIFSM

Regra: **ALERTA = A AND B AND C** e **BLOQUEIO = NOT C**, com
A = CONSUMO_ELEVADO, B = MODULO_CRITICO, C = SENSOR_VALIDO (veja `docs/fase7/circuito_logico.png`).

Há duas formas de montar; escolha uma (ou mostre as duas no vídeo).

## Opção 1 - Portas lógicas (circuito digital)
Componentes: 3 chaves deslizantes (A, B, C), 1 CI **74HC08** (4 portas AND), 1 CI **74HC04**
(6 inversores), 1 LED vermelho, 1 LED amarelo, 2 resistores de 220 ohms, bateria/fonte de 5 V.

1. Alimente os dois CIs (VCC = 5 V, GND = terra).
2. Chaves A e B -> entradas da 1ª porta AND do 74HC08 (pinos 1 e 2); saída (pino 3).
3. Saída da 1ª AND e chave C -> entradas da 2ª porta AND (pinos 4 e 5); saída (pino 6) -> resistor -> LED vermelho -> GND (**ALERTA**).
4. Chave C -> entrada de um inversor do 74HC04 (pino 1); saída (pino 2) -> resistor -> LED amarelo -> GND (**BLOQUEIO**).
5. Cada chave liga o 5 V à entrada (e um resistor de 10 k para GND como pull-down).

## Opção 2 - Arduino Uno
Monte conforme o cabeçalho de `sifsm_alerta.ino`: chaves em D2/D3/D4 (INPUT_PULLUP), LEDs em D8/D9
com resistor de 220 ohms. Cole o código no editor de código do Tinkercad e inicie a simulação.
O Monitor Serial mostra A, B, C, ALERTA e BLOQUEIO.

## Teste (deve bater com a tabela-verdade do sistema, opção 5 do menu)
| A | B | C | ALERTA | BLOQUEIO |
|---|---|---|--------|----------|
| 1 | 1 | 1 | 1 | 0 |
| 1 | 1 | 0 | 0 | 1 |
| 1 | 0 | 1 | 0 | 0 |
| 0 | 1 | 1 | 0 | 0 |

## Entrega
Quando o circuito estiver pronto no Tinkercad, copie o link de compartilhamento para o arquivo
`docs/fase7/link_tinkercad.txt` (e/ou use o `circuito_logico.png`). O menu (opção 6) mostra ambos.
