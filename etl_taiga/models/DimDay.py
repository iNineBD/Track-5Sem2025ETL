from peewee import *
from etl_taiga.models import BaseModel

class DimDay(BaseModel):
    """tabela dim_day"""
    id_day = AutoField(primary_key=True)
    day = IntegerField(null=False)

    class Meta:
        table_name = 'dim_day'