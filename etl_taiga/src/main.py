"""
Main module for the ETL pipeline.
"""

import logging
from datetime import datetime, timedelta

from prefect import flow

# !/usr/bin/env python3
from prefect.client.schemas.schedules import IntervalSchedule

from etl_taiga.db.Connection import connect_database, database_config
from etl_taiga.src.services.get_data import pipeline_main
from etl_taiga.src.services.methods import delete_all_data, insert_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("etl_taiga.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

schedule = IntervalSchedule(interval=timedelta(minutes=10))


@flow
def run_etl_process():
    """
    Main ETL process execution function.
    """
    # Initialize database connection
    db_config = database_config()
    db = connect_database(db_config)

    try:
        # Step 1: Reset database
        logger.info("Starting database reset...")
        start_time = datetime.now()

        delete_all_data(db)
        logger.info(f"Database reset completed in {datetime.now() - start_time}")

        # Step 2: Extract and transform data
        logger.info("Starting data extraction and transformation...")
        start_time = datetime.now()

        #        dataframes = pipeline_main()
        #        logger.info(f"Data transformation completed in {datetime.now() - start_time}")

        # Step 3: Load data
        logger.info("Starting data loading...")
        start_time = datetime.now()

        (
            fato_cards,
            df_platform,
            df_projects,
            df_cards,
            df_status,
            df_tags,
            df_users,
            df_roles,
            dim_time,
            dim_year,
            dim_month,
            dim_day,
            dim_hour,
            dim_minute,
        ) = pipeline_main()

        df_cards = df_cards.drop(
            columns=[
                "id_user",
                "id_tag",
                "id_status",
                "id_project",
                "day",
                "month",
                "year",
                "hour",
                "minute",
                "id_day",
                "id_month",
                "id_year",
                "id_hour",
                "id_minute",
                "id_time",
            ]
        )
        df_cards = df_cards.drop_duplicates(subset=["id_card"], keep="last")

        # Insert data
        result = insert_data(
            db,
            fato_cards,
            df_platform,
            df_projects,
            df_cards,
            df_status,
            df_tags,
            df_users,
            df_roles,
            dim_time,
            dim_year,
            dim_month,
            dim_day,
            dim_hour,
            dim_minute,
            batch_size=100,
        )

        if result["status"] == "success":
            logger.info(f"Data loading completed in {datetime.now() - start_time}")
            logger.info(f"Total records inserted: {result['total']}")
        else:
            logger.error(f"Data loading failed: {result['error']}")
            raise Exception(result["error"])

    except Exception as e:
        logger.error(f"ETL process failed: {str(e)}", exc_info=True)
        raise
    finally:
        if not db.is_closed():
            db.close()
        logger.info("Database connection closed")
        logger.info("ETL process completed")


if __name__ == "__main__":
    # run_etl_process() - descomente para rodar o ETL localmente sem automação
    run_etl_process.serve(name="etl10min", schedule=schedule)
