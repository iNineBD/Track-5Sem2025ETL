# db/base.py
from sqlalchemy.orm import declarative_base
from sqlalchemy.schema import MetaData

metadata = MetaData(schema="dw_track")
Base = declarative_base(metadata=metadata)
