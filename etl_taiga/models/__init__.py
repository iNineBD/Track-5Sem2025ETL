import os
from dotenv import load_dotenv
from peewee import *

load_dotenv()

TAIGA_USER = os.getenv("TAIGA_USER")
TAIGA_PASSWORD = os.getenv("TAIGA_PASSWORD")
TAIGA_HOST = os.getenv("TAIGA_HOST")
TAIGA_PORT = os.getenv("TAIGA_PORT")
TAIGA_DB = os.getenv("TAIGA_DB")
DB_SCHEMA = os.getenv("DB_SCHEMA")

db = PostgresqlDatabase(
    TAIGA_DB, user=TAIGA_USER, password=TAIGA_PASSWORD, host=TAIGA_HOST, port=TAIGA_PORT
)


class BaseModel(Model):
    class Meta:
        database = db
        schema = DB_SCHEMA
