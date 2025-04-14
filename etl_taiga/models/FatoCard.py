from peewee import *
from etl_taiga.models import *
from etl_taiga.models.DimCard import DimCard
from etl_taiga.models.DimProject import DimProject
from etl_taiga.models.DimStatus import DimStatus
from etl_taiga.models.DimTag import DimTag
from etl_taiga.models.DimTime import DimTime
from etl_taiga.models.DimUser import DimUser


class FatoCard(BaseModel):
    """tabela fato_card"""

    id_fato_card = AutoField(primary_key=True)

    id_card = ForeignKeyField(
        DimCard, column_name="id_card", backref="fatos", on_delete="CASCADE"
    )
    id_project = ForeignKeyField(
        DimProject, column_name="id_project", backref="fatos", on_delete="CASCADE"
    )
    id_user = ForeignKeyField(
        DimUser, column_name="id_user", backref="fatos", on_delete="CASCADE"
    )
    id_status = ForeignKeyField(
        DimStatus,
        column_name="id_status",
        backref="fatos",
    )

    id_time_created = ForeignKeyField(
        DimTime,
        column_name="id_time_created",
        backref="fatos_criados",
        on_delete="CASCADE",
    )
    id_time_finished = ForeignKeyField(
        DimTime,
        column_name="id_time_finished",
        backref="fatos_finalizados",
        null=True,
        on_delete="CASCADE",
    )

    id_tag = ForeignKeyField(
        DimTag, column_name="id_tag", backref="fatos", null=True, on_delete="CASCADE"
    )

    qtd_cards = IntegerField(default=1)

    class Meta:
        table_name = "fato_cards"
