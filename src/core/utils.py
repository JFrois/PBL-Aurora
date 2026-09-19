"""
Módulo Utilitário Global — Core
Base Aurora Siger | Fase 6
"""

import os


def limpar_tela():
    """Limpa o terminal de forma compatível com Windows e Unix."""
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    """Pausa a execução até o utilizador pressionar Enter."""
    input("\n[Pressione Enter para continuar...]")


def exibir_cabecalho(titulo: str):
    """Exibe um cabeçalho padronizado para as interfaces CLI."""
    limpar_tela()
    print("=" * 70)
    print(titulo.center(70))
    print("=" * 70)
