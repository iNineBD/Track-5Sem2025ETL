from peewee import AutoField, CharField
from etl_taiga.models import BaseModel


class DimPlatform(BaseModel):
    """tabela dim_platform"""

    id_platform = AutoField(primary_key=True)
    name_platform = CharField(max_length=200, null=False)

    class Meta:
        table_name = "dim_platform"
