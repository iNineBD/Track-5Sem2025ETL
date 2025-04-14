from peewee import *
from etl_taiga.models import BaseModel


class DimProject(BaseModel):
    """tabela dim_project"""

    id_project = AutoField(primary_key=True)
    name_project = CharField(max_length=200, null=False)
    description = CharField(max_length=400, null=False)

    class Meta:
        table_name = "dim_project"
