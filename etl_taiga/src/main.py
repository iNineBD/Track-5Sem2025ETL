# etl_taiga/src/main.py

# Importando a classe DBSessionManager da conexão do banco de dados
from etl_taiga.db.Connection import DBSessionManager

def main():
    # Criando uma instância da classe DBSessionManager
    db_session_manager = DBSessionManager()

    # Chamando o método conectar_banco para inicializar a sessão do banco
    sessao = db_session_manager.conectar_banco()

    # Verificando se a sessão foi criada corretamente
    if sessao:
        print("Conexão com o banco de dados estabelecida com sucesso!")
    else:
        print("Falha na conexão com o banco de dados.")

if __name__ == "__main__":
    main()


'''
"""
Main module for the ETL pipeline.
"""
#!/usr/bin/env python3

from etl_taiga.db.Connection import DBSessionManager
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
'''

