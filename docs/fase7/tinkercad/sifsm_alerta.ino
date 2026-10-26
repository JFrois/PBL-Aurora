// SIFSM - Regra de decisão da colônia no Arduino (Tinkercad Circuits)
// ALERTA   = CONSUMO_ELEVADO AND MODULO_CRITICO AND SENSOR_VALIDO
// BLOQUEIO = NOT SENSOR_VALIDO
//
// Entradas (chaves deslizantes, com INPUT_PULLUP: chave fechada ao GND = 1 lógico):
//   D2 = A (CONSUMO_ELEVADO)   D3 = B (MODULO_CRITICO)   D4 = C (SENSOR_VALIDO)
// Saídas:
//   D8 = LED vermelho (ALERTA)   D9 = LED amarelo (BLOQUEIO)   (cada LED com resistor de 220 ohms)

const int PINO_A = 2, PINO_B = 3, PINO_C = 4;
const int LED_ALERTA = 8, LED_BLOQUEIO = 9;

void setup() {
  pinMode(PINO_A, INPUT_PULLUP);
  pinMode(PINO_B, INPUT_PULLUP);
  pinMode(PINO_C, INPUT_PULLUP);
  pinMode(LED_ALERTA, OUTPUT);
  pinMode(LED_BLOQUEIO, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  bool a = (digitalRead(PINO_A) == LOW);  // LOW = chave ligada = 1 lógico
  bool b = (digitalRead(PINO_B) == LOW);
  bool c = (digitalRead(PINO_C) == LOW);

  bool alerta = a && b && c;   // mesma regra de logica.acionar_alerta()
  bool bloqueio = !c;          // mesma regra de logica.bloquear_operacao()

  digitalWrite(LED_ALERTA, alerta ? HIGH : LOW);
  digitalWrite(LED_BLOQUEIO, bloqueio ? HIGH : LOW);

  Serial.print("A="); Serial.print(a);
  Serial.print(" B="); Serial.print(b);
  Serial.print(" C="); Serial.print(c);
  Serial.print(" -> ALERTA="); Serial.print(alerta);
  Serial.print(" BLOQUEIO="); Serial.println(bloqueio);
  delay(300);
}
