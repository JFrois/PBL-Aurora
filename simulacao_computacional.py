"""Execução independente da simulação energética da Fase 7."""

import sqlite3

from src.fase7_sifsm import banco, simulacao


def main() -> None:
    """Prepara os dados quando necessário e executa a simulação."""
    try:
        banco.inicializar_banco()

        if banco.contar_leituras() == 0:
            banco.carregar_csv_para_banco()

        simulacao.executar_simulacao()

    except (banco.ErroBanco, ValueError, sqlite3.Error, OSError) as erro:
        print(f"Não foi possível executar a simulação: {erro}")
        raise SystemExit(1) from erro


if __name__ == "__main__":
    main()