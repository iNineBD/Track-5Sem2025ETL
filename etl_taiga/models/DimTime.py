from .Date import DimDay, DimHour, DimMinute, DimMonth, DimYear
from peewee import AutoField, IntegerField, DateField, ForeignKeyField
from etl_taiga.models import BaseModel


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
