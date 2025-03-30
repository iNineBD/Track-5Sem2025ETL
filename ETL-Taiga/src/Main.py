from db.Connection import conectar_banco
from src.services.GetData import (
    pipeline_projets,
    pipeline_roles,
    pipeline_users,
    pipeline_tags,
    pipeline_status,
    pipeline_fact_cards,
)
from src.services.Methods import reset_database, insert_data


def main():
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

    except Exception as e:
        print(f"Ocorreu um erro na execução: {e}")

    finally:
        # Fechar a sessão
        session.close()


if __name__ == "__main__":
    main()
