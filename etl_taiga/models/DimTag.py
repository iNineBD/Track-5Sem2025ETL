from peewee import *
from etl_taiga.models import BaseModel


class DimTag(BaseModel):
    """tabela dim_tag"""

    id_tag = AutoField(primary_key=True)
    name_tag = CharField(null=False, unique=True)

    class Meta:
        table_name = "dim_tag"
