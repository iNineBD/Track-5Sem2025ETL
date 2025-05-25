from peewee import AutoField, CharField

from etl_taiga.models import BaseModel


class DimRole(BaseModel):
    """tabela dim_role"""

    id_role = AutoField(primary_key=True)
    name_role = CharField(max_length=200, null=False)

    class Meta:
        table_name = "dim_role"
