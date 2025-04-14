from peewee import *
from etl_taiga.models import BaseModel

class DimStatus(BaseModel):
    """tabela dim_status"""
    id_status = AutoField(primary_key=True)
    name_status = CharField(max_length=200, null=False)

    class Meta:
        table_name = 'dim_status'