from dotenv import load_dotenv
import os
from peewee import *
from etl_taiga.db.Connection import database_config

load_dotenv()
DB_SCHEMA = os.getenv("DB_SCHEMA")
db = database_config()


class BaseModel(Model):
    class Meta:
        database = db
        schema = DB_SCHEMA
