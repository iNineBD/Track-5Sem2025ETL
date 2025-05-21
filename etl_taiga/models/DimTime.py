from peewee import AutoField, DateField, ForeignKeyField, IntegerField

from etl_taiga.models import BaseModel

from .Date import DimDay, DimHour, DimMinute, DimMonth, DimYear


class DimTime(BaseModel):
    """tabela dim_time"""

    id_time = AutoField(primary_key=True)

    id_day = ForeignKeyField(DimDay, backref="times", column_name="id_day", null=False)
    id_month = ForeignKeyField(
        DimMonth, backref="times", column_name="id_month", null=False
    )
    id_year = ForeignKeyField(
        DimYear, backref="times", column_name="id_year", null=False
    )
    id_hour = ForeignKeyField(
        DimHour, backref="times", column_name="id_hour", null=False
    )
    id_minute = ForeignKeyField(
        DimMinute, backref="times", column_name="id_minute", null=False
    )

    class Meta:
        table_name = "dim_time"
