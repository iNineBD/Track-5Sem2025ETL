from peewee import *
from etl_taiga.models import BaseModel


class DimMinute(BaseModel):
    """tabela dim_minute"""

    id_minute = AutoField(primary_key=True)
    minute = IntegerField(null=False)

    class Meta:
        table_name = "dim_minute"
