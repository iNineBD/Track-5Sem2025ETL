from peewee import AutoField, CharField, ForeignKeyField
from etl_taiga.models import BaseModel
from etl_taiga.models.DimPlatform import DimPlatform


class DimProject(BaseModel):
    """tabela dim_project"""

    id_project = AutoField(primary_key=True)
    name_project = CharField(max_length=200, null=False)
    description = CharField(max_length=9999, null=False)
    id_platform = ForeignKeyField(
        DimPlatform, backref="platforms", column_name="id_platform", null=False
    )

    class Meta:
        table_name = "dim_project"
