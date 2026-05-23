def memoria_colonia_aurora():

# Configurando a hierarquia dos dados e os subsistemas da base usando estruturas de chave-valor
    colonia_aurora_dados = {
        "sistema_energetico": {
            "tipo_geracao": {
                "solar": {
                    "nome": "Painéis Fotovoltaicos",
                    "status": "ativo",
                    "capacidade_max_mw": 120.0,
                    "geracao_atual": 50.0,
                    "consumo_atual": 2.5
                },
                "eolico": {
                    "nome": "Turbinas Eólicas",
                    "status": "ativo",
                    "capacidade_max_mw": 80.0,
                    "geracao_atual": 30.0,
                    "consumo_atual": 1.5
                }
            },
            "reserva_baterias": {
                "capacidade_total_mwh": 600.0,
                "nivel_atual_mwh": 150.0,
                "nivel_atual_porcentagem": 25.0,
                "nivel_critico_porcentagem": 20.0
            }
        },
        "clima": {
            "temperatura_C": 18.5,
            "vento_km_h": 36.0
        },

        "sistemas_consumo": {
            # --- SISTEMAS ESSENCIAIS (Suporte à Vida) ---
            "suporte_medico": {
                "nome": "Suporte Médico",
                "consumo_atual_mw": 25.0,
                "essencial": True,
                "status": "ligado",
            },
            "habitacao": {
                "nome": "Habitação",
                "consumo_atual_mw": 30.0,
                "essencial": True,
                "status": "ligado",
            },
            # --- SISTEMAS NÃO ESSENCIAIS (Gerenciáveis em Crise) ---
            "logistica": {
                "nome": "Logística",
                "consumo_atual_mw": 15.0,
                "essencial": False,
                "status": "ligado",
            },
            "laboratorio": {
                "nome": "Laboratório",
                "consumo_atual_mw": 20.0,
                "essencial": False,
                "status": "ligado",
            }
        }
    }
    return colonia_aurora_dados


# --- Estruturação de Decisões da Colônia Aurora ---
def colonia_aurora_decisao(colonia_aurora_dados, geracao_eolica_prevista=None):
    sistemas = colonia_aurora_dados["sistemas_consumo"]
    bateria = colonia_aurora_dados["sistema_energetico"]["reserva_baterias"]
    geradores = colonia_aurora_dados["sistema_energetico"]["tipo_geracao"]

    nivel_bateria = bateria["nivel_atual_porcentagem"]
    nivel_critico = bateria["nivel_critico_porcentagem"]

    # Calcular consumo total
    consumo_total = sum(s["consumo_atual_mw"] for s in sistemas.values())

    # Usar geração eólica prevista se fornecida, caso contrário usar valor atual
    geracao_eolica = geracao_eolica_prevista if geracao_eolica_prevista is not None \
        else geradores["eolico"]["geracao_atual"]
    geracao_solar = geradores["solar"]["geracao_atual"]
    geracao_total = geracao_solar + geracao_eolica

    balanco_mw = geracao_total - consumo_total  # positivo = excedente, negativo = déficit

    # --- Lógica de Decisão ---
    if nivel_bateria < nivel_critico or balanco_mw < -5:
        # Bateria crítica OU déficit acima de 5 MW → modo economia obrigatório
        print("ALERTA CRÍTICO: MODO ECONOMIA ATIVADO")
        print(f"  Bateria: {nivel_bateria}% | Balanço: {balanco_mw:.1f} MW")
        for nome, dados in sistemas.items():
            if not dados["essencial"]:
                dados["status"] = "desligado"
                print(f"  {dados['nome']} desligado")
    elif balanco_mw < 0:
        # Déficit leve: geração < consumo mas bateria ainda estável
        print(f"ALERTA: déficit de {abs(balanco_mw):.1f} MW — consumo supera geração atual")
        print("  Recomendação: reduzir sistemas não essenciais")
    elif nivel_bateria < 50:
        print(f"AVISO: bateria em {nivel_bateria}% — monitorar consumo")
        print(f"  Geração: {geracao_total:.1f} MW | Consumo: {consumo_total:.1f} MW")
    else:
        print("Sistema operando normalmente")
        print(f"  Geração: {geracao_total:.1f} MW | Consumo: {consumo_total:.1f} MW | Balanço: +{balanco_mw:.1f} MW")

    return colonia_aurora_dados


dados = memoria_colonia_aurora()
colonia_aurora_decisao(dados)
