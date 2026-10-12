# 🌪️ Fase 3: Sistema Inteligente da Colônia & Matriz Energética (SIC)

<span class="mission-patch">PHASE 3</span>
<span class="mission-patch cyan">SIC ENERGY</span>
<span class="mission-patch green">LINEAR REGRESSION & R²</span>

A **Fase 3** gerencia a sustentabilidade energética da colônia Aurora Siger após o pouso dos módulos, modelando a geração de energia a partir das turbinas eólicas marcianas e administrando o consumo dinâmico com corte inteligente de cargas secundárias.

---

## 1. Modelagem Numérica: Regressão Linear Simples

A geração eólica em Marte depende da velocidade dos ventos na cratera de pouso. O sistema armazena uma série temporal histórica de pares $(x_i, y_i)$ relacionando velocidade do vento em $\text{m/s}$ e potência gerada em $\text{kW}$.

### Fórmulas de Mínimos Quadrados:
$$m = \frac{n \sum(x \cdot y) - \sum x \sum y}{n \sum(x^2) - (\sum x)^2}$$
$$b = \frac{\sum y - m \sum x}{n}$$
$$\hat{y} = m \cdot x_{\text{atual}} + b$$

### Coeficiente de Determinação ($R^2$):
O sistema avalia a qualidade do ajuste do modelo estatístico calculando a razão entre a soma dos quadrados dos resíduos ($SS_{\text{res}}$) e a soma total dos quadrados ($SS_{\text{tot}}$):
$$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$

Um valor de $R^2 \ge 0.95$ classifica o ajuste como excelente, conferindo alta confiabilidade à previsão energética.

---

## 2. Catálogo de Consumo e Gestão de Carga

Cada módulo em solo marciano possui um perfil de consumo elétrico contínuo:

| Módulo | Tipo de Uso | Consumo Nominal | Prioridade de Sobrevivência |
|---|---|---|---|
| **Suporte Médico** | Crítico / Suporte à Vida | $30.0\text{ kW}$ | **Essencial (Inviolável)** |
| **Habitação Alfa** | Residencial / Suporte à Vida | $45.0\text{ kW}$ | **Essencial (Inviolável)** |
| **Centro de Controle** | Comando & Telecomunicações | $60.0\text{ kW}$ | **Essencial (Inviolável)** |
| **Laboratório Científico** | Pesquisa Geológica | $55.0\text{ kW}$ | **Não Essencial (Desligável)** |

---

## 3. Algoritmo de Corte Seletivo de Carga (Load Shedding)

Quando a geração eólica prevista somada à reserva das baterias não é suficiente para suprir a demanda simultânea da colônia, o sistema executa o protocolo de corte ordenado:

```mermaid
graph TD
    Vento[Medição do Vento Atual] --> Regressao[Calcular Previsão Eólica e R²]
    Regressao --> Balanco[Calcular Saldo: Geração vs Consumo Total]
    Balanco --> Check{Geração >= Consumo Total?}
    Check -- "Sim" --> TodosAtivos[Manter Todos os Módulos Ligados]
    Check -- "Não" --> DesligarLab[Desligar Módulos Não Essenciais (Laboratório)]
    DesligarLab --> CheckEssenciais{Geração supre Módulos Essenciais?}
    CheckEssenciais -- "Sim" --> AlertaAmbar[Operar em Modo de Economia - Status Atenção]
    CheckEssenciais -- "Não" --> Bateria[Acionar Banco de Baterias de Reserva]
    Bateria --> AlertaCritico[Disparar Alerta Crítico de Fuga Energética]
```
