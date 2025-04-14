from peewee import *
from etl_taiga.models import BaseModel, DimHour, DimMinute, DimDay, DimMonth, DimYear


class DimTime(BaseModel):
    """tabela dim_time"""

    id_time = AutoField(primary_key=True)
    date = DateField(null=False)
    id_day = ForeignKeyField(
        DimDay, backref="times", column_name="id_day", on_delete="CASCADE", null=False
    )
    id_month = ForeignKeyField(
        DimMonth,
        backref="times",
        column_name="id_month",
        on_delete="CASCADE",
        null=False,
    )
    id_year = ForeignKeyField(
        DimYear, backref="times", column_name="id_year", on_delete="CASCADE", null=False
    )
    id_hour = ForeignKeyField(
        DimHour, backref="times", column_name="id_hour", on_delete="CASCADE", null=False
    )
    id_minute = ForeignKeyField(
        DimMinute,
        backref="times",
        column_name="id_minute",
        on_delete="CASCADE",
        null=False,
    )

    class Meta:
        table_name = "dim_time"
