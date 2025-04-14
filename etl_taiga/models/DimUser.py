from peewee import *
from etl_taiga.models import BaseModel
from etl_taiga.models import db
from etl_taiga.models import DimRole


class DimUser(BaseModel):
    """tabela dim_user"""

    id_user = AutoField(primary_key=True)
    name_user = CharField(max_length=200, null=False)
    email = CharField(max_length=200, null=False)
    password = CharField(max_length=400, null=True)
    id_role = ForeignKeyField(
        DimRole, backref="users", column_name="id_role", on_delete="CASCADE", null=False
    )

    class Meta:
        table_name = "dim_user"
