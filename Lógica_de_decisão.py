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
def colonia_aurora_decisao(colonia_aurora_dados):
    consumo = 0
    sistemas = colonia_aurora_dados["sistemas_consumo"]
    nivel_bateria = colonia_aurora_dados["sistema_energetico"]["reserva_baterias"]["nivel_atual_porcentagem"]
    nivel_critico_bateria = colonia_aurora_dados["sistema_energetico"]["reserva_baterias"]["nivel_critico_porcentagem"]

# Verificar consumo
    for nome,dados in sistemas.items():
        consumo += dados["consumo_atual_mw"]

# Verificação de de Nível da Bateria
    if nivel_bateria < nivel_critico_bateria and consumo > 60:
        print("MODO ECONOMIA ATIVADO")
        for nome,dados in sistemas.items():
            if not dados["essencial"]:
                dados["status"] = "Desligado"
                print(f"{nome} foi desligado")
    elif nivel_bateria < 50:
        print("Alerta: reduzir consumo de energia")
    else:
        print("Sistema operando normalmente")
    

dados = memoria_colonia_aurora()
colonia_aurora_decisao(dados)
        

