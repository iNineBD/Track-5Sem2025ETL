from sqlalchemy.orm import Session
from models import (
    Base,
    FatoCard,
    DimUser,
    DimTag,
    DimStatus,
    DimRole,
    DimProject,
)
from src.services.Auth import auth_taiga
from db.Connection import conectar_banco
from sqlalchemy.orm import sessionmaker

def get_auth():
    auth = auth_taiga()
    if not auth:
        raise ValueError("Erro ao autenticar no Taiga")
    return auth


def get_session():
    """retorna a session do banco"""
    session = conectar_banco()
    return session


def reset_database(session: Session):

    try:
        # Apagar os dados das tabelas (remover registros de fato primeiro)
        session.query(FatoCard).delete()
        session.query(DimUser).delete()
        session.query(DimTag).delete()
        session.query(DimStatus).delete()
        session.query(DimRole).delete()
        session.query(DimProject).delete()

        # Commit das alterações
        session.commit()
        print("Dados apagados com sucesso")
    except Exception as e:
        session.rollback()
        print(f"Erro ao apagar dados: {e}")


def insert_data(session, df_projects, df_roles, df_users, df_tags, df_status, df_fact_cards):
    try:
        # Converter DataFrames para dicionários
        df_projects = df_projects.astype({'id': 'int', 'description': 'str', 'name': 'str', 'created_date': 'str', 'modified_date': 'str'})
        df_roles = df_roles.astype({'id': 'int', 'name': 'str'})
        df_users = df_users.astype({'id': 'int', 'full_name': 'str', 'color': 'str', 'fk_id_role': 'int'})
        df_tags = df_tags.astype({'id': 'int', 'name': 'str', 'color': 'str', 'id_card': 'int', 'id_project': 'int'})
        df_status = df_status.astype({'id': 'int', 'name': 'str', 'id_card': 'int', 'id_project': 'int'})
        df_fact_cards = df_fact_cards.astype({'fk_id_status': 'int', 'fk_id_tag': 'int', 'fk_id_user': 'int', 'fk_id_project': 'int', 'qtd_card': 'int'})

        # Inserir DimProject usando bulk_insert_mappings
        session.bulk_insert_mappings(DimProject, df_projects.to_dict(orient="records"))

        # Inserir DimRole
        session.bulk_insert_mappings(DimRole, df_roles.to_dict(orient="records"))

        # Inserir DimUser
        session.bulk_insert_mappings(DimUser, df_users.to_dict(orient="records"))

        # Inserir DimTag
        session.bulk_insert_mappings(DimTag, df_tags.to_dict(orient="records"))

        # Inserir DimStatus
        session.bulk_insert_mappings(DimStatus, df_status.to_dict(orient="records"))

        # Inserir FatoCard
        session.bulk_insert_mappings(FatoCard, df_fact_cards.to_dict(orient="records"))

        # Commit das alterações
        session.commit()
        print("Dados inseridos com sucesso")
    except Exception as e:
        session.rollback()
        print(f"Erro ao inserir dados: {e}")
