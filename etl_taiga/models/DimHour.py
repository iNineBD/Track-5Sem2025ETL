from peewee import *
from etl_taiga.models import BaseModel

class DimHour(BaseModel):
    """tabela dim_hour"""
    id_hour = AutoField(primary_key=True)
    hour = IntegerField(null=False)

    class Meta:
        table_name = 'dim_hour'