# src/services/methods.py
"""
Methods module for database operations.
"""
import logging
import os
import pandas as pd
from peewee import Model, OperationalError, chunked
from prefect import task
from prefect.cache_policies import NO_CACHE
from etl_taiga.db.Connection import connect_database, database_config
from etl_taiga.models import (
    DimCard,
    DimProject,
    DimRole,
    DimStatus,
    DimTag,
    DimTime,
    DimUser,
    FatoCard,
    DimPlatform,
)
from etl_taiga.models.Date import DimDay, DimHour, DimMinute, DimMonth, DimYear
from dotenv import load_dotenv

load_dotenv()
db = database_config()
db_open = connect_database(db)
DB_SCHEMA = os.getenv("DB_SCHEMA")


@task(cache_policy=NO_CACHE)
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
        DimPlatform.DimPlatform,
    ]

    tables_to_create = [
        DimRole.DimRole,
        DimYear,
        DimMonth,
        DimDay,
        DimHour,
        DimMinute,
        DimStatus.DimStatus,
        DimPlatform.DimPlatform,
        DimProject.DimProject,
        DimTag.DimTag,
        DimTime.DimTime,
        DimCard.DimCard,
        FatoCard.FatoCard,
    ]
    try:
        with db_open.atomic():
            db.execute_sql("SET session_replication_role = replica;")
            db.execute_sql(f"DELETE FROM {DB_SCHEMA}.dim_user WHERE password IS NULL")
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


@task(cache_policy=NO_CACHE)
def insert_data(
    db,
    df_fact_cards,
    df_platform,
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
        (DimDay, df_dim_day),  # Até aqui é a fase 1 (inserir dias)
        (DimHour, df_dim_hour),
        (DimMinute, df_dim_minute),
        (DimStatus.DimStatus, df_status),
        (DimPlatform.DimPlatform, df_platform),
        (DimProject.DimProject, df_projects),
        (DimTag.DimTag, df_tags),
        (DimTime.DimTime, df_dim_time),  # DimTime depende de DimDay
        (DimCard.DimCard, df_dim_cards),
        (FatoCard.FatoCard, df_fact_cards),
    ]

    results = {"tables": {}, "status": "success", "total": 0}

    # coloque o numero 31 onde o day for NaN
    df_dim_day["day"] = df_dim_day["day"].fillna(31).astype(int)
    df_dim_hour['hour'] = df_dim_hour['hour'].fillna(0).astype(int)
    df_dim_minute['minute'] = df_dim_minute['minute'].fillna(0).astype(int)
    df_dim_month['month'] = df_dim_month['month'].fillna(6).astype(int)
    df_dim_year['year'] = df_dim_year['year'].fillna(2025).astype(int)

    def clean_record(record):
        for key, value in record.items():
            if isinstance(value, float):
                if pd.isna(value):
                    record[key] = None
                elif value.is_integer():
                    record[key] = int(value)
        return record

    try:
        # 1ª fase: inserir até DimDay (inclusive)
        for model_class, df in insertion_sequence:
            # Parar após inserir DimDay
            if model_class == DimHour:
                break

            if df is None or df.empty:
                logger.warning(f"DataFrame para {model_class.__name__} está vazio ou nulo")
                results["tables"][model_class.__name__] = 0
                continue

            if model_class == DimUser.DimUser:
                existing_ids_user = {r.id_user for r in model_class.select(model_class.id_user)}
                if "id_user" in df.columns:
                    df = df[~df["id_user"].isin(existing_ids_user)]
                if df.empty:
                    logger.info("Nenhum novo registro para inserir em Dim User")
                    results["tables"][model_class.__name__] = 0
                    continue

            if model_class == DimDay and "day" in df.columns:
                df = df.dropna(subset=["day"])

            required_fields = {
                "DimYear": ["year"],
                "DimMonth": ["month"],
                "DimDay": ["day"],
                "DimHour": ["hour"],
                "DimMinute": ["minute"],
            }
            required = required_fields.get(model_class.__name__, [])
            for field in required:
                if field in df.columns:
                    before_count = len(df)
                    df = df[df[field].notnull()]
                    after_count = len(df)
                    if before_count != after_count:
                        logger.warning(f"{before_count - after_count} registros removidos com {field}=null para {model_class.__name__}")

            data = [clean_record(r) for r in df.to_dict("records")]
            inserted = 0

            with db.atomic():
                for batch in chunked(data, batch_size):

                    model_class.insert_many(batch).execute()
                    inserted += len(batch)

            logger.info(f"Inseridos {inserted} registros em {model_class.__name__}")
            results["tables"][model_class.__name__] = inserted
            results["total"] += inserted

        # Commit da 1ª fase para garantir DimDay salvo no banco
        if not db.is_closed():
            db.commit()

        # 2ª fase: inserir o resto, incluindo DimTime
        for model_class, df in insertion_sequence:
            if model_class in [DimRole.DimRole, DimUser.DimUser, DimYear, DimMonth, DimDay]:
                continue  # Já inserido

            if df is None or df.empty:
                logger.warning(f"DataFrame para {model_class.__name__} está vazio ou nulo")
                results["tables"][model_class.__name__] = 0
                continue

            if model_class == DimUser.DimUser:
                existing_ids_user = {r.id_user for r in model_class.select(model_class.id_user)}
                if "id_user" in df.columns:
                    df = df[~df["id_user"].isin(existing_ids_user)]
                if df.empty:
                    logger.info("Nenhum novo registro para inserir em Dim User")
                    results["tables"][model_class.__name__] = 0
                    continue

            if model_class == FatoCard.FatoCard:
                existing_ids_fato = {r.id_fato_card for r in model_class.select(model_class.id_fato_card)}
                if "id_fato_card" in df.columns:
                    df = df[~df["id_fato_card"].isin(existing_ids_fato)]
                if df.empty:
                    logger.info("Nenhum novo registro para inserir em FatoCard")
                    results["tables"][model_class.__name__] = 0
                    continue

            if model_class == DimTime and "id_day" in df.columns:
                existing_day_ids = {r.id_day for r in DimDay.select(DimDay.id_day)}
                df = df[df["id_day"].isin(existing_day_ids)]
                if df.empty:
                    logger.info("Nenhum novo registro válido para inserir em DimTime")
                    results["tables"][model_class.__name__] = 0
                    continue

            required_fields = {
                "DimYear": ["year"],
                "DimMonth": ["month"],
                "DimDay": ["day"],
                "DimHour": ["hour"],
                "DimMinute": ["minute"],
            }
            required = required_fields.get(model_class.__name__, [])
            for field in required:
                if field in df.columns:
                    before_count = len(df)
                    df = df[df[field].notnull()]
                    after_count = len(df)
                    if before_count != after_count:
                        logger.warning(f"{before_count - after_count} registros removidos com {field}=null para {model_class.__name__}")

            data = [clean_record(r) for r in df.to_dict("records")]
            inserted = 0

            with db.atomic():
                for batch in chunked(data, batch_size):
                    if model_class == DimYear:
                        for record in batch:
                            record["year"] = 2025

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
