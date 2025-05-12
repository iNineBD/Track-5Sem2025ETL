from peewee import AutoField, CharField
from etl_taiga.models import BaseModel


class DimCard(BaseModel):
    """tabela dim_card"""

    id_card = AutoField(primary_key=True)
    name_card = CharField(max_length=200, null=False)
    description = CharField(max_length=400, null=False)

    class Meta:
        table_name = "dim_card"
