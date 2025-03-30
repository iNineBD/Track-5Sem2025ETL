"""
Methods module for database operations.
"""

from sqlalchemy.orm import sessionmaker
from etl_taiga.models import (
    FatoCard,
    DimUser,
    DimTag,
    DimStatus,
    DimRole,
    DimProject,
)
from etl_taiga.src.services.Auth.auth_taiga import Auth
from etl_taiga.db.Connection import Connection


def get_auth():
    """
    Authenticate with Taiga and return the token.
    """
    auth = Auth()
    if not auth:
        raise ValueError("Erro ao autenticar no Taiga")
    return auth


def get_session():
    """
    Return the database session.
    """
    session = Connection()
    return session


def reset_database(session: sessionmaker):
    """
    Reset the database by deleting all records.
    """
    try:
        session.query(FatoCard).delete()
        session.query(DimUser).delete()
        session.query(DimTag).delete()
        session.query(DimStatus).delete()
        session.query(DimRole).delete()
        session.query(DimProject).delete()
        session.commit()
        print("Dados apagados com sucesso")
    except Exception as error:
        session.rollback()
        print(f"Erro ao apagar dados: {error}")


def insert_data(session, data):
    """
    Insert data into the database.
    """
    try:
        df_projects, df_roles, df_users, df_tags, df_status, df_fact_cards = data

        session.bulk_insert_mappings(DimProject, df_projects.to_dict(orient="records"))
        session.bulk_insert_mappings(DimRole, df_roles.to_dict(orient="records"))
        session.bulk_insert_mappings(DimUser, df_users.to_dict(orient="records"))
        session.bulk_insert_mappings(DimTag, df_tags.to_dict(orient="records"))
        session.bulk_insert_mappings(DimStatus, df_status.to_dict(orient="records"))
        session.bulk_insert_mappings(FatoCard, df_fact_cards.to_dict(orient="records"))

        session.commit()
        print("Dados inseridos com sucesso")
    except Exception as error:
        session.rollback()
        print(f"Erro ao inserir dados: {error}")
