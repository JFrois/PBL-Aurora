# Missão Aurora Siger 🚀

Este repositório contém a documentação e o protótipo inicial de telemetria da nave **Aurora**. O projeto integra conceitos de Ciência da Computação, Engenharia de Foguetes e Meteorologia para validar a segurança de um lançamento espacial.

## 📋 Sobre o Projeto
O objetivo desta fase é fornecer informações essenciais sobre o funcionamento de foguetes, abrangendo cálculos técnicos, estimativa de custos e o impacto social da exploração espacial. O projeto culmina em um script Python que processa dados de telemetria simulados para autorizar ou abortar uma decolagem.

### Parâmetros de Telemetria Monitorados:
* **Temperatura:** Interna e externa.
* **Integridade Estrutural:** Status operacional do corpo da nave.
* **Níveis de Energia:** Capacidade e carga disponível (%).
* **Pressão:** Monitoramento dos tanques.
* **Módulos Críticos:** Verificação de status dos sistemas essenciais.

---

## 👥 Equipe (FIAP 2026)
| Nome | RM |
| :--- | :--- |
| **Juan de Lucas Frois** | RM563260 |
| **Flávia Roberta Pennachin** | RM561860 |
| **Pedro Valente Toledo** | RM570394 |
| **Bruno Antonio Santos Silva** | RM573180 | 
| **Renan Mano Otero** | RM573615 |

---

## 🛠️ Implementação Técnica
O script Python realiza a leitura dos dados simulados e executa as seguintes verificações de segurança para permitir o lançamento:

### Regras de Negócio:
* **Integridade Estrutural:** Deve ser 1 (Operacional).
* **Energia:** Mínimo de 80% para decolagem segura.
* **Pressão:** Deve estar entre 300 e 450 psi.
* **Temperatura Interna:** Faixa segura entre 18°C e 25°C.
* **Módulos Críticos:** Devem retornar status "OK".

### Exemplo de Saída:
```text
--- RELATÓRIO OPERACIONAL ---
STATUS: DECOLAGEM ABORTADA!
MOTIVOS:
- Energia insuficiente: 45.2% (Mínimo: 80%)
- Pressão fora dos padrões: 480.0 psi
```

---

## 🌍 Reflexão Ética e Sustentabilidade
O projeto aborda a responsabilidade na exploração espacial, discutindo temas como:
* **Lixo Espacial:** Riscos de colisão e desórbita programada.
* **Impacto Social:** Como a tecnologia aeroespacial auxilia na agricultura e prevenção de desastres na Terra.
* **Ética:** Justificativa da expansão humana versus problemas globais imediatos.

---

**Instituição:** FIAP
**Ano:** 2026
