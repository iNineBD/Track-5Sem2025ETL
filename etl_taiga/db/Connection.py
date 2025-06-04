import os

from dotenv import load_dotenv
from peewee import OperationalError, PostgresqlDatabase
from prefect import task
from prefect.tasks import Task
from prefect.tasks import NO_CACHE


@task
def database_config():
    load_dotenv()

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_DATABASE = os.getenv("DB_DATABASE")

    db = PostgresqlDatabase(
        DB_DATABASE, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    return db


@task(cache_policy=NO_CACHE)  # desativa cache explicitamente
def connect_database(db):
    try:
        db = database_config()
        db.connect()
    except OperationalError as e:
        print(f"{e}")
        raise
    return db
