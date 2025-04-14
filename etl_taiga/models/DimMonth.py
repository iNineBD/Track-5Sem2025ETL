from peewee import *
from etl_taiga.models import BaseModel


class DimMonth(BaseModel):
    """tabela dim_month"""

    id_month = AutoField(primary_key=True)
    month = IntegerField(null=False)

    class Meta:
        table_name = "dim_month"
