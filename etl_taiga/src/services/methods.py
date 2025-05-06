# src/services/methods.py
"""
Methods module for database operations.
"""

from etl_taiga.models import (
    DimProject,
    DimCard,
    DimRole,
    DimUser,
    DimTag,
    DimStatus,
    FatoCard,
    DimTime,
)
from etl_taiga.models.Date import DimDay, DimHour, DimMinute, DimMonth, DimYear
from etl_taiga.db.Connection import connect_database, database_config
from peewee import *
import pandas as pd
import logging

db = database_config()
db_open = connect_database(db)


def delete_all_data(db_open):
    """
    Delete all data from the database.
    """
    tables_to_drop = [
        DimCard.DimCard,
        DimTag.DimTag,
        DimTime.DimTime,
        DimStatus.DimStatus,
        DimProject.DimProject,
        DimRole.DimRole,
        DimDay,
        DimHour,
        DimMinute,
        DimMonth,
        DimYear,
    ]

    tables_to_create = [
        DimRole.DimRole,
        DimYear,
        DimMonth,
        DimDay,
        DimHour,
        DimMinute,
        DimStatus.DimStatus,
        DimProject.DimProject,
        DimTag.DimTag,
        DimTime.DimTime,
        DimCard.DimCard,
        FatoCard.FatoCard,
    ]
    try:
        with db_open.atomic():
            db.execute_sql("SET session_replication_role = replica;")
            db.execute_sql("DELETE FROM dw_track_develop.dim_user WHERE password IS NULL")
            db.drop_tables(tables_to_drop, safe=True, cascade=True)
            db.create_tables(tables_to_create, safe=True)

            db.execute_sql("SET session_replication_role = DEFAULT;")

        print("Database reset successfully.")

    except OperationalError as e:
        print(f"Error resetting database: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        if not db.is_closed():
            db.close()
            print("Database connection closed.")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def insert_data(
    db,
    df_fact_cards,
    df_projects,
    df_dim_cards,
    df_status,
    df_tags,
    df_users,
    df_roles,
    df_dim_time,
    df_dim_year,
    df_dim_month,
    df_dim_day,
    df_dim_hour,
    df_dim_minute,
    batch_size=100,
):
    insertion_sequence = [
        (DimRole.DimRole, df_roles),
        (DimUser.DimUser, df_users),
        (DimYear, df_dim_year),
        (DimMonth, df_dim_month),
        (DimDay, df_dim_day),
        (DimHour, df_dim_hour),
        (DimMinute, df_dim_minute),
        (DimStatus.DimStatus, df_status),
        (DimProject.DimProject, df_projects),
        (DimTag.DimTag, df_tags),
        (DimTime.DimTime, df_dim_time),
        (DimCard.DimCard, df_dim_cards),
        (FatoCard.FatoCard, df_fact_cards),
    ]

    results = {"tables": {}, "status": "success", "total": 0}

    try:
        # Processar cada inserção na ordem correta
        for model_class, df in insertion_sequence:
            if df is None or df.empty:
                logger.warning(f"DataFrame para {model_class.__name__} esta vazio ou nulo")
                results[model_class.__name__] = 0
                continue

            if model_class == DimUser.DimUser:
                existing_ids_user = {r.id_user for r in model_class.select(model_class.id_user)}

                if 'id_user' in df.columns:
                    df = df[~df['id_user'].isin(existing_ids_user)]

                if df.empty:
                    logger.info(f"Nenhum novo registro para inserir em Dim User")
                    results["tables"][model_class.__name__] = 0
                    continue

            if model_class == FatoCard.FatoCard:
                existing_ids_fato = {r.id_fato_card for r in model_class.select(model_class.id_fato_card)}

                if 'id_fato_card' in df.columns:
                    df = df[~df['id_fato_card'].isin(existing_ids_fato)]

                if df.empty:
                    logger.info(f"Nenhum novo registro para inserir em FatoCard")
                    results["tables"][model_class.__name__] = 0
                    continue

            data = df.replace({pd.NA: None}).to_dict("records")
            inserted = 0

            with db.atomic():
                for batch in chunked(data, batch_size):
                    model_class.insert_many(batch).execute()
                    inserted += len(batch)

            logger.info(f"Inseridos {inserted} registros em {model_class.__name__}")
            results["tables"][model_class.__name__] = inserted
            results["total"] += inserted

        return results

    except Exception as e:
        logger.error(f"Erro na inserção: {str(e)}", exc_info=True)
        results["status"] = "error"
        results["error"] = str(e)
        if not db.is_closed():
            db.rollback()
        return results
