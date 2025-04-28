from etl_taiga.models import BaseModel
from peewee import AutoField, IntegerField


class DimDay(BaseModel):
    """tabela dim_day"""

    id_day = AutoField(primary_key=True)
    day = IntegerField(null=False)

    class Meta:
        table_name = "dim_day"


class DimHour(BaseModel):
    """tabela dim_hour"""

    id_hour = AutoField(primary_key=True)
    hour = IntegerField(null=False)

    class Meta:
        table_name = "dim_hour"


class DimMinute(BaseModel):
    """tabela dim_minute"""

    id_minute = AutoField(primary_key=True)
    minute = IntegerField(null=False)

    class Meta:
        table_name = "dim_minute"


class DimMonth(BaseModel):
    """tabela dim_month"""

    id_month = AutoField(primary_key=True)
    month = IntegerField(null=False)

    class Meta:
        table_name = "dim_month"


class DimYear(BaseModel):
    """tabela dim_year"""

    id_year = AutoField(primary_key=True)
    year = IntegerField(null=False)

    class Meta:
        table_name = "dim_year"
