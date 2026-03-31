import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configurações da Simulação
rows = 500
start_time = datetime(2026, 3, 30, 10, 0, 0)

data = {
    "timestamp": [(start_time + timedelta(seconds=i)).isoformat() for i in range(rows)],
    "temp_interna_c": np.random.uniform(17.5, 25.5, rows).round(2),
    "temp_externa_c": np.random.uniform(10.0, 30.0, rows).round(2),
    "integridade_estrutural": np.random.choice([1, 0], rows, p=[0.98, 0.02]),
    "energia_capacidade_kwh": [5000] * rows,
    "energia_carga_pct": np.linspace(99, 75, rows).round(2), # Simula descarga lenta
    "energia_consumo_decolagem_kwh": [1200] * rows,
    "energia_perdas_kwh": np.random.uniform(10, 20, rows).round(2),
    "pressao_tanques_psi": np.random.uniform(290, 460, rows).round(2),
    "status_modulos": np.random.choice(["OK", "FALHA_SISTEMA", "RECALIBRANDO"], rows, p=[0.95, 0.02, 0.03])
}

df = pd.DataFrame(data)

# Exportar para CSV
csv_filename = "telemetria_nave.csv"
df.to_csv(csv_filename, index=False)

print(f"Arquivo '{csv_filename}' gerado com sucesso com {rows} linhas.")