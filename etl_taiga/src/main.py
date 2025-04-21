"""
Main module for the ETL pipeline.
"""
# !/usr/bin/env python3

from etl_taiga.db.Connection import conectar_banco
from services.get_data import (
    pipeline_projets,
    pipeline_roles,
    pipeline_users,
    pipeline_tags,
    pipeline_status,
    pipeline_fact_cards,
)
from services.methods import reset_database, insert_data


def main():
    """
    Main function to execute the ETL pipeline.
    """
    session = conectar_banco()
    projetos = pipeline_projets()
    roles = pipeline_roles()
    users = pipeline_users(roles)
    tags = pipeline_tags()
    status = pipeline_status()
    fact_cards = pipeline_fact_cards()

    try:
        # Chama a função para apagar os dados das tabelas
        reset_database(session)

        # Chama a função para inserir os novos dados
        insert_data(session, projetos, roles, users, tags, status, fact_cards)

    except Exception as error:  # Replace with the specific exception type
        print(f"Ocorreu um erro na execução: {error}")

    finally:
        # Fechar a sessão
        session.close()


if __name__ == "__main__":
    main()
