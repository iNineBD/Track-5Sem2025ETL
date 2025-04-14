from peewee import *
from etl_taiga.models import BaseModel


class DimYear(BaseModel):
    """tabela dim_year"""

    id_year = AutoField(primary_key=True)
    year = IntegerField(null=False)

    class Meta:
        table_name = "dim_year"
